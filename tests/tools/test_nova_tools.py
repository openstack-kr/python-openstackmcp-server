from openstack_mcp_server.tools.nova_tools import NovaTools


class TestNovaTools:
    def test_register_tools(self, mock_fastmcp):
        """Test that tools are properly registered with FastMCP."""
        # Arrange
        nova_tools = NovaTools()

        # Act
        nova_tools.register_tools(mock_fastmcp)

        # Assert
        mock_fastmcp.tool.assert_called_once()
        mock_fastmcp.tool().assert_called_once_with(
            nova_tools.get_nova_servers
        )

    def test_get_nova_servers(
        self, mock_openstack_logging, mock_openstack_connect, sample_servers
    ):
        """Test getting Nova servers list."""
        # Arrange
        mock_conn = mock_openstack_connect.return_value
        mock_conn.list_servers.return_value = sample_servers
        nova_tools = NovaTools()

        # Act
        result = nova_tools.get_nova_servers()

        # Assert
        expected = (
            "server1 (id1) - Status: ACTIVE\nserver2 (id2) - Status: STOPPED"
        )
        assert result == expected
        mock_openstack_logging.assert_called_once_with(debug=True)
        mock_openstack_connect.assert_called_once_with(cloud="openstack")

    def test_get_nova_servers_empty_list(
        self, mock_openstack_logging, mock_openstack_connect
    ):
        """Test getting Nova servers when no servers exist."""
        # Arrange
        mock_conn = mock_openstack_connect.return_value
        mock_conn.list_servers.return_value = []
        nova_tools = NovaTools()

        # Act
        result = nova_tools.get_nova_servers()

        # Assert
        assert result == ""

    def test_get_nova_servers_single_server(
        self, mock_openstack_connection, mock_server
    ):
        """Test getting single Nova server."""
        # Arrange
        mock_conn, mock_connect = mock_openstack_connection
        test_server = mock_server("web-server", "web-001", "BUILDING")
        mock_conn.list_servers.return_value = [test_server]
        nova_tools = NovaTools()

        # Act
        result = nova_tools.get_nova_servers()

        # Assert
        expected = "web-server (web-001) - Status: BUILDING"
        assert result == expected
