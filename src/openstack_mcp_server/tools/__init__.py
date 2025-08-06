from fastmcp import FastMCP


def register_tool(mcp: FastMCP):
    """
    Register Openstack MCP tools.
    """
    from .compute_tools import ComputeTools
    from .image_tools import ImageTools
    from .keystone_tools import KeystoneTools

    ComputeTools().register_tools(mcp)
    ImageTools().register_tools(mcp)
    KeystoneTools().register_tools(mcp)
