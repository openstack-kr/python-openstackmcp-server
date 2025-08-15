import atexit

import openstack

from openstack import connection

from openstack_mcp_server import config


class OpenStackConnectionManager:
    """OpenStack Connection Manager"""

    _connection: connection.Connection | None = None

    @classmethod
    def get_connection(cls) -> connection.Connection:
        """OpenStack Connection"""
        if cls._connection is None:
            openstack.enable_logging(debug=config.MCP_DEBUG_MODE)
            cls._connection = openstack.connect(cloud=config.MCP_CLOUD_NAME)
            atexit.register(cls._cleanup)
        return cls._connection

    @classmethod
    def _cleanup(cls) -> None:
        """Cleanup method called at program exit"""
        if cls._connection is not None:
            cls._connection.close()
            cls._connection = None


_openstack_connection_manager = OpenStackConnectionManager()


def get_openstack_conn():
    """Get OpenStack Connection"""
    return _openstack_connection_manager.get_connection()
