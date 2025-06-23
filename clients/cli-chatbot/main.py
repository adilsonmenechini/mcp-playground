import asyncio
import json
import logging
import os
import shutil
from contextlib import AsyncExitStack
from typing import Any

import ollama
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Configuration:
    def __init__(self) -> None:
        self.load_env()

    @staticmethod
    def load_env() -> None:
        load_dotenv()

    @staticmethod
    def load_config(file_path: str) -> dict[str, Any]:
        with open(file_path, "r") as f:
            return json.load(f)


def check_model_available(model: str = "mistral:instruct") -> bool:
    try:
        models = ollama.list()["models"]
        return any(m["name"].startswith(model) for m in models)
    except Exception as e:
        logging.error(f"Erro ao checar modelos disponíveis no Ollama: {e}")
        return False


class Server:
    def __init__(self, name: str, config: dict[str, Any]) -> None:
        self.name: str = name
        self.config: dict[str, Any] = config
        self.stdio_context: Any | None = None
        self.session: ClientSession | None = None
        self._cleanup_lock: asyncio.Lock = asyncio.Lock()
        self.exit_stack: AsyncExitStack = AsyncExitStack()

    async def initialize(self) -> None:
        command = shutil.which("npx") if self.config["command"] == "npx" else self.config["command"]
        if command is None:
            raise ValueError("The command must be a valid string and cannot be None.")

        server_params = StdioServerParameters(
            command=command,
            args=self.config["args"],
            env={**os.environ, **self.config["env"]} if self.config.get("env") else None,
        )
        try:
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            self.session = session
        except Exception as e:
            logging.error(f"Error initializing server {self.name}: {e}")
            await self.cleanup()
            raise

    async def list_tools(self) -> list[Any]:
        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")

        tools_response = await self.session.list_tools()
        tools = []

        for item in tools_response:
            if isinstance(item, tuple) and item[0] == "tools":
                tools.extend(
                    Tool(tool.name, tool.description, tool.inputSchema, getattr(tool, 'title', None))
                    for tool in item[1]
                )

        return tools

    async def execute_tool(self, tool_name: str, arguments: dict[str, Any], retries: int = 2, delay: float = 1.0) -> Any:
        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")

        attempt = 0
        while attempt < retries:
            try:
                logging.info(f"Executing {tool_name}...")
                result = await self.session.call_tool(tool_name, arguments)
                return result
            except Exception as e:
                attempt += 1
                logging.warning(f"Error executing tool: {e}. Attempt {attempt} of {retries}.")
                if attempt < retries:
                    logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logging.error("Max retries reached. Failing.")
                    raise

    async def cleanup(self) -> None:
        async with self._cleanup_lock:
            try:
                await self.exit_stack.aclose()
                self.session = None
                self.stdio_context = None
            except Exception as e:
                logging.error(f"Error during cleanup of server {self.name}: {e}")


class Tool:
    def __init__(self, name: str, description: str, input_schema: dict[str, Any], title: str | None = None) -> None:
        self.name: str = name
        self.title: str | None = title
        self.description: str = description
        self.input_schema: dict[str, Any] = input_schema

    def format_for_llm(self) -> str:
        args_desc = []
        if "properties" in self.input_schema:
            for param_name, param_info in self.input_schema["properties"].items():
                arg_desc = f"- {param_name}: {param_info.get('description', 'No description')}"
                if param_name in self.input_schema.get("required", []):
                    arg_desc += " (required)"
                args_desc.append(arg_desc)

        output = f"Tool: {self.name}\n"
        if self.title:
            output += f"User-readable title: {self.title}\n"
        output += f"Description: {self.description}\nArguments:\n{chr(10).join(args_desc)}\n"
        return output


class LLMClient:
    def __init__(self, models: list[str] = ["llama3.2","deepseek-r1:8b"]):
        self.models = models

    def get_response(self, messages: list[dict[str, str]]) -> str:
        for model in self.models:
            try:
                response = ollama.chat(
                    model=model,
                    messages=messages,
                    options={
                        "temperature": 0.7,
                        "top_p": 1,
                        "num_predict": 4096, 
                        "stream": True,
                        },
                )
                return response["message"]["content"]
            except Exception as e:
                logging.warning(f"Erro com modelo {model}: {e}")
        return "❌ Nenhum modelo Ollama respondeu corretamente. Verifique a instância local."


