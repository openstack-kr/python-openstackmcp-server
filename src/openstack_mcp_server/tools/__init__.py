from fastmcp import FastMCP


def register_tool(mcp: FastMCP):
    """
    Register Openstack MCP tools.
    """
    from .compute_tools import ComputeTools
    from .glance_tools import GlanceTools
    from .keystone_tools import KeystoneTools

    ComputeTools().register_tools(mcp)
    GlanceTools().register_tools(mcp)
    KeystoneTools().register_tools(mcp)
