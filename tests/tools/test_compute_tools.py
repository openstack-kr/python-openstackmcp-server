from unittest.mock import Mock, call

from openstack_mcp_server.tools.compute_tools import ComputeTools
from openstack_mcp_server.tools.response.compute import (
    Flavor,
    Image,
    Server,
    ServerIp,
    ServerSecurityGroup,
)


class TestComputeTools:
    """Test cases for ComputeTools class."""

    def test_get_servers_success(self, mock_get_openstack_conn):
        """Test getting servers successfully."""
        mock_conn = mock_get_openstack_conn

        # Create mock server objects
        mock_server1 = {
            "name": "web-server-01",
            "id": "434eb822-3fbd-44a1-a000-3b511ac9b516",
            "status": "ACTIVE",
            "flavor": {
                "original_name": "m1.tiny",
                "vcpus": 1,
                "ram": 512,
                "disk": 1,
            },
            "image": {"id": "de527f30-d078-41f4-8f18-a23bf2d39366"},
            "addresses": {
                "private": [
                    {
                        "addr": "192.168.1.10",
                        "version": 4,
                        "OS-EXT-IPS:type": "fixed",
                    },
                ],
            },
            "key_name": "my-key",
            "security_groups": [{"name": "default"}],
        }

        mock_server2 = {
            "name": "db-server-01",
            "id": "ffd071fe-1334-45f6-8894-5b0bcac262a6",
            "status": "SHUTOFF",
            "flavor": {
                "original_name": "m1.small",
                "vcpus": 2,
                "ram": 2048,
                "disk": 20,
            },
            "image": {"id": "3d897e0e-4117-46bb-ae77-e734bb16a1ca"},
            "addresses": {
                "net1": [
                    {
                        "addr": "192.168.1.11",
                        "version": 4,
                        "OS-EXT-IPS:type": "fixed",
                    },
                ],
            },
            "key_name": None,
            "security_groups": [{"name": "default"}, {"name": "group1"}],
        }

        # Configure mock compute.servers()
        mock_conn.compute.servers.return_value = [mock_server1, mock_server2]

        # Test ComputeTools
        compute_tools = ComputeTools()
        result = compute_tools.get_servers()

        # Verify results
        expected_output = [
            Server(
                id="434eb822-3fbd-44a1-a000-3b511ac9b516",
                name="web-server-01",
                status="ACTIVE",
                flavor=Flavor(id=None, name="m1.tiny"),
                image=Image(id="de527f30-d078-41f4-8f18-a23bf2d39366"),
                addresses={
                    "private": [
                        ServerIp(addr="192.168.1.10", version=4, type="fixed"),
                    ],
                },
                key_name="my-key",
                security_groups=[ServerSecurityGroup(name="default")],
            ),
            Server(
                id="ffd071fe-1334-45f6-8894-5b0bcac262a6",
                name="db-server-01",
                status="SHUTOFF",
                flavor=Flavor(id=None, name="m1.small"),
                image=Image(id="3d897e0e-4117-46bb-ae77-e734bb16a1ca"),
                addresses={
                    "net1": [
                        ServerIp(addr="192.168.1.11", version=4, type="fixed"),
                    ],
                },
                key_name=None,
                security_groups=[
                    ServerSecurityGroup(name="default"),
                    ServerSecurityGroup(name="group1"),
                ],
            ),
        ]
        assert result == expected_output

        # Verify mock calls
        mock_conn.compute.servers.assert_called_once()

    def test_get_servers_empty_list(self, mock_get_openstack_conn):
        """Test getting servers when no servers exist."""
        mock_conn = mock_get_openstack_conn

        # Empty server list
        mock_conn.compute.servers.return_value = []

        compute_tools = ComputeTools()
        result = compute_tools.get_servers()

        # Verify empty list
        assert result == []

        mock_conn.compute.servers.assert_called_once()

    def test_get_server_success(self, mock_get_openstack_conn):
        """Test getting a specific server successfully."""
        mock_conn = mock_get_openstack_conn

        # Create mock server object
        mock_server = {
            "name": "test-server",
            "id": "fe4b6b9b-090c-4dee-ab27-5155476e8e7d",
            "status": "ACTIVE",
        }

        mock_conn.compute.get_server.return_value = mock_server

        compute_tools = ComputeTools()
        result = compute_tools.get_server(
            "fe4b6b9b-090c-4dee-ab27-5155476e8e7d",
        )

        expected_output = Server(
            name="test-server",
            id="fe4b6b9b-090c-4dee-ab27-5155476e8e7d",
            status="ACTIVE",
        )
        assert result == expected_output
        mock_conn.compute.get_server.assert_called_once_with(
            "fe4b6b9b-090c-4dee-ab27-5155476e8e7d",
        )

    def test_create_server_success(self, mock_get_openstack_conn):
        """Test creating a server successfully."""
        mock_conn = mock_get_openstack_conn

        # Mock the create and get operations
        mock_create_response = Mock()
        mock_create_response.id = "5f4ce035-79a3-4feb-a011-9c256789f380"

        mock_server = {
            "name": "new-server",
            "id": mock_create_response.id,
            "status": "BUILDING",
        }

        mock_conn.compute.create_server.return_value = mock_create_response
        mock_conn.compute.get_server.return_value = mock_server

        compute_tools = ComputeTools()
        result = compute_tools.create_server(
            name="new-server",
            image="a6c3a174-b3d1-4019-8023-fef9518fbaff",
            flavor=1,
            network="49173e57-f96e-474b-b36b-2f3f432ef7aa",
        )

        expected_output = Server(
            name="new-server",
            id="5f4ce035-79a3-4feb-a011-9c256789f380",
            status="BUILDING",
        )
        assert result == expected_output

        expected_params = {
            "name": "new-server",
            "flavorRef": 1,
            "imageRef": "a6c3a174-b3d1-4019-8023-fef9518fbaff",
            "networks": [{"uuid": "49173e57-f96e-474b-b36b-2f3f432ef7aa"}],
        }
        mock_conn.compute.create_server.assert_called_once_with(
            **expected_params,
        )
        mock_conn.compute.get_server.assert_called_once_with(
            mock_create_response.id,
        )

    def test_create_server_with_optional_params(self, mock_get_openstack_conn):
        """Test creating a server with optional parameters."""
        mock_conn = mock_get_openstack_conn

        mock_create_response = Mock()
        mock_create_response.id = "b6bcd30f-f150-4751-998e-fd7349f50160"

        mock_server = {
            "name": "server-with-options",
            "id": mock_create_response.id,
            "status": "BUILDING",
        }

        mock_conn.compute.create_server.return_value = mock_create_response
        mock_conn.compute.get_server.return_value = mock_server

        compute_tools = ComputeTools()
        compute_tools.create_server(
            name="server-with-options",
            image="a6c3a174-b3d1-4019-8023-fef9518fbaff",
            flavor=2,
            network="49173e57-f96e-474b-b36b-2f3f432ef7aa",
            key_name="my-key",
            security_groups=["default", "web"],
            user_data="#!/bin/bash\necho 'Hello World'",
        )

        expected_params = {
            "name": "server-with-options",
            "flavorRef": 2,
            "imageRef": "a6c3a174-b3d1-4019-8023-fef9518fbaff",
            "networks": [{"uuid": "49173e57-f96e-474b-b36b-2f3f432ef7aa"}],
            "key_name": "my-key",
            "security_groups": ["default", "web"],
            "user_data": "#!/bin/bash\necho 'Hello World'",
        }
        mock_conn.compute.create_server.assert_called_once_with(
            **expected_params,
        )
        mock_conn.compute.get_server.assert_called_once_with(
            mock_create_response.id,
        )

    def test_register_tools(self):
        """Test that tools are properly registered with FastMCP."""
        # Create FastMCP mock
        mock_mcp = Mock()
        mock_tool_decorator = Mock()
        mock_mcp.tool.return_value = mock_tool_decorator

        compute_tools = ComputeTools()
        compute_tools.register_tools(mock_mcp)

        mock_tool_decorator.assert_has_calls(
            [
                call(compute_tools.get_servers),
                call(compute_tools.get_server),
                call(compute_tools.create_server),
            ],
        )
        assert mock_tool_decorator.call_count == 3

    def test_compute_tools_instantiation(self):
        """Test ComputeTools can be instantiated."""
        compute_tools = ComputeTools()
        assert compute_tools is not None
        assert hasattr(compute_tools, "register_tools")
        assert hasattr(compute_tools, "get_servers")
        assert callable(compute_tools.register_tools)
        assert callable(compute_tools.get_servers)

    def test_get_servers_docstring(self):
        """Test that get_servers has proper docstring."""
        compute_tools = ComputeTools()
        docstring = compute_tools.get_servers.__doc__

        assert docstring is not None
        assert "Get the list of Compute servers" in docstring
        assert "return" in docstring.lower() or "Return" in docstring
