from unittest.mock import Mock

from openstack_mcp_server.tools.network_tools import NetworkTools
from openstack_mcp_server.tools.request.network import (
    ExternalGatewayInfo,
    Route,
)
from openstack_mcp_server.tools.response.network import (
    FloatingIP,
    Network,
    Port,
    Router,
    Subnet,
)


class TestNetworkTools:
    """Test cases for NetworkTools class."""

    def get_network_tools(self) -> NetworkTools:
        """Get an instance of NetworkTools."""
        return NetworkTools()

    def test_get_networks_success(
        self,
        mock_openstack_connect_network,
    ):
        """Test getting openstack networks successfully."""
        mock_conn = mock_openstack_connect_network

        mock_network1 = Mock()
        mock_network1.id = "net-123-abc-def"
        mock_network1.name = "private-network"
        mock_network1.status = "ACTIVE"
        mock_network1.description = "Private network for project"
        mock_network1.is_admin_state_up = True
        mock_network1.is_shared = False
        mock_network1.mtu = 1500
        mock_network1.provider_network_type = "vxlan"
        mock_network1.provider_physical_network = None
        mock_network1.provider_segmentation_id = 100
        mock_network1.project_id = "proj-456-ghi-jkl"

        mock_network2 = Mock()
        mock_network2.id = "net-789-mno-pqr"
        mock_network2.name = "public-network"
        mock_network2.status = "ACTIVE"
        mock_network2.description = "Public shared network"
        mock_network2.is_admin_state_up = True
        mock_network2.is_shared = True
        mock_network2.mtu = 1450
        mock_network2.provider_network_type = "flat"
        mock_network2.provider_physical_network = "physnet1"
        mock_network2.provider_segmentation_id = None
        mock_network2.project_id = "proj-admin-000"

        mock_conn.network.networks.return_value = [
            mock_network1,
            mock_network2,
        ]

        network_tools = self.get_network_tools()
        result = network_tools.get_networks()

        expected_network1 = Network(
            id="net-123-abc-def",
            name="private-network",
            status="ACTIVE",
            description="Private network for project",
            is_admin_state_up=True,
            is_shared=False,
            mtu=1500,
            provider_network_type="vxlan",
            provider_physical_network=None,
            provider_segmentation_id=100,
            project_id="proj-456-ghi-jkl",
        )

        expected_network2 = Network(
            id="net-789-mno-pqr",
            name="public-network",
            status="ACTIVE",
            description="Public shared network",
            is_admin_state_up=True,
            is_shared=True,
            mtu=1450,
            provider_network_type="flat",
            provider_physical_network="physnet1",
            provider_segmentation_id=None,
            project_id="proj-admin-000",
        )

        assert len(result) == 2
        assert result[0] == expected_network1
        assert result[1] == expected_network2

        mock_conn.network.networks.assert_called_once_with()

    def test_get_networks_empty_list(
        self,
        mock_openstack_connect_network,
    ):
        """Test getting openstack networks when no networks exist."""
        mock_conn = mock_openstack_connect_network

        mock_conn.network.networks.return_value = []

        network_tools = self.get_network_tools()
        result = network_tools.get_networks()

        assert result == []

        mock_conn.network.networks.assert_called_once_with()

    def test_get_networks_with_status_filter(
        self,
        mock_openstack_connect_network,
    ):
        """Test getting opestack networks with status filter."""
        mock_conn = mock_openstack_connect_network

        mock_network1 = Mock()
        mock_network1.id = "net-active"
        mock_network1.name = "active-network"
        mock_network1.status = "ACTIVE"
        mock_network1.description = None
        mock_network1.is_admin_state_up = True
        mock_network1.is_shared = False
        mock_network1.mtu = None
        mock_network1.provider_network_type = None
        mock_network1.provider_physical_network = None
        mock_network1.provider_segmentation_id = None
        mock_network1.project_id = None

        mock_network2 = Mock()
        mock_network2.id = "net-down"
        mock_network2.name = "down-network"
        mock_network2.status = "DOWN"
        mock_network2.description = None
        mock_network2.is_admin_state_up = False
        mock_network2.is_shared = False
        mock_network2.mtu = None
        mock_network2.provider_network_type = None
        mock_network2.provider_physical_network = None
        mock_network2.provider_segmentation_id = None
        mock_network2.project_id = None

        mock_conn.network.networks.return_value = [
            mock_network1,
        ]  # Only ACTIVE network
        network_tools = self.get_network_tools()
        result = network_tools.get_networks(status_filter="ACTIVE")

        assert len(result) == 1
        assert result[0].id == "net-active"
        assert result[0].status == "ACTIVE"

        mock_conn.network.networks.assert_called_once_with(
            status="ACTIVE",
        )

    def test_get_networks_shared_only(
        self,
        mock_openstack_connect_network,
    ):
        """Test getting only shared networks."""
        mock_conn = mock_openstack_connect_network

        mock_network1 = Mock()
        mock_network1.id = "net-private"
        mock_network1.name = "private-network"
        mock_network1.status = "ACTIVE"
        mock_network1.description = None
        mock_network1.is_admin_state_up = True
        mock_network1.is_shared = False
        mock_network1.mtu = None
        mock_network1.provider_network_type = None
        mock_network1.provider_physical_network = None
        mock_network1.provider_segmentation_id = None
        mock_network1.project_id = None

        mock_network2 = Mock()
        mock_network2.id = "net-shared"
        mock_network2.name = "shared-network"
        mock_network2.status = "ACTIVE"
        mock_network2.description = None
        mock_network2.is_admin_state_up = True
        mock_network2.is_shared = True
        mock_network2.mtu = None
        mock_network2.provider_network_type = None
        mock_network2.provider_physical_network = None
        mock_network2.provider_segmentation_id = None
        mock_network2.project_id = None

        mock_conn.network.networks.return_value = [
            mock_network2,
        ]  # Only shared network

        network_tools = self.get_network_tools()
        result = network_tools.get_networks(shared_only=True)

        assert len(result) == 1
        assert result[0].id == "net-shared"
        assert result[0].is_shared is True

        mock_conn.network.networks.assert_called_once_with(
            is_shared=True,
        )

    def test_get_networks_status_filter_case_insensitive(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        mock_network = Mock()
        mock_network.id = "net-active"
        mock_network.name = "active-network"
        mock_network.status = "ACTIVE"
        mock_network.description = None
        mock_network.is_admin_state_up = True
        mock_network.is_shared = False
        mock_network.mtu = None
        mock_network.provider_network_type = None
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = None
        mock_network.project_id = None

        mock_conn.network.networks.return_value = [mock_network]

        tools = self.get_network_tools()
        res = tools.get_networks(status_filter="active")

        assert len(res) == 1
        assert res[0].status == "ACTIVE"
        mock_conn.network.networks.assert_called_once_with(status="ACTIVE")

    def test_create_network_success(self, mock_openstack_connect_network):
        """Test creating a network successfully."""
        mock_conn = mock_openstack_connect_network

        mock_network = Mock()
        mock_network.id = "net-new-123"
        mock_network.name = "new-network"
        mock_network.status = "ACTIVE"
        mock_network.description = "A new network"
        mock_network.is_admin_state_up = True
        mock_network.is_shared = False
        mock_network.mtu = 1500
        mock_network.provider_network_type = "vxlan"
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = 200
        mock_network.project_id = "proj-123"

        mock_conn.network.create_network.return_value = mock_network

        network_tools = self.get_network_tools()
        result = network_tools.create_network(
            name="new-network",
            description="A new network",
            provider_network_type="vxlan",
            provider_segmentation_id=200,
        )

        expected_network = Network(
            id="net-new-123",
            name="new-network",
            status="ACTIVE",
            description="A new network",
            is_admin_state_up=True,
            is_shared=False,
            mtu=1500,
            provider_network_type="vxlan",
            provider_physical_network=None,
            provider_segmentation_id=200,
            project_id="proj-123",
        )

        assert result == expected_network

        expected_args = {
            "name": "new-network",
            "admin_state_up": True,
            "shared": False,
            "description": "A new network",
            "provider_network_type": "vxlan",
            "provider_segmentation_id": 200,
        }
        mock_conn.network.create_network.assert_called_once_with(
            **expected_args,
        )

    def test_create_network_minimal_args(self, mock_openstack_connect_network):
        """Test creating a network with minimal arguments."""
        mock_conn = mock_openstack_connect_network

        mock_network = Mock()
        mock_network.id = "net-minimal-123"
        mock_network.name = "minimal-network"
        mock_network.status = "ACTIVE"
        mock_network.description = None
        mock_network.is_admin_state_up = True
        mock_network.is_shared = False
        mock_network.mtu = None
        mock_network.provider_network_type = None
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = None
        mock_network.project_id = None

        mock_conn.network.create_network.return_value = mock_network

        network_tools = self.get_network_tools()
        result = network_tools.create_network(name="minimal-network")

        expected_network = Network(
            id="net-minimal-123",
            name="minimal-network",
            status="ACTIVE",
            description=None,
            is_admin_state_up=True,
            is_shared=False,
            mtu=None,
            provider_network_type=None,
            provider_physical_network=None,
            provider_segmentation_id=None,
            project_id=None,
        )

        assert result == expected_network

        expected_args = {
            "name": "minimal-network",
            "admin_state_up": True,
            "shared": False,
        }
        mock_conn.network.create_network.assert_called_once_with(
            **expected_args,
        )

    def test_get_network_detail_success(self, mock_openstack_connect_network):
        """Test getting network detail successfully."""
        mock_conn = mock_openstack_connect_network

        mock_network = Mock()
        mock_network.id = "net-detail-123"
        mock_network.name = "detail-network"
        mock_network.status = "ACTIVE"
        mock_network.description = "Network for detail testing"
        mock_network.is_admin_state_up = True
        mock_network.is_shared = True
        mock_network.mtu = 1500
        mock_network.provider_network_type = "vlan"
        mock_network.provider_physical_network = "physnet1"
        mock_network.provider_segmentation_id = 100
        mock_network.project_id = "proj-detail-123"

        mock_conn.network.get_network.return_value = mock_network

        network_tools = self.get_network_tools()
        result = network_tools.get_network_detail("net-detail-123")

        expected_network = Network(
            id="net-detail-123",
            name="detail-network",
            status="ACTIVE",
            description="Network for detail testing",
            is_admin_state_up=True,
            is_shared=True,
            mtu=1500,
            provider_network_type="vlan",
            provider_physical_network="physnet1",
            provider_segmentation_id=100,
            project_id="proj-detail-123",
        )

        assert result == expected_network

        mock_conn.network.get_network.assert_called_once_with("net-detail-123")

    def test_update_network_success(self, mock_openstack_connect_network):
        """Test updating a network successfully."""
        mock_conn = mock_openstack_connect_network

        mock_network = Mock()
        mock_network.id = "net-update-123"
        mock_network.name = "updated-network"
        mock_network.status = "ACTIVE"
        mock_network.description = "Updated description"
        mock_network.is_admin_state_up = False
        mock_network.is_shared = True
        mock_network.mtu = 1400
        mock_network.provider_network_type = "vxlan"
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = 300
        mock_network.project_id = "proj-update-123"

        mock_conn.network.update_network.return_value = mock_network

        network_tools = self.get_network_tools()
        result = network_tools.update_network(
            network_id="net-update-123",
            name="updated-network",
            description="Updated description",
            is_admin_state_up=False,
            is_shared=True,
        )

        expected_network = Network(
            id="net-update-123",
            name="updated-network",
            status="ACTIVE",
            description="Updated description",
            is_admin_state_up=False,
            is_shared=True,
            mtu=1400,
            provider_network_type="vxlan",
            provider_physical_network=None,
            provider_segmentation_id=300,
            project_id="proj-update-123",
        )

        assert result == expected_network

        expected_args = {
            "name": "updated-network",
            "description": "Updated description",
            "admin_state_up": False,
            "shared": True,
        }
        mock_conn.network.update_network.assert_called_once_with(
            "net-update-123",
            **expected_args,
        )

    def test_update_network_partial_update(
        self,
        mock_openstack_connect_network,
    ):
        """Test updating a network with only some parameters."""
        mock_conn = mock_openstack_connect_network

        mock_network = Mock()
        mock_network.id = "net-partial-123"
        mock_network.name = "new-name"
        mock_network.status = "ACTIVE"
        mock_network.description = "old description"
        mock_network.is_admin_state_up = True
        mock_network.is_shared = False
        mock_network.mtu = None
        mock_network.provider_network_type = None
        mock_network.provider_physical_network = None
        mock_network.provider_segmentation_id = None
        mock_network.project_id = None

        mock_conn.network.update_network.return_value = mock_network
        network_tools = self.get_network_tools()
        result = network_tools.update_network(
            network_id="net-partial-123",
            name="new-name",
        )

        expected_network = Network(
            id="net-partial-123",
            name="new-name",
            status="ACTIVE",
            description="old description",
            is_admin_state_up=True,
            is_shared=False,
            mtu=None,
            provider_network_type=None,
            provider_physical_network=None,
            provider_segmentation_id=None,
            project_id=None,
        )

        assert result == expected_network

        expected_args = {"name": "new-name"}
        mock_conn.network.update_network.assert_called_once_with(
            "net-partial-123",
            **expected_args,
        )

    def test_delete_network_success(self, mock_openstack_connect_network):
        """Test deleting a network successfully."""
        mock_conn = mock_openstack_connect_network

        mock_network = Mock()
        mock_network.name = "network-to-delete"

        mock_conn.network.delete_network.return_value = None

        network_tools = self.get_network_tools()
        result = network_tools.delete_network("net-delete-123")

        assert result is None

        mock_conn.network.delete_network.assert_called_once_with(
            "net-delete-123",
            ignore_missing=False,
        )

    def test_get_ports_with_filters(self, mock_openstack_connect_network):
        mock_conn = mock_openstack_connect_network

        port = Mock()
        port.id = "port-1"
        port.name = "p1"
        port.status = "ACTIVE"
        port.description = None
        port.project_id = "proj-1"
        port.network_id = "net-1"
        port.admin_state_up = True
        port.is_admin_state_up = True
        port.device_id = "device-1"
        port.device_owner = "compute:nova"
        port.mac_address = "fa:16:3e:00:00:01"
        port.fixed_ips = [{"subnet_id": "subnet-1", "ip_address": "10.0.0.10"}]
        port.security_group_ids = ["sg-1", "sg-2"]

        mock_conn.network.ports.return_value = [port]

        tools = self.get_network_tools()
        result = tools.get_ports(
            status_filter="ACTIVE",
            device_id="device-1",
            network_id="net-1",
        )

        assert result == [
            Port(
                id="port-1",
                name="p1",
                status="ACTIVE",
                description=None,
                project_id="proj-1",
                network_id="net-1",
                is_admin_state_up=True,
                device_id="device-1",
                device_owner="compute:nova",
                mac_address="fa:16:3e:00:00:01",
                fixed_ips=[
                    {"subnet_id": "subnet-1", "ip_address": "10.0.0.10"},
                ],
                security_group_ids=["sg-1", "sg-2"],
            ),
        ]

        mock_conn.network.ports.assert_called_once_with(
            status="ACTIVE",
            device_id="device-1",
            network_id="net-1",
        )

    def test_create_port_success(self, mock_openstack_connect_network):
        mock_conn = mock_openstack_connect_network

        port = Mock()
        port.id = "port-1"
        port.name = "p1"
        port.status = "DOWN"
        port.description = "desc"
        port.project_id = "proj-1"
        port.network_id = "net-1"
        port.admin_state_up = True
        port.is_admin_state_up = True
        port.device_id = None
        port.device_owner = None
        port.mac_address = "fa:16:3e:00:00:02"
        port.fixed_ips = []
        port.security_group_ids = ["sg-1"]

        mock_conn.network.create_port.return_value = port

        tools = self.get_network_tools()
        result = tools.create_port(
            network_id="net-1",
            name="p1",
            description="desc",
            is_admin_state_up=True,
            fixed_ips=[],
            security_group_ids=["sg-1"],
        )

        assert result == Port(
            id="port-1",
            name="p1",
            status="DOWN",
            description="desc",
            project_id="proj-1",
            network_id="net-1",
            is_admin_state_up=True,
            device_id=None,
            device_owner=None,
            mac_address="fa:16:3e:00:00:02",
            fixed_ips=[],
            security_group_ids=["sg-1"],
        )

        mock_conn.network.create_port.assert_called_once()

    def test_get_ports_status_filter_only(
        self, mock_openstack_connect_network
    ):
        mock_conn = mock_openstack_connect_network

        port = Mock()
        port.id = "port-1"
        port.name = "p1"
        port.status = "DOWN"
        port.description = None
        port.project_id = None
        port.network_id = "net-1"
        port.admin_state_up = True
        port.is_admin_state_up = True
        port.device_id = None
        port.device_owner = None
        port.mac_address = "fa:16:3e:00:00:03"
        port.fixed_ips = []
        port.security_group_ids = None

        mock_conn.network.ports.return_value = [port]

        tools = self.get_network_tools()
        res = tools.get_ports(status_filter="down")
        assert len(res) == 1
        assert res[0].status == "DOWN"
        mock_conn.network.ports.assert_called_once_with(status="DOWN")

    def test_get_port_detail_success(self, mock_openstack_connect_network):
        mock_conn = mock_openstack_connect_network

        port = Mock()
        port.id = "port-1"
        port.name = "p1"
        port.status = "ACTIVE"
        port.description = None
        port.project_id = None
        port.network_id = "net-1"
        port.admin_state_up = True
        port.is_admin_state_up = True
        port.device_id = None
        port.device_owner = None
        port.mac_address = "fa:16:3e:00:00:03"
        port.fixed_ips = []
        port.security_group_ids = None

        mock_conn.network.get_port.return_value = port

        tools = self.get_network_tools()
        result = tools.get_port_detail("port-1")
        assert result.id == "port-1"
        mock_conn.network.get_port.assert_called_once_with("port-1")

    def test_update_port_success(self, mock_openstack_connect_network):
        mock_conn = mock_openstack_connect_network

        port = Mock()
        port.id = "port-1"
        port.name = "p-new"
        port.status = "ACTIVE"
        port.description = "d-new"
        port.project_id = None
        port.network_id = "net-1"
        port.admin_state_up = False
        port.is_admin_state_up = False
        port.device_id = "dev-2"
        port.device_owner = None
        port.mac_address = "fa:16:3e:00:00:04"
        port.fixed_ips = []
        port.security_group_ids = ["sg-2"]

        mock_conn.network.update_port.return_value = port

        tools = self.get_network_tools()
        res = tools.update_port(
            port_id="port-1",
            name="p-new",
            description="d-new",
            is_admin_state_up=False,
            device_id="dev-2",
            security_group_ids=["sg-2"],
        )
        assert res.name == "p-new"
        mock_conn.network.update_port.assert_called_once_with(
            "port-1",
            name="p-new",
            description="d-new",
            admin_state_up=False,
            device_id="dev-2",
            security_groups=["sg-2"],
        )

    def test_delete_port_success(self, mock_openstack_connect_network):
        mock_conn = mock_openstack_connect_network

        port = Mock()
        port.id = "port-1"
        mock_conn.network.delete_port.return_value = None

        tools = self.get_network_tools()
        result = tools.delete_port("port-1")
        assert result is None
        mock_conn.network.delete_port.assert_called_once_with(
            "port-1",
            ignore_missing=False,
        )

    def test_add_port_fixed_ip(self, mock_openstack_connect_network):
        mock_conn = mock_openstack_connect_network

        current = Mock()
        current.fixed_ips = [
            {"subnet_id": "subnet-1", "ip_address": "10.0.0.10"},
        ]
        mock_conn.network.get_port.return_value = current

        updated = Mock()
        updated.id = "port-1"
        updated.name = "p1"
        updated.status = "ACTIVE"
        updated.description = None
        updated.project_id = None
        updated.network_id = "net-1"
        updated.admin_state_up = True
        updated.is_admin_state_up = True
        updated.device_id = None
        updated.device_owner = None
        updated.mac_address = "fa:16:3e:00:00:05"
        updated.fixed_ips = [
            {"subnet_id": "subnet-1", "ip_address": "10.0.0.10"},
            {"subnet_id": "subnet-2", "ip_address": "10.0.1.10"},
        ]
        updated.security_group_ids = None
        mock_conn.network.update_port.return_value = updated

        tools = self.get_network_tools()
        new_fixed = list(current.fixed_ips)
        new_fixed.append({"subnet_id": "subnet-2", "ip_address": "10.0.1.10"})
        res = tools.update_port("port-1", fixed_ips=new_fixed)
        assert len(res.fixed_ips or []) == 2

    def test_remove_port_fixed_ip(self, mock_openstack_connect_network):
        mock_conn = mock_openstack_connect_network

        current = Mock()
        current.fixed_ips = [
            {"subnet_id": "subnet-1", "ip_address": "10.0.0.10"},
            {"subnet_id": "subnet-2", "ip_address": "10.0.1.10"},
        ]
        mock_conn.network.get_port.return_value = current

        updated = Mock()
        updated.id = "port-1"
        updated.name = "p1"
        updated.status = "ACTIVE"
        updated.description = None
        updated.project_id = None
        updated.network_id = "net-1"
        updated.admin_state_up = True
        updated.is_admin_state_up = True
        updated.device_id = None
        updated.device_owner = None
        updated.mac_address = "fa:16:3e:00:00:06"
        updated.fixed_ips = [
            {"subnet_id": "subnet-1", "ip_address": "10.0.0.10"},
        ]
        updated.security_group_ids = None
        mock_conn.network.update_port.return_value = updated

        tools = self.get_network_tools()
        filtered = [
            fi for fi in current.fixed_ips if fi["ip_address"] != "10.0.1.10"
        ]
        res = tools.update_port("port-1", fixed_ips=filtered)
        assert len(res.fixed_ips or []) == 1

    def test_get_and_update_allowed_address_pairs(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        port = Mock()
        port.allowed_address_pairs = []
        mock_conn.network.get_port.return_value = port

        tools = self.get_network_tools()
        lst = tools.get_port_allowed_address_pairs("port-1")
        assert lst == []

        updated = Mock()
        updated.id = "port-1"
        updated.name = "p1"
        updated.status = "ACTIVE"
        updated.description = None
        updated.project_id = None
        updated.network_id = "net-1"
        updated.admin_state_up = True
        updated.is_admin_state_up = True
        updated.device_id = None
        updated.device_owner = None
        updated.mac_address = "fa:16:3e:00:00:07"
        updated.fixed_ips = []
        updated.security_group_ids = None
        mock_conn.network.update_port.return_value = updated

        pairs = []
        pairs.append(
            {"ip_address": "192.0.2.5", "mac_address": "aa:bb:cc:dd:ee:ff"}
        )
        res_add = tools.update_port("port-1", allowed_address_pairs=pairs)
        assert isinstance(res_add, Port)

        filtered = [
            p
            for p in pairs
            if not (
                p["ip_address"] == "192.0.2.5"
                and p["mac_address"] == "aa:bb:cc:dd:ee:ff"
            )
        ]
        res_remove = tools.update_port(
            "port-1", allowed_address_pairs=filtered
        )
        assert isinstance(res_remove, Port)

    def test_set_port_binding_and_admin_state(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        updated = Mock()
        updated.id = "port-1"
        updated.name = "p1"
        updated.status = "ACTIVE"
        updated.description = None
        updated.project_id = None
        updated.network_id = "net-1"
        updated.is_admin_state_up = False
        updated.device_id = None
        updated.device_owner = None
        updated.mac_address = "fa:16:3e:00:00:08"
        updated.fixed_ips = []
        updated.security_group_ids = None
        mock_conn.network.update_port.return_value = updated

        tools = self.get_network_tools()
        res_bind = tools.set_port_binding(
            "port-1",
            host_id="host-1",
            vnic_type="normal",
            profile={"key": "val"},
        )
        assert isinstance(res_bind, Port)

        res_set = tools.update_port("port-1", is_admin_state_up=False)
        assert res_set.is_admin_state_up is False

        current = Mock()
        current.is_admin_state_up = False
        mock_conn.network.get_port.return_value = current
        updated.is_admin_state_up = True
        res_toggle = tools.update_port(
            "port-1", is_admin_state_up=not current.admin_state_up
        )
        assert res_toggle.is_admin_state_up is True

    def test_get_subnets_filters_and_has_gateway_true(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        subnet1 = Mock()
        subnet1.id = "subnet-1"
        subnet1.name = "s1"
        subnet1.status = "ACTIVE"
        subnet1.description = None
        subnet1.project_id = "proj-1"
        subnet1.network_id = "net-1"
        subnet1.cidr = "10.0.0.0/24"
        subnet1.ip_version = 4
        subnet1.gateway_ip = "10.0.0.1"
        subnet1.enable_dhcp = True
        subnet1.is_dhcp_enabled = True
        subnet1.allocation_pools = []
        subnet1.dns_nameservers = []
        subnet1.host_routes = []

        subnet2 = Mock()
        subnet2.id = "subnet-2"
        subnet2.name = "s2"
        subnet2.status = "ACTIVE"
        subnet2.description = None
        subnet2.project_id = "proj-2"
        subnet2.network_id = "net-1"
        subnet2.cidr = "10.0.1.0/24"
        subnet2.ip_version = 4
        subnet2.gateway_ip = None
        subnet2.enable_dhcp = False
        subnet2.is_dhcp_enabled = False
        subnet2.allocation_pools = []
        subnet2.dns_nameservers = []
        subnet2.host_routes = []

        mock_conn.network.subnets.return_value = [subnet1, subnet2]

        tools = self.get_network_tools()
        result = tools.get_subnets(
            network_id="net-1",
            ip_version=4,
            project_id="proj-1",
            has_gateway=True,
            is_dhcp_enabled=True,
        )

        assert len(result) == 1
        assert result[0] == Subnet(
            id="subnet-1",
            name="s1",
            status="ACTIVE",
            description=None,
            project_id="proj-1",
            network_id="net-1",
            cidr="10.0.0.0/24",
            ip_version=4,
            gateway_ip="10.0.0.1",
            is_dhcp_enabled=True,
            allocation_pools=[],
            dns_nameservers=[],
            host_routes=[],
        )

        mock_conn.network.subnets.assert_called_once_with(
            network_id="net-1",
            ip_version=4,
            project_id="proj-1",
            enable_dhcp=True,
        )

    def test_get_subnets_has_gateway_false(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        subnet1 = Mock()
        subnet1.id = "subnet-1"
        subnet1.name = "s1"
        subnet1.status = "ACTIVE"
        subnet1.description = None
        subnet1.project_id = None
        subnet1.network_id = "net-1"
        subnet1.cidr = "10.0.0.0/24"
        subnet1.ip_version = 4
        subnet1.gateway_ip = "10.0.0.1"
        subnet1.enable_dhcp = True
        subnet1.is_dhcp_enabled = True
        subnet1.allocation_pools = []
        subnet1.dns_nameservers = []
        subnet1.host_routes = []

        subnet2 = Mock()
        subnet2.id = "subnet-2"
        subnet2.name = "s2"
        subnet2.status = "ACTIVE"
        subnet2.description = None
        subnet2.project_id = None
        subnet2.network_id = "net-1"
        subnet2.cidr = "10.0.1.0/24"
        subnet2.ip_version = 4
        subnet2.gateway_ip = None
        subnet2.enable_dhcp = False
        subnet2.is_dhcp_enabled = False
        subnet2.allocation_pools = []
        subnet2.dns_nameservers = []
        subnet2.host_routes = []

        mock_conn.network.subnets.return_value = [subnet1, subnet2]

        tools = self.get_network_tools()
        result = tools.get_subnets(
            network_id="net-1",
            has_gateway=False,
        )

        assert len(result) == 1
        assert result[0].id == "subnet-2"

    def test_create_subnet_success(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        subnet = Mock()
        subnet.id = "subnet-new"
        subnet.name = "s-new"
        subnet.status = "ACTIVE"
        subnet.description = "desc"
        subnet.project_id = "proj-1"
        subnet.network_id = "net-1"
        subnet.cidr = "10.0.0.0/24"
        subnet.ip_version = 4
        subnet.gateway_ip = "10.0.0.1"
        subnet.enable_dhcp = True
        subnet.is_dhcp_enabled = True
        subnet.allocation_pools = [{"start": "10.0.0.10", "end": "10.0.0.20"}]
        subnet.dns_nameservers = ["8.8.8.8"]
        subnet.host_routes = []

        mock_conn.network.create_subnet.return_value = subnet

        tools = self.get_network_tools()
        result = tools.create_subnet(
            network_id="net-1",
            cidr="10.0.0.0/24",
            name="s-new",
            gateway_ip="10.0.0.1",
            is_dhcp_enabled=True,
            description="desc",
            dns_nameservers=["8.8.8.8"],
            allocation_pools=[{"start": "10.0.0.10", "end": "10.0.0.20"}],
            host_routes=[],
        )

        assert result == Subnet(
            id="subnet-new",
            name="s-new",
            status="ACTIVE",
            description="desc",
            project_id="proj-1",
            network_id="net-1",
            cidr="10.0.0.0/24",
            ip_version=4,
            gateway_ip="10.0.0.1",
            is_dhcp_enabled=True,
            allocation_pools=[{"start": "10.0.0.10", "end": "10.0.0.20"}],
            dns_nameservers=["8.8.8.8"],
            host_routes=[],
        )

        mock_conn.network.create_subnet.assert_called_once()

    def test_get_subnet_detail_success(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        subnet = Mock()
        subnet.id = "subnet-1"
        subnet.name = "s1"
        subnet.status = "ACTIVE"
        subnet.description = None
        subnet.project_id = "proj-1"
        subnet.network_id = "net-1"
        subnet.cidr = "10.0.0.0/24"
        subnet.ip_version = 4
        subnet.gateway_ip = "10.0.0.1"
        subnet.enable_dhcp = True
        subnet.is_dhcp_enabled = True
        subnet.allocation_pools = []
        subnet.dns_nameservers = []
        subnet.host_routes = []

        mock_conn.network.get_subnet.return_value = subnet

        tools = self.get_network_tools()
        result = tools.get_subnet_detail("subnet-1")

        assert result.id == "subnet-1"
        mock_conn.network.get_subnet.assert_called_once_with("subnet-1")

    def test_update_subnet_success(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        subnet = Mock()
        subnet.id = "subnet-1"
        subnet.name = "s1-new"
        subnet.status = "ACTIVE"
        subnet.description = "d-new"
        subnet.project_id = "proj-1"
        subnet.network_id = "net-1"
        subnet.cidr = "10.0.0.0/24"
        subnet.ip_version = 4
        subnet.gateway_ip = "10.0.0.254"
        subnet.enable_dhcp = False
        subnet.is_dhcp_enabled = False
        subnet.allocation_pools = []
        subnet.dns_nameservers = []
        subnet.host_routes = []

        mock_conn.network.update_subnet.return_value = subnet

        tools = self.get_network_tools()
        result = tools.update_subnet(
            subnet_id="subnet-1",
            name="s1-new",
            description="d-new",
            gateway_ip="10.0.0.254",
            is_dhcp_enabled=False,
        )

        assert result.name == "s1-new"
        mock_conn.network.update_subnet.assert_called_once_with(
            "subnet-1",
            name="s1-new",
            description="d-new",
            gateway_ip="10.0.0.254",
            enable_dhcp=False,
        )

    def test_delete_subnet_success(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        subnet = Mock()
        subnet.id = "subnet-1"
        mock_conn.network.delete_subnet.return_value = None

        tools = self.get_network_tools()
        result = tools.delete_subnet("subnet-1")

        assert result is None
        mock_conn.network.delete_subnet.assert_called_once_with(
            "subnet-1",
            ignore_missing=False,
        )

    def test_set_and_clear_subnet_gateway(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        updated = Mock()
        updated.id = "subnet-1"
        updated.name = "s1"
        updated.status = "ACTIVE"
        updated.description = None
        updated.project_id = None
        updated.network_id = "net-1"
        updated.cidr = "10.0.0.0/24"
        updated.ip_version = 4
        updated.gateway_ip = "10.0.0.254"
        updated.enable_dhcp = True
        updated.is_dhcp_enabled = True
        updated.allocation_pools = []
        updated.dns_nameservers = []
        updated.host_routes = []

        mock_conn.network.update_subnet.return_value = updated

        tools = self.get_network_tools()
        res1 = tools.update_subnet("subnet-1", gateway_ip="10.0.0.254")
        assert res1.gateway_ip == "10.0.0.254"

        updated.gateway_ip = None
        res2 = tools.update_subnet("subnet-1", clear_gateway=True)
        assert res2.gateway_ip is None

    def test_set_and_toggle_subnet_dhcp(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        updated = Mock()
        updated.id = "subnet-1"
        updated.name = "s1"
        updated.status = "ACTIVE"
        updated.description = None
        updated.project_id = None
        updated.network_id = "net-1"
        updated.cidr = "10.0.0.0/24"
        updated.ip_version = 4
        updated.gateway_ip = "10.0.0.1"
        updated.enable_dhcp = True
        updated.is_dhcp_enabled = True
        updated.allocation_pools = []
        updated.dns_nameservers = []
        updated.host_routes = []

        mock_conn.network.update_subnet.return_value = updated

        tools = self.get_network_tools()
        res1 = tools.update_subnet("subnet-1", is_dhcp_enabled=True)
        assert res1.is_dhcp_enabled is True

        updated.enable_dhcp = False
        updated.is_dhcp_enabled = False
        res2 = tools.update_subnet("subnet-1", is_dhcp_enabled=False)
        assert res2.is_dhcp_enabled is False

    def test_get_floating_ips_with_filters_and_unassigned(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        f1 = Mock()
        f1.id = "fip-1"
        f1.name = None
        f1.status = "DOWN"
        f1.description = None
        f1.project_id = "proj-1"
        f1.floating_ip_address = "203.0.113.10"
        f1.floating_network_id = "ext-net"
        f1.fixed_ip_address = None
        f1.port_id = None
        f1.router_id = None

        f2 = Mock()
        f2.id = "fip-2"
        f2.name = None
        f2.status = "ACTIVE"
        f2.description = None
        f2.project_id = "proj-1"
        f2.floating_ip_address = "203.0.113.11"
        f2.floating_network_id = "ext-net"
        f2.fixed_ip_address = "10.0.0.10"
        f2.port_id = "port-1"
        f2.router_id = None

        mock_conn.network.ips.return_value = [f1, f2]

        tools = self.get_network_tools()
        result = tools.get_floating_ips(
            status_filter="ACTIVE",
            project_id="proj-1",
            floating_network_id="ext-net",
            unassigned_only=True,
        )
        assert result == [
            FloatingIP(
                id="fip-1",
                name=None,
                status="DOWN",
                description=None,
                project_id="proj-1",
                floating_ip_address="203.0.113.10",
                floating_network_id="ext-net",
                fixed_ip_address=None,
                port_id=None,
                router_id=None,
            ),
        ]

    def test_create_attach_detach_delete_floating_ip(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        fip = Mock()
        fip.id = "fip-1"
        fip.name = None
        fip.status = "DOWN"
        fip.description = "d"
        fip.project_id = "proj-1"
        fip.floating_ip_address = "203.0.113.10"
        fip.floating_network_id = "ext-net"
        fip.fixed_ip_address = None
        fip.port_id = None
        fip.router_id = None
        mock_conn.network.create_ip.return_value = fip

        tools = self.get_network_tools()
        created = tools.create_floating_ip("ext-net", description="d")
        assert created.floating_network_id == "ext-net"

        updated = Mock()
        updated.id = "fip-1"
        updated.name = None
        updated.status = "ACTIVE"
        updated.description = "d"
        updated.project_id = "proj-1"
        updated.floating_ip_address = "203.0.113.10"
        updated.floating_network_id = "ext-net"
        updated.fixed_ip_address = "10.0.0.10"
        updated.port_id = "port-1"
        updated.router_id = None
        mock_conn.network.update_ip.return_value = updated

        attached = tools.update_floating_ip(
            "fip-1",
            port_id="port-1",
            fixed_ip_address="10.0.0.10",
        )
        assert attached.port_id == "port-1"

        updated.port_id = None
        detached = tools.update_floating_ip("fip-1", clear_port=True)
        assert detached.port_id is None

        mock_conn.network.get_ip.return_value = updated
        tools.delete_floating_ip("fip-1")
        mock_conn.network.delete_ip.assert_called_once_with(
            "fip-1",
            ignore_missing=False,
        )

    def test_update_reassign_bulk_and_auto_assign_floating_ip(
        self,
        mock_openstack_connect_network,
    ):
        mock_conn = mock_openstack_connect_network

        updated = Mock()
        updated.id = "fip-1"
        updated.name = None
        updated.status = "DOWN"
        updated.description = "new desc"
        updated.project_id = None
        updated.floating_ip_address = "203.0.113.10"
        updated.floating_network_id = "ext-net"
        updated.fixed_ip_address = None
        updated.port_id = None
        updated.router_id = None
        mock_conn.network.update_ip.return_value = updated

        tools = self.get_network_tools()
        res_desc = tools.update_floating_ip("fip-1", description="new desc")
        assert res_desc.description == "new desc"

        updated.port_id = "port-2"
        res_reassign = tools.update_floating_ip("fip-1", port_id="port-2")
        assert res_reassign.port_id == "port-2"

        f1 = Mock()
        f1.id = "fip-a"
        f1.name = None
        f1.status = "DOWN"
        f1.description = None
        f1.project_id = None
        f1.floating_ip_address = "203.0.113.20"
        f1.floating_network_id = "ext-net"
        f1.fixed_ip_address = None
        f1.port_id = None
        f1.router_id = None
        mock_conn.network.create_ip.side_effect = [f1]
        bulk = tools.create_floating_ips_bulk("ext-net", 1)
        assert len(bulk) == 1

        exists = Mock()
        exists.id = "fip-b"
        exists.name = None
        exists.status = "DOWN"
        exists.description = None
        exists.project_id = None
        exists.floating_ip_address = "203.0.113.21"
        exists.floating_network_id = "ext-net"
        exists.fixed_ip_address = None
        exists.port_id = None
        exists.router_id = None
        mock_conn.network.ips.return_value = [exists]
        mock_conn.network.update_ip.return_value = exists
        auto = tools.assign_first_available_floating_ip("ext-net", "port-9")
        assert isinstance(auto, FloatingIP)

    def test_get_routers_with_filters(self, mock_openstack_connect_network):
        mock_conn = mock_openstack_connect_network

        r = Mock()
        r.id = "router-1"
        r.name = "r1"
        r.status = "ACTIVE"
        r.description = "desc"
        r.project_id = "proj-1"
        r.is_admin_state_up = True
        r.external_gateway_info = None
        r.is_distributed = False
        r.is_ha = False
        r.routes = []

        mock_conn.network.routers.return_value = [r]

        tools = self.get_network_tools()
        res = tools.get_routers(
            status_filter="ACTIVE",
            project_id="proj-1",
            is_admin_state_up=True,
        )

        assert res == [
            Router(
                id="router-1",
                name="r1",
                status="ACTIVE",
                description="desc",
                project_id="proj-1",
                is_admin_state_up=True,
                external_gateway_info=None,
                is_distributed=False,
                is_ha=False,
                routes=[],
            ),
        ]

        mock_conn.network.routers.assert_called_once_with(
            project_id="proj-1",
            admin_state_up=True,
        )

    def test_create_router_success(self, mock_openstack_connect_network):
        mock_conn = mock_openstack_connect_network

        r = Mock()
        r.id = "router-1"
        r.name = "r1"
        r.status = "ACTIVE"
        r.description = "desc"
        r.project_id = "proj-1"
        r.is_admin_state_up = True
        r.external_gateway_info = None
        r.is_distributed = True
        r.is_ha = None
        r.routes = []
        mock_conn.network.create_router.return_value = r

        tools = self.get_network_tools()
        res = tools.create_router(
            name="r1",
            description="desc",
            is_admin_state_up=True,
            is_distributed=True,
            project_id="proj-1",
            external_gateway_info=ExternalGatewayInfo(network_id="ext-net"),
        )

        assert isinstance(res, Router)
        mock_conn.network.create_router.assert_called_once_with(
            admin_state_up=True,
            name="r1",
            description="desc",
            distributed=True,
            project_id="proj-1",
            external_gateway_info={"network_id": "ext-net"},
        )

    def test_create_router_minimal(self, mock_openstack_connect_network):
        mock_conn = mock_openstack_connect_network

        r = Mock()
        r.id = "router-2"
        r.name = None
        r.status = "DOWN"
        r.description = None
        r.project_id = None
        r.is_admin_state_up = True
        r.external_gateway_info = None
        r.is_distributed = None
        r.is_ha = None
        r.routes = None
        mock_conn.network.create_router.return_value = r

        tools = self.get_network_tools()
        res = tools.create_router()
        assert isinstance(res, Router)
        mock_conn.network.create_router.assert_called_once_with(
            admin_state_up=True,
        )

    def test_get_router_detail_success(self, mock_openstack_connect_network):
        mock_conn = mock_openstack_connect_network

        r = Mock()
        r.id = "router-3"
        r.name = "r3"
        r.status = "ACTIVE"
        r.description = None
        r.project_id = "proj-1"
        r.is_admin_state_up = True
        r.external_gateway_info = None
        r.is_distributed = False
        r.is_ha = False
        r.routes = []
        mock_conn.network.get_router.return_value = r

        tools = self.get_network_tools()
        res = tools.get_router_detail("router-3")
        assert res.id == "router-3"
        mock_conn.network.get_router.assert_called_once_with("router-3")

    def test_update_router_success(self, mock_openstack_connect_network):
        mock_conn = mock_openstack_connect_network

        r = Mock()
        r.id = "router-4"
        r.name = "r4-new"
        r.status = "ACTIVE"
        r.description = "d-new"
        r.project_id = "proj-1"
        r.is_admin_state_up = False
        r.external_gateway_info = None
        r.is_distributed = True
        r.is_ha = False
        r.routes = []
        mock_conn.network.update_router.return_value = r

        tools = self.get_network_tools()
        res = tools.update_router(
            router_id="router-4",
            name="r4-new",
            description="d-new",
            is_admin_state_up=False,
            is_distributed=True,
            external_gateway_info=ExternalGatewayInfo(
                network_id="ext-net", enable_snat=True
            ),
            routes=[
                Route(destination="198.51.100.0/24", nexthop="10.0.0.254")
            ],
        )
        assert res.name == "r4-new"
        mock_conn.network.update_router.assert_called_once_with(
            "router-4",
            name="r4-new",
            description="d-new",
            admin_state_up=False,
            distributed=True,
            external_gateway_info={
                "network_id": "ext-net",
                "enable_snat": True,
            },
            routes=[
                {"destination": "198.51.100.0/24", "nexthop": "10.0.0.254"}
            ],
        )

    def test_update_router_no_fields_returns_current(
        self, mock_openstack_connect_network
    ):
        mock_conn = mock_openstack_connect_network

        current = Mock()
        current.id = "router-5"
        current.name = "r5"
        current.status = "ACTIVE"
        current.description = None
        current.project_id = None
        current.is_admin_state_up = True
        current.external_gateway_info = None
        current.is_distributed = None
        current.is_ha = None
        current.routes = None
        mock_conn.network.get_router.return_value = current

        tools = self.get_network_tools()
        res = tools.update_router("router-5")
        assert res.id == "router-5"

    def test_delete_router_success(self, mock_openstack_connect_network):
        mock_conn = mock_openstack_connect_network
        mock_conn.network.delete_router.return_value = None

        tools = self.get_network_tools()
        result = tools.delete_router("router-6")
        assert result is None
        mock_conn.network.delete_router.assert_called_once_with(
            "router-6",
            ignore_missing=False,
        )
