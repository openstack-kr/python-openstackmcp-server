import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_get_openstack_conn():
    """Mock get_openstack_conn function for nova_tools."""
    mock_conn = Mock()

    with patch(
        "openstack_mcp_server.tools.nova_tools.get_openstack_conn",
        return_value=mock_conn
    ):
        yield mock_conn


@pytest.fixture
def mock_get_openstack_conn_glance():
    """Mock get_openstack_conn function for glance_tools."""
    mock_conn = Mock()

    with patch(
        "openstack_mcp_server.tools.glance_tools.get_openstack_conn",
        return_value=mock_conn
    ):
        yield mock_conn

@pytest.fixture
def mock_get_openstack_conn_keystone():
    """Mock get_openstack_conn function for keystone_tools."""
    mock_conn = Mock()
    
    with patch(
        "openstack_mcp_server.tools.keystone_tools.get_openstack_conn",
        return_value=mock_conn
    ):
        yield mock_conn

@pytest.fixture
def mock_openstack_base():
    """Mock base module functions."""
    mock_conn = Mock()

    with patch(
        "openstack_mcp_server.tools.base.get_openstack_conn",
        return_value=mock_conn
    ):
        yield mock_conn