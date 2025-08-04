from fastmcp import FastMCP


def register_tool(mcp: FastMCP):
    """
    Register Openstack MCP tools.
    """
    from .glance_tools import GlanceTools
    from .nova_tools import NovaTools
    from .cinder_tools import CinderTools

    NovaTools().register_tools(mcp)
    GlanceTools().register_tools(mcp)
    CinderTools().register_tools(mcp)
