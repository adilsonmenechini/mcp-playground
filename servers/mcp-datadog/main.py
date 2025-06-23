import logging
import sys
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s', stream=sys.stderr) # Redirect logs to stderr

from mcp.server.fastmcp import FastMCP
from modules import mcp_tools  # Import tool functions
from pathlib import Path
from mcp.server.fastmcp.resources import FileResource

# Initialize MCP server
mcp = FastMCP("Datadog Integration Service", host="0.0.0.0", port=8000)

for tool in mcp_tools:
    mcp.tool()(tool)

@mcp.resource("docs://modules")
def view_documentation():
    """
    Returns a link to the documentation for this MCP service.
    """
    readme_path = Path("./docs/modules.md").resolve()
    if readme_path.exists():
        # Use a file:// URI scheme
        return FileResource(
            uri=f"file://{readme_path.as_posix()}",
            path=readme_path,
            name="modules.md",
            description="The project's modules.",
            mime_type="text/markdown"
        )


@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"

if __name__ == "__main__":
    mcp.run(transport="sse")
