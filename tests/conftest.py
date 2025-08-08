import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_get_openstack_conn():
    """Mock get_openstack_conn function for compute_tools."""
    mock_conn = Mock()

    with patch(
        "openstack_mcp_server.tools.compute_tools.get_openstack_conn",
        return_value=mock_conn
    ) as mock_func:

        yield mock_conn


@pytest.fixture
def mock_get_openstack_conn_image():
    """Mock get_openstack_conn function for image_tools."""
    mock_conn = Mock()

    with patch(
        "openstack_mcp_server.tools.image_tools.get_openstack_conn",
        return_value=mock_conn
    ) as mock_func:

        yield mock_conn


@pytest.fixture
def mock_get_openstack_conn_identity():
    """Mock get_openstack_conn function for identity_tools."""
    mock_conn = Mock()

    with patch(
        "openstack_mcp_server.tools.identity_tools.get_openstack_conn",
        return_value=mock_conn
    ) as mock_func:

        yield mock_conn


@pytest.fixture
def mock_openstack_base():
    """Mock base module functions."""
    mock_conn = Mock()

    with patch(
        "openstack_mcp_server.tools.base.get_openstack_conn",
        return_value=mock_conn,
    ):
        yield mock_conn


@pytest.fixture
def mock_openstack_connect_neutron():
    """Mock get_openstack_conn function for neutron_tools."""
    mock_conn = Mock()

    with patch(
        "openstack_mcp_server.tools.neutron_tools.get_openstack_conn",
        return_value=mock_conn,
    ):
        yield mock_conn
