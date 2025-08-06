from fastmcp import FastMCP


def register_tool(mcp: FastMCP):
    """
    Register Openstack MCP tools.
    """
    from .glance_tools import GlanceTools
    from .keystone_tools import KeystoneTools
    from .nova_tools import NovaTools

    NovaTools().register_tools(mcp)
    GlanceTools().register_tools(mcp)
    KeystoneTools().register_tools(mcp)
