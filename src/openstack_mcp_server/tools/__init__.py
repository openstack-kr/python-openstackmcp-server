from fastmcp import FastMCP


def register_tool(mcp: FastMCP):
    """
    Register Openstack MCP tools.
    """
    
    from .compute_tools import ComputeTools
    from .identity_tools import IdentityTools
    from .image_tools import ImageTools
    from .neutron_tools import NeutronTools

    ComputeTools().register_tools(mcp)
    ImageTools().register_tools(mcp)
    IdentityTools().register_tools(mcp)
    NeutronTools().register_tools(mcp)
