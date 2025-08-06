from fastmcp.server import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware

from openstack_mcp_server.tools import register_tool


def serve(transport: str, **kwargs):
    """Serve the MCP server with the specified transport."""
    mcp = FastMCP(
        "openstack_mcp_server",
    )

    register_tool(mcp)
    # resister_resources(mcp)
    # register_prompt(mcp)

    # Add middlewares
    mcp.add_middleware(ErrorHandlingMiddleware())
    mcp.add_middleware(LoggingMiddleware())

    if transport == "stdio":
        mcp.run(transport="stdio", **kwargs)
    elif transport == "streamable-http":
        mcp.run(transport="streamable-http", **kwargs)
    elif transport == "sse":
        mcp.run(transport="sse", **kwargs)
    else:
        raise ValueError(f"Unsupported transport: {transport}")
