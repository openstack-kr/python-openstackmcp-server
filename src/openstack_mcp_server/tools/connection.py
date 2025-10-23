import openstack

from fastmcp import FastMCP
from openstack import connection
from openstack.config.loader import OpenStackConfig

from openstack_mcp_server import config


class ConnectionManager:
    _cloud_name = config.MCP_CLOUD_NAME

    def register_tools(self, mcp: FastMCP):
        mcp.tool(self.get_cloud_config)
        mcp.tool(self.get_cloud_names)
        mcp.tool(self.get_cloud_name)
        mcp.tool(self.set_cloud_name)

    def get_connection(self) -> connection.Connection:
        return openstack.connect(cloud=self._cloud_name)

    def get_cloud_names(self) -> list[str]:
        """List available cloud configurations.

        :return: Names of OpenStack clouds from user's config file.
        """
        config = OpenStackConfig()
        return list(config.get_cloud_names())

    def get_cloud_config(self) -> dict:
        """Provide cloud configuration with secrets masked of current user's config file.

        :return: Cloud configuration dictionary with credentials masked.
        """
        config = OpenStackConfig()
        return ConnectionManager._mask_credential(
            config.cloud_config, ["password"]
        )

    @staticmethod
    def _mask_credential(
        config_dict: dict, credential_keys: list[str]
    ) -> dict:
        masked = {}
        for k, v in config_dict.items():
            if k in credential_keys:
                masked[k] = "****"
            elif isinstance(v, dict):
                masked[k] = ConnectionManager._mask_credential(
                    v, credential_keys
                )
            else:
                masked[k] = v
        return masked

    @classmethod
    def get_cloud_name(cls) -> str:
        """Return the currently selected cloud name.

        :return: current OpenStack cloud name.
        """
        return cls._cloud_name

    @classmethod
    def set_cloud_name(cls, cloud_name: str) -> None:
        """Set cloud name to use for later connections. Must set name from currently valid cloud config file.

        :param cloud_name: Name of the OpenStack cloud profile to activate.
        """
        cls._cloud_name = cloud_name
