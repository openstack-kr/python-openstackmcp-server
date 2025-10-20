from openstack_mcp_server.tools.connection import ConnectionManager


_connection_manager = ConnectionManager()


def get_openstack_conn():
    return _connection_manager.get_connection()


def set_openstack_cloud_name(cloud_name: str) -> None:
    _connection_manager.set_cloud_name(cloud_name)


def get_openstack_cloud_name() -> str:
    return _connection_manager.get_cloud_name()
