import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, \
                    StdioServerParameters, StdioConnectionParams

# IMPORTANT: Use the local adk_server.py in this package by default.
PATH_TO_YOUR_MCP_SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "adk_server.py")

if not os.path.exists(PATH_TO_YOUR_MCP_SERVER_SCRIPT):
    print(f"WARNING: PATH_TO_YOUR_MCP_SERVER_SCRIPT '{PATH_TO_YOUR_MCP_SERVER_SCRIPT}' does not exist. Please update the path if required.")

root_agent = LlmAgent(
    model=os.getenv("MODEL"),
    name='web_reader_mcp_client_agent',
    instruction="Use the 'load_web_page' tool to fetch content from a URL provided by the user.",
    ## Add the MCPToolset below:
    tools=[
    MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python3", # Command to run your MCP server script
            args=[PATH_TO_YOUR_MCP_SERVER_SCRIPT], # Argument is the path to the script
        ),
        timeout=15,
        ),
        tool_filter=['load_web_page'] # Optional: ensure only specific tools are loaded
    )
],
)