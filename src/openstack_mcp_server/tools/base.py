import openstack
from openstack import connection
from openstack_mcp_server import config


class OpenStackConnectionManager:
    """OpenStack Connection Manager"""

    _connection: connection.Connection | None = None

    # TODO: Try/Catch disconnection by token expired case
    @classmethod
    def get_connection(cls) -> connection.Connection:
        """OpenStack Connection)"""
        if cls._connection is None:
            openstack.enable_logging(debug=config.MCP_DEBUG_MODE)
            cls._connection = openstack.connect(cloud=config.MCP_CLOUD_NAME)
        return cls._connection


    # TODO: Close connection


def get_openstack_conn():
    """Get OpenStack Connection"""
    return OpenStackConnectionManager.get_connection()
