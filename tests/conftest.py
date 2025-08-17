from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_get_openstack_conn():
    """Mock get_openstack_conn function for compute_tools."""
    mock_conn = Mock()

    with patch(
        "openstack_mcp_server.tools.compute_tools.get_openstack_conn",
        return_value=mock_conn,
    ):
        yield mock_conn


@pytest.fixture
def mock_get_openstack_conn_image():
    """Mock get_openstack_conn function for image_tools."""
    mock_conn = Mock()

    with patch(
        "openstack_mcp_server.tools.image_tools.get_openstack_conn",
        return_value=mock_conn,
    ):
        yield mock_conn


@pytest.fixture
def mock_get_openstack_conn_identity():
    """Mock get_openstack_conn function for identity_tools."""
    mock_conn = Mock()

    with patch(
        "openstack_mcp_server.tools.identity_tools.get_openstack_conn",
        return_value=mock_conn,
    ):
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
def mock_openstack_connect_network():
    """Mock get_openstack_conn function for network_tools."""
    mock_conn = Mock()

    with patch(
        "openstack_mcp_server.tools.network_tools.get_openstack_conn",
        return_value=mock_conn,
    ):
        yield mock_conn


@pytest.fixture
def mock_get_openstack_conn_block_storage():
    """Mock get_openstack_conn function for block_storage_tools."""
    mock_conn = Mock()

    with patch(
        "openstack_mcp_server.tools.block_storage_tools.get_openstack_conn",
        return_value=mock_conn,
    ):
        yield mock_conn
