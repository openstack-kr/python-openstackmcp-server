from collections.abc import Callable, Collection

from fastmcp.server import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware

from openstack_mcp_server.tools import register_tool


def serve(
    transport: str, 
    supported_transports: Collection[str],
    log_transport: Callable[[str], None],
    **kwargs) -> None:
    """Serve the MCP server with the specified transport."""
    if transport not in supported_transports:
        transport = "stdio"    
    log_transport(transport)
    
    mcp = FastMCP(
        "openstack_mcp_server",
    )
    register_tool(mcp)
    # resister_resources(mcp)
    # register_prompt(mcp)

    # Add middlewares
    mcp.add_middleware(ErrorHandlingMiddleware())
    mcp.add_middleware(LoggingMiddleware())
    mcp.run(transport=transport, **kwargs)