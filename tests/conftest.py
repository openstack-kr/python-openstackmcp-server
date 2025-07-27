import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_openstack_logging():
    """Mock openstack.enable_logging function."""
    with patch('openstack_mcp_server.tools.nova_tools.openstack.enable_logging') as mock:
        yield mock


@pytest.fixture
def mock_openstack_connect():
    """Mock openstack.connect function."""
    with patch('openstack_mcp_server.tools.nova_tools.openstack.connect') as mock:
        yield mock


@pytest.fixture
def mock_openstack_connection():
    """Mock openstack connection object."""
    mock_conn = Mock()
    with patch('openstack_mcp_server.tools.nova_tools.openstack.connect', return_value=mock_conn) as mock_connect:
        yield mock_conn, mock_connect


@pytest.fixture
def mock_server():
    """Create a mock server object."""
    def _create_server(name="test-server", server_id="test-id", status="ACTIVE"):
        mock = Mock()
        mock.name = name
        mock.id = server_id
        mock.status = status
        return mock
    return _create_server


@pytest.fixture
def sample_servers(mock_server):
    """Create sample server list."""
    return [
        mock_server("server1", "id1", "ACTIVE"),
        mock_server("server2", "id2", "STOPPED")
    ]


@pytest.fixture
def mock_fastmcp():
    """Mock FastMCP instance."""
    return Mock()