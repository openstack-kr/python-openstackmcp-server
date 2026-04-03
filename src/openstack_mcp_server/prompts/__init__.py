from fastmcp import FastMCP


def register_prompt(mcp: FastMCP):
    """
    Register Openstack MCP prompts.
    """

    @mcp.prompt()
    def get_servers_by_security_group(security_group_name: str) -> str:
        """
        Get servers associated with a specific security group.

        :param security_group_name: The name of the security group to filter servers by.
        """
        return (
            f"Find all compute servers that have the security group "
            f"'{security_group_name}' attached.\n\n"
            f"Steps:\n"
            f"1. Call get_servers to list all servers.\n"
            f"2. Check each server's security_groups field.\n"
            f"3. Return only the servers where security_groups contains "
            f"an entry with name '{security_group_name}'.\n"
            f"4. For each matching server, show the server name, ID, "
            f"status, and the full list of its security groups."
        )
