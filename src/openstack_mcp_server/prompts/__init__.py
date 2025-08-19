from fastmcp import FastMCP


def register_prompt(mcp: FastMCP):
    """
    Register OpenStack MCP prompts.
    """

    # Add image tools prompt
    mcp.add_prompt(
        "image_tools",
        "ImageTools Usage Guide - Only use parameters that the user explicitly requests",
        "prompts/image_tools_prompt.md",
    )
