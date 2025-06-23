# CLI Chatbot com MCP (Model Context Protocol)

## Descrição
Este é um chatbot CLI que implementa o protocolo MCP (Model Context Protocol) para interação com diferentes servidores de modelos e ferramentas. O projeto utiliza o Ollama como backend LLM e suporta integração com múltiplos servidores MCP através de conexões stdio.

## Requisitos
- Python >= 3.12
- uv (gerenciador de pacotes Python)
- Ollama instalado localmente
- Acesso ao servidor MCP-User-DB

## Instalação

1. Clone o repositório completo:
```bash
git clone <repository-url>
cd mcp-playground
```

2. Instale as dependências no diretório cli-chatbot:
```bash
cd clients/cli-chatbot
uv venv
source .venv/bin/activate  # No Linux/macOS
# ou
.venv\Scripts\activate     # No Windows
uv pip install .
```

3. Instale as dependências do servidor MCP-User-DB:
```bash
cd ../../servers/mcp-user-db
uv venv
source .venv/bin/activate
uv pip install .
```

## Configuração

### Estrutura do Projeto
O projeto é composto por dois componentes principais:
1. CLI Chatbot (este repositório)
2. Servidor MCP-User-DB (dependência necessária)

### Configuração do Servidor
O arquivo `servers_config.json` já está configurado para usar o servidor MCP-User-DB. Verifique se o caminho do servidor está correto no arquivo:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-user-db/",
        "run",
        "server.py"
      ]
    }
  }
}
```

### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto (opcional):
```env
# Configurações do ambiente (se necessário)
```

## Uso

1. Inicie primeiro o servidor MCP-User-DB em um terminal separado:
```bash
cd /path/to/mcp-playground/servers/mcp-user-db
source .venv/bin/activate
python server.py
```

2. Em outro terminal, inicie o chatbot:
```bash
cd /path/to/mcp-playground/clients/cli-chatbot
source .venv/bin/activate
python main.py
```

3. Interaja com o chatbot através do terminal:
- Digite suas mensagens e pressione Enter
- Use "quit" ou "exit" para sair
- Use Ctrl+C para interromper a execução

## Arquitetura

### Componentes Principais

1. **Configuration**
- Gerencia configurações e variáveis de ambiente
- Carrega configurações do arquivo servers_config.json

2. **Server**
- Gerencia conexões com servidores MCP
- Manipula inicialização e limpeza de recursos
- Implementa sistema de retry para execução de ferramentas

3. **Tool**
- Representa ferramentas disponíveis nos servidores
- Formata informações para uso com LLM

4. **LLMClient**
- Gerencia comunicação com o Ollama
- Configurado para usar o modelo mistral:instruct
- Implementa tratamento de erros e retries

5. **ChatSession**
- Orquestra interações entre usuário, LLM e ferramentas
- Gerencia o fluxo de mensagens e respostas
- Processa execução de ferramentas baseado nas respostas do LLM

## Desenvolvimento

### Dependências Principais
- httpx: Cliente HTTP assíncrono
- mcp[cli]: Implementação do protocolo MCP
- ollama: Interface com o Ollama LLM
- python-dotenv: Gerenciamento de variáveis de ambiente

## Solução de Problemas

### Erro de Servidor Web
Se você ver a mensagem:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```
Isso significa que você está executando o servidor MCP-User-DB diretamente no diretório do cli-chatbot. Certifique-se de:
1. Executar o servidor no diretório correto (/path/to/mcp-playground/servers/mcp-user-db)
2. Usar o ambiente virtual correto para cada componente

## Contribuição
Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nome-feature`)
3. Faça commit das mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nome-feature`)
5. Crie um Pull Request

## Licença
[Adicionar informações de licença]