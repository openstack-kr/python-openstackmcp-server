from mcp.server.fastmcp import FastMCP

def register_tool(mcp : FastMCP):
    """
    Register Openstack MCP tools.
    """
    from .nova_tools import NovaTools

    NovaTools().register_tools(mcp)