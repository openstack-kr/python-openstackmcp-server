from unittest.mock import Mock, call
from openstack_mcp_server.tools.response.compute import Server
from openstack_mcp_server.tools.compute_tools import ComputeTools


class TestComputeTools:
    """Test cases for ComputeTools class."""

    def test_get_compute_servers_success(self, mock_get_openstack_conn):
        """Test getting compute servers successfully."""
        mock_conn = mock_get_openstack_conn

        # Create mock server objects
        mock_server1 = Mock()
        mock_server1.name = "web-server-01"
        mock_server1.id = "abc123-def456-ghi789"
        mock_server1.status = "ACTIVE"

        mock_server2 = Mock()
        mock_server2.name = "db-server-01"
        mock_server2.id = "xyz789-uvw456-rst123"
        mock_server2.status = "SHUTOFF"

        # Configure mock compute.servers()
        mock_conn.compute.servers.return_value = [mock_server1, mock_server2]

        # Test ComputeTools
        compute_tools = ComputeTools()
        result = compute_tools.get_compute_servers()

        # Verify results
        expected_output = [
            Server(name="web-server-01", id="abc123-def456-ghi789", status="ACTIVE"),
            Server(name="db-server-01", id="xyz789-uvw456-rst123", status="SHUTOFF"),
        ]
        assert result == expected_output

        # Verify mock calls
        mock_conn.compute.servers.assert_called_once()

    def test_get_compute_servers_empty_list(self, mock_get_openstack_conn):
        """Test getting compute servers when no servers exist."""
        mock_conn = mock_get_openstack_conn

        # Empty server list
        mock_conn.compute.servers.return_value = []

        compute_tools = ComputeTools()
        result = compute_tools.get_compute_servers()

        # Verify empty list
        assert result == []

        mock_conn.compute.servers.assert_called_once()

    def test_get_compute_servers_single_server(self, mock_get_openstack_conn):
        """Test getting compute servers with a single server."""
        mock_conn = mock_get_openstack_conn

        # Single server
        mock_server = Mock()
        mock_server.name = "test-server"
        mock_server.id = "single-123"
        mock_server.status = "BUILDING"

        mock_conn.compute.servers.return_value = [mock_server]

        compute_tools = ComputeTools()
        result = compute_tools.get_compute_servers()

        expected_output = [Server(name="test-server", id="single-123", status="BUILDING")]
        assert result == expected_output

        mock_conn.compute.servers.assert_called_once()

    def test_get_compute_servers_multiple_statuses(self, mock_get_openstack_conn):
        """Test servers with various statuses."""
        mock_conn = mock_get_openstack_conn

        # Servers with different statuses
        servers_data = [
            ("server-active", "id-1", "ACTIVE"),
            ("server-shutoff", "id-2", "SHUTOFF"),
            ("server-error", "id-3", "ERROR"),
            ("server-building", "id-4", "BUILDING"),
            ("server-paused", "id-5", "PAUSED"),
        ]

        mock_servers = []
        for name, server_id, status in servers_data:
            mock_server = Mock()
            mock_server.name = name
            mock_server.id = server_id
            mock_server.status = status
            mock_servers.append(mock_server)

        mock_conn.compute.servers.return_value = mock_servers

        compute_tools = ComputeTools()
        result = compute_tools.get_compute_servers()

        # Verify each server is included in the result
        for name, server_id, status in servers_data:
            assert any(
                server.name == name and server.id == server_id and server.status == status
                for server in result
            )

        mock_conn.compute.servers.assert_called_once()

    def test_get_compute_servers_with_special_characters(self, mock_get_openstack_conn):
        """Test servers with special characters in names."""
        mock_conn = mock_get_openstack_conn

        # Server names with special characters
        mock_server1 = Mock()
        mock_server1.name = "web-server_test-01"
        mock_server1.id = "id-with-dashes"
        mock_server1.status = "ACTIVE"

        mock_server2 = Mock()
        mock_server2.name = "db.server.prod"
        mock_server2.id = "id.with.dots"
        mock_server2.status = "SHUTOFF"

        mock_conn.compute.servers.return_value = [mock_server1, mock_server2]

        compute_tools = ComputeTools()
        result = compute_tools.get_compute_servers()

        assert Server(name="web-server_test-01", id="id-with-dashes", status="ACTIVE") in result
        assert Server(name="db.server.prod", id="id.with.dots", status="SHUTOFF") in result


        mock_conn.compute.servers.assert_called_once()

    def test_register_tools(self):
        """Test that tools are properly registered with FastMCP."""
        # Create FastMCP mock
        mock_mcp = Mock()
        mock_tool_decorator = Mock()
        mock_mcp.tool.return_value = mock_tool_decorator

        compute_tools = ComputeTools()
        compute_tools.register_tools(mock_mcp)
        
        mock_tool_decorator.assert_has_calls([
            call(compute_tools.get_compute_servers),
            call(compute_tools.get_compute_server)
        ])
        assert mock_tool_decorator.call_count == 2

    def test_compute_tools_instantiation(self):
        """Test ComputeTools can be instantiated."""
        compute_tools = ComputeTools()
        assert compute_tools is not None
        assert hasattr(compute_tools, 'register_tools')
        assert hasattr(compute_tools, 'get_compute_servers')
        assert callable(compute_tools.register_tools)
        assert callable(compute_tools.get_compute_servers)

    def test_get_compute_servers_docstring(self):
        """Test that get_compute_servers has proper docstring."""
        compute_tools = ComputeTools()
        docstring = compute_tools.get_compute_servers.__doc__

        assert docstring is not None
        assert "Get the list of Compute servers" in docstring
        assert "return" in docstring.lower() or "Return" in docstring