class ChatSession:
    def __init__(self, servers: list[Server], llm_client: LLMClient) -> None:
        self.servers: list[Server] = servers
        self.llm_client: LLMClient = llm_client

    async def cleanup_servers(self) -> None:
        for server in reversed(self.servers):
            try:
                await server.cleanup()
            except Exception as e:
                logging.warning(f"Warning during final cleanup: {e}")

    async def process_llm_response(self, llm_response: str) -> str:
        try:
            tool_call = json.loads(llm_response)
            if "tool" in tool_call and "arguments" in tool_call:
                logging.info(f"Executing tool: {tool_call['tool']}")
                logging.info(f"With arguments: {tool_call['arguments']}")

                for server in self.servers:
                    tools = await server.list_tools()
                    if any(tool.name == tool_call["tool"] for tool in tools):
                        try:
                            result = await server.execute_tool(tool_call["tool"], tool_call["arguments"])

                            if isinstance(result, dict) and "progress" in result:
                                progress = result["progress"]
                                total = result["total"]
                                percentage = (progress / total) * 100
                                logging.info(f"Progress: {progress}/{total} ({percentage:.1f}%)")

                            return f"Tool execution result: {result}"
                        except Exception as e:
                            error_msg = f"Error executing tool: {str(e)}"
                            logging.error(error_msg)
                            return error_msg

                return f"No server found with tool: {tool_call['tool']}"
            return llm_response
        except json.JSONDecodeError:
            return llm_response

    async def start(self) -> None:
        try:
            for server in self.servers:
                try:
                    await server.initialize()
                except Exception as e:
                    logging.error(f"Failed to initialize server: {e}")
                    await self.cleanup_servers()
                    return

            all_tools = []
            for server in self.servers:
                tools = await server.list_tools()
                all_tools.extend(tools)

            tools_description = "\n".join([tool.format_for_llm() for tool in all_tools])

            system_message = (
                "Você é um assistente especializado integrado ao Model Context Protocol (MCP), "
                "com acesso a diversas ferramentas e recursos para ajudar em tarefas específicas.\n\n"
                "📚 FERRAMENTAS DISPONÍVEIS:\n"
                f"{tools_description}\n\n"
                "🔧 INSTRUÇÕES DE USO:\n\n"
                "1. Para usar uma ferramenta, responda APENAS com um JSON no formato:\n"
                "{\n"
                '  "tool": "nome_da_ferramenta",\n'
                '  "arguments": {\n'
                '    "param1": "valor1",\n'
                '    "param2": "valor2"\n'
                "  }\n"
                "}\n\n"
                "2. O JSON deve conter:\n"
                "   - tool: nome exato da ferramenta desejada\n"
                "   - arguments: parâmetros requeridos pela ferramenta\n\n"
                "3. Se a ferramenta retornar resultados, eles serão processados e incorporados ao contexto\n\n"
                "4. Para respostas que não necessitam de ferramentas, use texto natural\n\n"
                "⚠️ IMPORTANTE:\n"
                "- Verifique os parâmetros obrigatórios de cada ferramenta\n"
                "- Use apenas ferramentas listadas acima\n"
                "- Mantenha o formato JSON exato quando usar ferramentas\n"
                "- Respostas em texto natural quando não usar ferramentas"
            )

            messages = [{"role": "system", "content": system_message}]

            while True:
                try:
                    user_input = input("You: ").strip()
                    if user_input.lower() in ["quit", "exit"]:
                        logging.info("\nExiting...")
                        break

                    messages.append({"role": "user", "content": user_input})
                    print("\n🧠 Pensando...")
                    llm_response = self.llm_client.get_response(messages)
                    logging.info("\n🤖 Assistente: %s", llm_response)

                    result = await self.process_llm_response(llm_response)

                    if result != llm_response:
                        messages.append({"role": "assistant", "content": llm_response})
                        messages.append({"role": "system", "content": result})
                        final_response = self.llm_client.get_response(messages)
                        logging.info("\n✨ Resposta final: %s", final_response)
                        messages.append({"role": "assistant", "content": final_response})
                    else:
                        messages.append({"role": "assistant", "content": llm_response})

                except KeyboardInterrupt:
                    logging.info("\nExiting...")
                    break
        finally:
            await self.cleanup_servers()


async def main() -> None:
    config = Configuration()
    server_config = config.load_config("servers_config.json")
    servers = [Server(name, srv_config) for name, srv_config in server_config["mcpServers"].items()]

    llm_client = LLMClient()
    chat_session = ChatSession(servers, llm_client)
    await chat_session.start()


if __name__ == "__main__":
    asyncio.run(main())