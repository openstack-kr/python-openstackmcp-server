from unittest.mock import Mock, call

import pytest

from openstack.exceptions import ConflictException, NotFoundException

from openstack_mcp_server.tools.compute_tools import ComputeTools
from openstack_mcp_server.tools.response.compute import Flavor, Server


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
                flavor=Server.Flavor(id=None, name="m1.tiny"),
                image=Server.Image(id="de527f30-d078-41f4-8f18-a23bf2d39366"),
                addresses={
                    "private": [
                        Server.IPAddress(
                            addr="192.168.1.10",
                            version=4,
                            type="fixed",
                        ),
                    ],
                },
                key_name="my-key",
                security_groups=[Server.SecurityGroup(name="default")],
            ),
            Server(
                id="ffd071fe-1334-45f6-8894-5b0bcac262a6",
                name="db-server-01",
                status="SHUTOFF",
                flavor=Server.Flavor(id=None, name="m1.small"),
                image=Server.Image(id="3d897e0e-4117-46bb-ae77-e734bb16a1ca"),
                addresses={
                    "net1": [
                        Server.IPAddress(
                            addr="192.168.1.11",
                            version=4,
                            type="fixed",
                        ),
                    ],
                },
                key_name=None,
                security_groups=[
                    Server.SecurityGroup(name="default"),
                    Server.SecurityGroup(name="group1"),
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
                call(compute_tools.get_flavors),
                call(compute_tools.action_server),
                call(compute_tools.update_server),
                call(compute_tools.delete_server),
                call(compute_tools.attach_volume),
                call(compute_tools.detach_volume),
            ],
        )
        assert mock_tool_decorator.call_count == 9

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

    def test_get_flavors_success(self, mock_get_openstack_conn):
        """Test getting flavors successfully."""
        mock_conn = mock_get_openstack_conn

        # Create mock flavor objects
        mock_flavor1 = {
            "id": "1",
            "name": "m1.tiny",
            "vcpus": 1,
            "ram": 512,
            "disk": 1,
            "swap": 0,
            "os-flavor-access:is_public": True,
        }

        mock_flavor2 = {
            "id": "2",
            "name": "m1.small",
            "vcpus": 2,
            "ram": 2048,
            "disk": 20,
            "swap": 0,
            "os-flavor-access:is_public": True,
        }

        mock_conn.compute.flavors.return_value = [mock_flavor1, mock_flavor2]

        compute_tools = ComputeTools()
        result = compute_tools.get_flavors()

        expected_output = [
            Flavor(
                id="1",
                name="m1.tiny",
                vcpus=1,
                ram=512,
                disk=1,
                swap=0,
                is_public=True,
            ),
            Flavor(
                id="2",
                name="m1.small",
                vcpus=2,
                ram=2048,
                disk=20,
                swap=0,
                is_public=True,
            ),
        ]
        assert result == expected_output
        mock_conn.compute.flavors.assert_called_once()

    def test_get_flavors_empty_list(self, mock_get_openstack_conn):
        """Test getting flavors when no flavors exist."""
        mock_conn = mock_get_openstack_conn
        mock_conn.compute.flavors.return_value = []

        compute_tools = ComputeTools()
        result = compute_tools.get_flavors()

        assert result == []
        mock_conn.compute.flavors.assert_called_once()

    @pytest.mark.parametrize(
        "action",
        [
            "pause",
            "unpause",
            "suspend",
            "resume",
            "lock",
            "unlock",
            "rescue",
            "unrescue",
            "start",
            "stop",
            "shelve",
            "shelve_offload",
            "unshelve",
        ],
    )
    def test_action_server_success(self, mock_get_openstack_conn, action):
        """Test action_server with all supported actions."""
        mock_conn = mock_get_openstack_conn
        server_id = "test-server-id"

        # Mock the action method to avoid calling actual methods
        action_method = getattr(mock_conn.compute, f"{action}_server")
        action_method.return_value = None

        compute_tools = ComputeTools()
        result = compute_tools.action_server(server_id, action)

        # Verify the result is None (void function)
        assert result is None

        # Verify the correct method was called with server ID
        action_method.assert_called_once_with(server_id)

    def test_action_server_unsupported_action(self, mock_get_openstack_conn):
        """Test action_server with unsupported action raises ValueError."""
        server_id = "test-server-id"
        unsupported_action = "invalid_action"

        compute_tools = ComputeTools()

        with pytest.raises(
            ValueError,
            match=f"Unsupported action: {unsupported_action}",
        ):
            compute_tools.action_server(server_id, unsupported_action)

    def test_action_server_not_found(self, mock_get_openstack_conn):
        """Test action_server when server does not exist."""
        mock_conn = mock_get_openstack_conn
        server_id = "non-existent-server-id"
        action = "pause"

        # Mock the action method to raise NotFoundException
        mock_conn.compute.pause_server.side_effect = NotFoundException()

        compute_tools = ComputeTools()

        with pytest.raises(NotFoundException):
            compute_tools.action_server(server_id, action)

        mock_conn.compute.pause_server.assert_called_once_with(server_id)

    def test_action_server_conflict_exception(self, mock_get_openstack_conn):
        """Test action_server when action cannot be performed due to Conflict Exception."""
        mock_conn = mock_get_openstack_conn
        server_id = "test-server-id"
        action = "start"

        # Mock the action method to raise ConflictException
        mock_conn.compute.start_server.side_effect = ConflictException()

        compute_tools = ComputeTools()

        with pytest.raises(ConflictException):
            compute_tools.action_server(server_id, action)

        mock_conn.compute.start_server.assert_called_once_with(server_id)

    def test_update_server_success(self, mock_get_openstack_conn):
        """Test updating a server successfully with all parameters."""
        mock_conn = mock_get_openstack_conn
        server_id = "test-server-id"

        mock_server = {
            "name": "updated-server",
            "id": server_id,
            "status": "ACTIVE",
            "hostname": "updated-hostname",
            "description": "Updated server description",
            "accessIPv4": "192.168.1.100",
            "accessIPv6": "2001:db8::1",
        }

        mock_conn.compute.update_server.return_value = mock_server

        compute_tools = ComputeTools()
        server_params = mock_server.copy()
        server_params.pop("status")
        result = compute_tools.update_server(**server_params)

        expected_output = Server(**mock_server)
        assert result == expected_output

        expected_params = {
            "accessIPv4": "192.168.1.100",
            "accessIPv6": "2001:db8::1",
            "name": "updated-server",
            "hostname": "updated-hostname",
            "description": "Updated server description",
        }
        mock_conn.compute.update_server.assert_called_once_with(
            server_id, **expected_params
        )

    @pytest.mark.parametrize(
        "params",
        [
            {"param_key": "name", "value": "new-name"},
            {"param_key": "hostname", "value": "new-hostname"},
            {"param_key": "description", "value": "New description"},
            {"param_key": "accessIPv4", "value": "192.168.1.100"},
            {"param_key": "accessIPv6", "value": "2001:db8::1"},
        ],
    )
    def test_update_server_optional_params(
        self, mock_get_openstack_conn, params
    ):
        """Test updating a server with optional parameters."""
        mock_conn = mock_get_openstack_conn
        server_id = "test-server-id"

        mock_server = {
            "id": server_id,
            "name": "original-name",
            "description": "Original description",
            "hostname": "original-hostname",
            "accessIPv4": "1.1.1.1",
            "accessIPv6": "::",
            "status": "ACTIVE",
            **{params["param_key"]: params["value"]},
        }

        mock_conn.compute.update_server.return_value = mock_server

        compute_tools = ComputeTools()
        result = compute_tools.update_server(
            id=server_id,
            **{params["param_key"]: params["value"]},
        )
        assert result == Server(**mock_server)

        expected_params = {params["param_key"]: params["value"]}
        mock_conn.compute.update_server.assert_called_once_with(
            server_id, **expected_params
        )

    def test_update_server_not_found(self, mock_get_openstack_conn):
        """Test updating a server that does not exist."""
        mock_conn = mock_get_openstack_conn
        server_id = "non-existent-server-id"

        # Mock the update_server method to raise NotFoundException
        mock_conn.compute.update_server.side_effect = NotFoundException()

        compute_tools = ComputeTools()

        with pytest.raises(NotFoundException):
            compute_tools.update_server(id=server_id)

        mock_conn.compute.update_server.assert_called_once_with(server_id)

    def test_delete_server_success(self, mock_get_openstack_conn):
        """Test deleting a server successfully."""
        mock_conn = mock_get_openstack_conn
        server_id = "test-server-id"

        mock_conn.compute.delete_server.return_value = None

        compute_tools = ComputeTools()
        result = compute_tools.delete_server(server_id)

        assert result is None
        mock_conn.compute.delete_server.assert_called_once_with(server_id)

    def test_delete_server_not_found(self, mock_get_openstack_conn):
        """Test deleting a server that does not exist."""
        mock_conn = mock_get_openstack_conn
        server_id = "non-existent-server-id"

        # Mock the delete_server method to raise NotFoundException
        mock_conn.compute.delete_server.side_effect = NotFoundException()

        compute_tools = ComputeTools()

        with pytest.raises(NotFoundException):
            compute_tools.delete_server(server_id)

        mock_conn.compute.delete_server.assert_called_once_with(server_id)

    def test_attach_volume_success(self, mock_get_openstack_conn):
        """Test attaching a volume to a server successfully."""
        mock_conn = mock_get_openstack_conn
        server_id = "test-server-id"
        volume_id = "test-volume-id"

        mock_conn.compute.create_volume_attachment.return_value = None

        compute_tools = ComputeTools()
        result = compute_tools.attach_volume(server_id, volume_id)

        assert result is None
        mock_conn.compute.create_volume_attachment.assert_called_once_with(
            server_id, volume_id=volume_id, device=None
        )

    def test_attach_volume_with_device(self, mock_get_openstack_conn):
        """Test attaching a volume to a server with a specific device."""
        mock_conn = mock_get_openstack_conn
        server_id = "test-server-id"
        volume_id = "test-volume-id"
        device = "/dev/vdb"

        mock_conn.compute.create_volume_attachment.return_value = None

        compute_tools = ComputeTools()
        result = compute_tools.attach_volume(server_id, volume_id, device)

        assert result is None
        mock_conn.compute.create_volume_attachment.assert_called_once_with(
            server_id, volume_id=volume_id, device=device
        )

    def test_attach_volume_exception(self, mock_get_openstack_conn):
        """Test attaching a volume when exception occurs."""
        mock_conn = mock_get_openstack_conn
        server_id = "test-server-id"
        volume_id = "test-volume-id"

        mock_conn.compute.create_volume_attachment.side_effect = (
            NotFoundException()
        )

        compute_tools = ComputeTools()

        with pytest.raises(NotFoundException):
            compute_tools.attach_volume(server_id, volume_id)

        mock_conn.compute.create_volume_attachment.assert_called_once_with(
            server_id, volume_id=volume_id, device=None
        )

    def test_detach_volume_success(self, mock_get_openstack_conn):
        """Test detaching a volume from a server successfully."""
        mock_conn = mock_get_openstack_conn
        server_id = "test-server-id"
        volume_id = "test-volume-id"

        mock_conn.compute.delete_volume_attachment.return_value = None

        compute_tools = ComputeTools()
        result = compute_tools.detach_volume(server_id, volume_id)

        assert result is None
        mock_conn.compute.delete_volume_attachment.assert_called_once_with(
            server_id, volume_id
        )

    def test_detach_volume_exception(self, mock_get_openstack_conn):
        """Test detaching a volume when exception occurs."""
        mock_conn = mock_get_openstack_conn
        server_id = "test-server-id"
        volume_id = "test-volume-id"

        mock_conn.compute.delete_volume_attachment.side_effect = (
            NotFoundException()
        )

        compute_tools = ComputeTools()

        with pytest.raises(NotFoundException):
            compute_tools.detach_volume(server_id, volume_id)

        mock_conn.compute.delete_volume_attachment.assert_called_once_with(
            server_id, volume_id
        )
