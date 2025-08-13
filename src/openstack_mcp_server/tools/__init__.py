from fastmcp import FastMCP


def register_tool(mcp: FastMCP):
    """
    Register Openstack MCP tools.
    """

    from .block_storage_tools import BlockStorageTools
    from .compute_tools import ComputeTools
    from .identity_tools import IdentityTools
    from .image_tools import ImageTools
    from .network_tools import NetworkTools

    ComputeTools().register_tools(mcp)
    ImageTools().register_tools(mcp)
    IdentityTools().register_tools(mcp)
    NetworkTools().register_tools(mcp)
    BlockStorageTools().register_tools(mcp)
