from unittest.mock import MagicMock

from fastmcp import FastMCP

from openstack_mcp_server.prompts import register_prompt


class TestPrompts:
    """Test cases for MCP prompts."""

    def test_get_servers_by_security_group_prompt_registered(self):
        """Test that the prompt is registered with the MCP instance."""
        mcp = MagicMock()
        register_prompt(mcp)
        mcp.prompt.assert_called()

    def test_get_servers_by_security_group_prompt_content(self):
        """Test that the prompt returns expected content."""
        mcp = FastMCP("test")
        register_prompt(mcp)

        prompts = mcp._prompt_manager._prompts
        assert "get_servers_by_security_group" in prompts

        prompt_obj = prompts["get_servers_by_security_group"]
        assert prompt_obj.fn is not None

        result = prompt_obj.fn(security_group_name="my-sg")
        assert "my-sg" in result
        assert "get_servers" in result
        assert "security_groups" in result
