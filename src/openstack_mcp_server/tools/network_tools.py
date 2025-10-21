from fastmcp import FastMCP

from .base import get_openstack_conn
from .request.network import (
    ExternalGatewayInfo,
    Route,
)
from .response.network import (
    FloatingIP,
    Network,
    Port,
    Router,
    RouterInterface,
    SecurityGroup,
    SecurityGroupRule,
    Subnet,
)


class NetworkTools:
    """
    A class to encapsulate Network-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Network-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_networks)
        mcp.tool()(self.create_network)
        mcp.tool()(self.get_network_detail)
        mcp.tool()(self.update_network)
        mcp.tool()(self.delete_network)
        mcp.tool()(self.get_subnets)
        mcp.tool()(self.create_subnet)
        mcp.tool()(self.get_subnet_detail)
        mcp.tool()(self.update_subnet)
        mcp.tool()(self.delete_subnet)
        mcp.tool()(self.get_ports)
        mcp.tool()(self.create_port)
        mcp.tool()(self.get_port_detail)
        mcp.tool()(self.update_port)
        mcp.tool()(self.delete_port)
        mcp.tool()(self.get_port_allowed_address_pairs)
        mcp.tool()(self.set_port_binding)
        mcp.tool()(self.add_security_group_to_port)
        mcp.tool()(self.remove_security_group_from_port)
        mcp.tool()(self.get_floating_ips)
        mcp.tool()(self.create_floating_ip)
        mcp.tool()(self.delete_floating_ip)
        mcp.tool()(self.update_floating_ip)
        mcp.tool()(self.create_floating_ips_bulk)
        mcp.tool()(self.assign_first_available_floating_ip)
        mcp.tool()(self.get_routers)
        mcp.tool()(self.create_router)
        mcp.tool()(self.get_router_detail)
        mcp.tool()(self.update_router)
        mcp.tool()(self.delete_router)
        mcp.tool()(self.add_router_interface)
        mcp.tool()(self.get_router_interfaces)
        mcp.tool()(self.remove_router_interface)
        mcp.tool()(self.get_security_groups)
        mcp.tool()(self.create_security_group)
        mcp.tool()(self.get_security_group_detail)
        mcp.tool()(self.update_security_group)
        mcp.tool()(self.delete_security_group)
        mcp.tool()(self.create_security_group_rule)
        mcp.tool()(self.get_security_group_rule_detail)
        mcp.tool()(self.delete_security_group_rule)
        mcp.tool()(self.create_security_group_rules_bulk)

    def get_networks(
        self,
        status_filter: str | None = None,
        shared_only: bool = False,
    ) -> list[Network]:
        """
        Get the list of Networks with optional filtering.

        :param status_filter: Filter networks by status (e.g., `ACTIVE`, `DOWN`)
        :param shared_only: If True, only show shared networks
        :return: List of Network objects
        """
        conn = get_openstack_conn()

        filters = {}

        if status_filter:
            filters["status"] = status_filter.upper()

        if shared_only:
            filters["is_shared"] = True

        networks = conn.network.networks(**filters)

        return [
            self._convert_to_network_model(network) for network in networks
        ]

    def create_network(
        self,
        name: str,
        description: str | None = None,
        is_admin_state_up: bool = True,
        is_shared: bool = False,
        provider_network_type: str | None = None,
        provider_physical_network: str | None = None,
        provider_segmentation_id: int | None = None,
        project_id: str | None = None,
    ) -> Network:
        """
        Create a new Network.

        :param name: Network name
        :param description: Network description
        :param is_admin_state_up: Administrative state
        :param is_shared: Whether the network is shared
        :param provider_network_type: Provider network type (e.g., 'vlan', 'flat', 'vxlan')
        :param provider_physical_network: Physical network name
        :param provider_segmentation_id: Segmentation ID for VLAN/VXLAN
        :return: Created Network object
        """
        conn = get_openstack_conn()

        network_args = {
            "name": name,
            "admin_state_up": is_admin_state_up,
            "shared": is_shared,
        }

        if description:
            network_args["description"] = description

        if provider_network_type:
            network_args["provider_network_type"] = provider_network_type

        if project_id:
            network_args["project_id"] = project_id

        if provider_physical_network:
            network_args["provider_physical_network"] = (
                provider_physical_network
            )

        if provider_segmentation_id is not None:
            network_args["provider_segmentation_id"] = provider_segmentation_id

        network = conn.network.create_network(**network_args)

        return self._convert_to_network_model(network)

    def get_network_detail(self, network_id: str) -> Network:
        """
        Get detailed information about a specific Network.

        :param network_id: ID of the network to retrieve
        :return: Network details
        """
        conn = get_openstack_conn()

        network = conn.network.get_network(network_id)
        return self._convert_to_network_model(network)

    def update_network(
        self,
        network_id: str,
        name: str | None = None,
        description: str | None = None,
        is_admin_state_up: bool | None = None,
        is_shared: bool | None = None,
    ) -> Network:
        """
        Update an existing Network.

        :param network_id: ID of the network to update
        :param name: New network name
        :param description: New network description
        :param is_admin_state_up: New administrative state
        :param is_shared: New shared state
        :return: Updated Network object
        """
        conn = get_openstack_conn()

        update_args = {}

        if name:
            update_args["name"] = name
        if description:
            update_args["description"] = description
        if is_admin_state_up is not None:
            update_args["admin_state_up"] = is_admin_state_up
        if is_shared is not None:
            update_args["shared"] = is_shared

        if not update_args:
            current = conn.network.get_network(network_id)
            return self._convert_to_network_model(current)
        network = conn.network.update_network(network_id, **update_args)
        return self._convert_to_network_model(network)

    def delete_network(self, network_id: str) -> None:
        """
        Delete a Network.

        :param network_id: ID of the network to delete
        :return: None
        """
        conn = get_openstack_conn()
        conn.network.delete_network(network_id, ignore_missing=False)

        return None

    def _convert_to_network_model(self, openstack_network) -> Network:
        """
        Convert an OpenStack network object to a Network pydantic model.

        :param openstack_network: OpenStack network object
        :return: Pydantic Network model
        """
        return Network(
            id=openstack_network.id,
            name=openstack_network.name or "",
            status=openstack_network.status or "",
            description=openstack_network.description or None,
            is_admin_state_up=openstack_network.is_admin_state_up or False,
            is_shared=openstack_network.is_shared or False,
            mtu=openstack_network.mtu or None,
            provider_network_type=openstack_network.provider_network_type
            or None,
            provider_physical_network=openstack_network.provider_physical_network
            or None,
            provider_segmentation_id=openstack_network.provider_segmentation_id
            or None,
            project_id=openstack_network.project_id or None,
        )

    def get_subnets(
        self,
        network_id: str | None = None,
        ip_version: int | None = None,
        project_id: str | None = None,
        has_gateway: bool | None = None,
        is_dhcp_enabled: bool | None = None,
    ) -> list[Subnet]:
        """
        Get the list of Subnets with optional filtering.

        Use this to narrow results by network, project, IP version, gateway presence, and
        DHCP-enabled state.

        Notes:
        - has_gateway is applied client-side after retrieval and checks whether `gateway_ip` is set.
        - `is_dhcp_enabled` maps to Neutron's `enable_dhcp` filter.
        - Combining filters further restricts the result (logical AND).

        Examples:
        - All IPv4 subnets in a network: `network_id="net-1"`, `ip_version=4`
        - Only subnets with a gateway: `has_gateway=True`
        - DHCP-enabled subnets for a project: `project_id="proj-1"`, `is_dhcp_enabled=True`

        :param network_id: Filter by network ID
        :param ip_version: Filter by IP version (e.g., 4, 6)
        :param project_id: Filter by project ID
        :param has_gateway: True for subnets with a gateway, False for no gateway
        :param is_dhcp_enabled: True for DHCP-enabled subnets, False for disabled
        :return: List of Subnet objects
        """
        conn = get_openstack_conn()
        filters: dict = {}
        if network_id:
            filters["network_id"] = network_id
        if ip_version is not None:
            filters["ip_version"] = ip_version
        if project_id:
            filters["project_id"] = project_id
        if is_dhcp_enabled is not None:
            filters["enable_dhcp"] = is_dhcp_enabled
        subnets = conn.network.subnets(**filters)
        if has_gateway is not None:
            subnets = [
                s for s in subnets if (s.gateway_ip is not None) == has_gateway
            ]
        return [self._convert_to_subnet_model(subnet) for subnet in subnets]

    def create_subnet(
        self,
        network_id: str,
        cidr: str,
        name: str | None = None,
        ip_version: int = 4,
        gateway_ip: str | None = None,
        is_dhcp_enabled: bool = True,
        description: str | None = None,
        dns_nameservers: list[str] | None = None,
        allocation_pools: list[dict] | None = None,
        host_routes: list[dict] | None = None,
    ) -> Subnet:
        """
        Create a new Subnet.

        :param network_id: ID of the parent network
        :param cidr: Subnet CIDR
        :param name: Subnet name
        :param ip_version: IP version
        :param gateway_ip: Gateway IP address
        :param is_dhcp_enabled: Whether DHCP is enabled
        :param description: Subnet description
        :param dns_nameservers: DNS nameserver list
        :param allocation_pools: Allocation pool list
        :param host_routes: Static host routes
        :return: Created Subnet object
        """
        conn = get_openstack_conn()
        subnet_args: dict = {
            "network_id": network_id,
            "cidr": cidr,
            "ip_version": ip_version,
            "enable_dhcp": is_dhcp_enabled,
        }
        if name:
            subnet_args["name"] = name
        if description:
            subnet_args["description"] = description
        if gateway_ip:
            subnet_args["gateway_ip"] = gateway_ip
        if dns_nameservers is not None:
            subnet_args["dns_nameservers"] = dns_nameservers
        if allocation_pools is not None:
            subnet_args["allocation_pools"] = allocation_pools
        if host_routes is not None:
            subnet_args["host_routes"] = host_routes
        subnet = conn.network.create_subnet(**subnet_args)
        return self._convert_to_subnet_model(subnet)

    def get_subnet_detail(self, subnet_id: str) -> Subnet:
        """
        Get detailed information about a specific Subnet.

        :param subnet_id: ID of the subnet to retrieve
        :return: Subnet details
        """
        conn = get_openstack_conn()
        subnet = conn.network.get_subnet(subnet_id)
        return self._convert_to_subnet_model(subnet)

    def update_subnet(
        self,
        subnet_id: str,
        name: str | None = None,
        description: str | None = None,
        gateway_ip: str | None = None,
        clear_gateway: bool = False,
        is_dhcp_enabled: bool | None = None,
        dns_nameservers: list[str] | None = None,
        allocation_pools: list[dict] | None = None,
        host_routes: list[dict] | None = None,
    ) -> Subnet:
        """
        Update subnet attributes atomically. Only provided parameters are changed; omitted
        parameters remain untouched.

        Typical use-cases:
        - Set gateway: `gateway_ip="10.0.0.1"`.
        - Clear gateway: `clear_gateway=True`.
        - Enable/disable DHCP: `is_dhcp_enabled=True or False`.
        - Batch updates: update name/description and DNS nameservers together.

        Notes:
        - `clear_gateway=True` explicitly clears `gateway_ip` (sets to None). If both `gateway_ip`
          and `clear_gateway=True` are provided, `clear_gateway` takes precedence.
        - For list-typed fields (`dns_nameservers`, `allocation_pools`, `host_routes`), the provided
          list replaces the entire list on the server. Pass `[]` to remove all entries.
        - For a DHCP toggle, read the current value via `get_subnet_detail()` and pass the inverted
          boolean to `is_dhcp_enabled`.

        Examples:
        - Clear the gateway and disable DHCP: `clear_gateway=True`, `is_dhcp_enabled=False`
        - Replace DNS servers: `dns_nameservers=["8.8.8.8", "1.1.1.1"]`

        :param subnet_id: ID of the subnet to update
        :param name: New subnet name
        :param description: New subnet description
        :param gateway_ip: New gateway IP
        :param clear_gateway: If True, clear the gateway IP (sets to None)
        :param is_dhcp_enabled: DHCP enabled state
        :param dns_nameservers: DNS nameserver list (replaces entire list)
        :param allocation_pools: Allocation pool list (replaces entire list)
        :param host_routes: Static host routes (replaces entire list)
        :return: Updated Subnet object
        """
        conn = get_openstack_conn()
        update_args: dict = {}
        if name:
            update_args["name"] = name
        if description:
            update_args["description"] = description
        if clear_gateway:
            update_args["gateway_ip"] = None
        elif gateway_ip:
            update_args["gateway_ip"] = gateway_ip
        if is_dhcp_enabled is not None:
            update_args["enable_dhcp"] = is_dhcp_enabled
        if dns_nameservers is not None:
            update_args["dns_nameservers"] = dns_nameservers
        if allocation_pools is not None:
            update_args["allocation_pools"] = allocation_pools
        if host_routes is not None:
            update_args["host_routes"] = host_routes
        if not update_args:
            current = conn.network.get_subnet(subnet_id)
            return self._convert_to_subnet_model(current)
        subnet = conn.network.update_subnet(subnet_id, **update_args)
        return self._convert_to_subnet_model(subnet)

    def delete_subnet(self, subnet_id: str) -> None:
        """
        Delete a Subnet.

        :param subnet_id: ID of the subnet to delete
        :return: None
        """
        conn = get_openstack_conn()
        conn.network.delete_subnet(subnet_id, ignore_missing=False)
        return None

    def _convert_to_subnet_model(self, openstack_subnet) -> Subnet:
        """
        Convert an OpenStack subnet object to a Subnet pydantic model.

        :param openstack_subnet: OpenStack subnet object
        :return: Pydantic Subnet model
        """
        return Subnet(
            id=openstack_subnet.id,
            name=openstack_subnet.name,
            status=getattr(openstack_subnet, "status", None),
            description=openstack_subnet.description,
            project_id=openstack_subnet.project_id,
            network_id=openstack_subnet.network_id,
            cidr=openstack_subnet.cidr,
            ip_version=openstack_subnet.ip_version,
            gateway_ip=openstack_subnet.gateway_ip,
            is_dhcp_enabled=openstack_subnet.is_dhcp_enabled,
            allocation_pools=getattr(
                openstack_subnet, "allocation_pools", None
            ),
            dns_nameservers=getattr(openstack_subnet, "dns_nameservers", None),
            host_routes=getattr(openstack_subnet, "host_routes", None),
        )

    def get_ports(
        self,
        status_filter: str | None = None,
        device_id: str | None = None,
        network_id: str | None = None,
    ) -> list[Port]:
        """
        Get the list of Ports with optional filtering.

        :param status_filter: Filter by port status (e.g., `ACTIVE`, `DOWN`)
        :param device_id: Filter by device ID
        :param network_id: Filter by network ID
        :return: List of Port objects
        """
        conn = get_openstack_conn()
        filters: dict = {}
        if status_filter:
            filters["status"] = status_filter.upper()
        if device_id:
            filters["device_id"] = device_id
        if network_id:
            filters["network_id"] = network_id

        ports = conn.network.ports(**filters)

        return [self._convert_to_port_model(port) for port in ports]

    def get_port_allowed_address_pairs(self, port_id: str) -> list[dict]:
        """
        Get allowed address pairs configured on a port.

        :param port_id: Port ID
        :return: Allowed address pairs
        """
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        return list(port.allowed_address_pairs or [])

    def set_port_binding(
        self,
        port_id: str,
        host_id: str | None = None,
        vnic_type: str | None = None,
        profile: dict | None = None,
    ) -> Port:
        """
        Set binding attributes for a port.

        :param port_id: Port ID
        :param host_id: Binding host ID
        :param vnic_type: VNIC type
        :param profile: Binding profile
        :return: Updated Port object
        """
        conn = get_openstack_conn()
        update_args: dict = {}
        if host_id:
            update_args["binding_host_id"] = host_id
        if vnic_type:
            update_args["binding_vnic_type"] = vnic_type
        if profile is not None:
            update_args["binding_profile"] = profile
        if not update_args:
            current = conn.network.get_port(port_id)
            return self._convert_to_port_model(current)
        updated = conn.network.update_port(port_id, **update_args)
        return self._convert_to_port_model(updated)

    def add_security_group_to_port(
        self,
        port_id: str,
        security_group_id: str,
    ) -> Port:
        """
        Attach a Security Group to a Port.

        Idempotent: if the security group is already attached, returns the current
        port state without issuing an update.

        :param port_id: Port ID
        :param security_group_id: Security Group ID to attach
        :return: Updated (or current) Port object
        """
        conn = get_openstack_conn()
        current = conn.network.get_port(port_id)
        current_group_ids: list[str] = list(current.security_group_ids or [])
        if security_group_id in current_group_ids:
            return self._convert_to_port_model(current)

        updated_group_ids = current_group_ids + [security_group_id]
        updated = conn.network.update_port(
            port_id, security_groups=updated_group_ids
        )
        return self._convert_to_port_model(updated)

    def remove_security_group_from_port(
        self,
        port_id: str,
        security_group_id: str,
    ) -> Port:
        """
        Detach a Security Group from a Port.

        Idempotent: if the security group is not attached, returns the current
        port state without issuing an update.

        :param port_id: Port ID
        :param security_group_id: Security Group ID to detach
        :return: Updated (or current) Port object
        """
        conn = get_openstack_conn()
        current = conn.network.get_port(port_id)
        current_group_ids: list[str] = list(current.security_group_ids or [])
        if security_group_id not in current_group_ids:
            return self._convert_to_port_model(current)

        updated_group_ids = [
            sg_id for sg_id in current_group_ids if sg_id != security_group_id
        ]
        updated = conn.network.update_port(
            port_id, security_groups=updated_group_ids
        )
        return self._convert_to_port_model(updated)

    def create_port(
        self,
        network_id: str,
        name: str | None = None,
        description: str | None = None,
        is_admin_state_up: bool = True,
        device_id: str | None = None,
        fixed_ips: list[dict] | None = None,
        security_group_ids: list[str] | None = None,
    ) -> Port:
        """
        Create a new Port.

        :param network_id: ID of the parent network
        :param name: Port name
        :param description: Port description
        :param is_admin_state_up: Administrative state
        :param device_id: Device ID
        :param fixed_ips: Fixed IP list
        :param security_group_ids: Security group ID list
        :return: Created Port object
        """
        conn = get_openstack_conn()
        port_args: dict = {
            "network_id": network_id,
            "admin_state_up": is_admin_state_up,
        }
        if name:
            port_args["name"] = name
        if description:
            port_args["description"] = description
        if device_id:
            port_args["device_id"] = device_id
        if fixed_ips is not None:
            port_args["fixed_ips"] = fixed_ips
        if security_group_ids is not None:
            port_args["security_groups"] = security_group_ids
        port = conn.network.create_port(**port_args)
        return self._convert_to_port_model(port)

    def get_port_detail(self, port_id: str) -> Port:
        """
        Get detailed information about a specific Port.

        :param port_id: ID of the port to retrieve
        :return: Port details
        """
        conn = get_openstack_conn()
        port = conn.network.get_port(port_id)
        return self._convert_to_port_model(port)

    def update_port(
        self,
        port_id: str,
        name: str | None = None,
        description: str | None = None,
        is_admin_state_up: bool | None = None,
        device_id: str | None = None,
        security_group_ids: list[str] | None = None,
        allowed_address_pairs: list[dict] | None = None,
        fixed_ips: list[dict] | None = None,
    ) -> Port:
        """
        Update an existing Port. Only provided parameters are changed; omitted parameters remain untouched.

        Typical use-cases:
        - Set admin state down: is_admin_state_up=False
        - Toggle admin state: read current via get_port_detail(); pass inverted value
        - Replace security groups: security_group_ids=["sg-1", "sg-2"]
        - Replace allowed address pairs:
          1) current = get_port_allowed_address_pairs(port_id)
          2) edit the list (append/remove dicts)
          3) update_port(port_id, allowed_address_pairs=current)
        - Replace fixed IPs:
          1) current = get_port_detail(port_id).fixed_ips
          2) edit the list
          3) update_port(port_id, fixed_ips=current)

        Notes:
        - List-typed fields (security groups, allowed address pairs, fixed IPs) replace the entire list
          with the provided value. Pass [] to remove all entries.
        - For fixed IPs, each dict typically includes keys like "subnet_id" and/or "ip_address".

        Examples:
        - Add a fixed IP: read current, append a new {"subnet_id": "subnet-2", "ip_address": "10.0.1.10"},
          then pass fixed_ips=[...]
        - Clear all security groups: security_group_ids=[]

        :param port_id: ID of the port to update
        :param name: New port name
        :param description: New port description
        :param is_admin_state_up: Administrative state
        :param device_id: Device ID
        :param security_group_ids: Security group ID list (replaces entire list)
        :param allowed_address_pairs: Allowed address pairs (replaces entire list)
        :param fixed_ips: Fixed IP assignments (replaces entire list)
        :return: Updated Port object
        """
        conn = get_openstack_conn()
        update_args: dict = {}
        if name:
            update_args["name"] = name
        if description:
            update_args["description"] = description
        if is_admin_state_up is not None:
            update_args["admin_state_up"] = is_admin_state_up
        if device_id:
            update_args["device_id"] = device_id
        if security_group_ids is not None:
            update_args["security_groups"] = security_group_ids
        if allowed_address_pairs is not None:
            update_args["allowed_address_pairs"] = allowed_address_pairs
        if fixed_ips is not None:
            update_args["fixed_ips"] = fixed_ips
        if not update_args:
            current = conn.network.get_port(port_id)
            return self._convert_to_port_model(current)
        port = conn.network.update_port(port_id, **update_args)
        return self._convert_to_port_model(port)

    def delete_port(self, port_id: str) -> None:
        """
        Delete a Port.

        :param port_id: ID of the port to delete
        :return: None
        """
        conn = get_openstack_conn()
        conn.network.delete_port(port_id, ignore_missing=False)
        return None

    def _convert_to_port_model(self, openstack_port) -> Port:
        """
        Convert an OpenStack Port object to a Port pydantic model.

        :param openstack_port: OpenStack port object
        :return: Pydantic Port model
        """
        return Port(
            id=openstack_port.id,
            name=openstack_port.name,
            status=openstack_port.status,
            description=openstack_port.description,
            project_id=openstack_port.project_id,
            network_id=openstack_port.network_id,
            is_admin_state_up=openstack_port.is_admin_state_up,
            device_id=openstack_port.device_id,
            device_owner=openstack_port.device_owner,
            mac_address=openstack_port.mac_address,
            fixed_ips=openstack_port.fixed_ips,
            security_group_ids=openstack_port.security_group_ids
            if hasattr(openstack_port, "security_group_ids")
            else None,
        )

    def get_floating_ips(
        self,
        status_filter: str | None = None,
        project_id: str | None = None,
        port_id: str | None = None,
        floating_network_id: str | None = None,
        unassigned_only: bool | None = None,
    ) -> list[FloatingIP]:
        """
        Get the list of Floating IPs with optional filtering.

        :param status_filter: Filter by IP status (e.g., `ACTIVE`)
        :param project_id: Filter by project ID
        :param port_id: Filter by attached port ID
        :param floating_network_id: Filter by external network ID
        :param unassigned_only: If True, return only unassigned IPs
        :return: List of FloatingIP objects
        """
        conn = get_openstack_conn()
        filters: dict = {}
        if status_filter:
            filters["status"] = status_filter.upper()
        if project_id:
            filters["project_id"] = project_id
        if port_id:
            filters["port_id"] = port_id
        if floating_network_id:
            filters["floating_network_id"] = floating_network_id
        ips = list(conn.network.ips(**filters))
        if unassigned_only:
            ips = [i for i in ips if not i.port_id]
        return [self._convert_to_floating_ip_model(ip) for ip in ips]

    def create_floating_ip(
        self,
        floating_network_id: str,
        description: str | None = None,
        fixed_ip_address: str | None = None,
        port_id: str | None = None,
        project_id: str | None = None,
    ) -> FloatingIP:
        """
        Create a new Floating IP.

        Typical use-cases:
        - Allocate in a pool and attach immediately: provide port_id (and optionally fixed_ip_address).
        - Allocate for later use: omit port_id (unassigned state).
        - Add metadata: provide description.

        :param floating_network_id: External (floating) network ID
        :param description: Floating IP description (omit to keep empty)
        :param fixed_ip_address: Internal fixed IP to map when attaching to a port
        :param port_id: Port ID to attach (omit for unassigned allocation)
        :param project_id: Project ID to assign ownership
        :return: Created FloatingIP object
        """
        conn = get_openstack_conn()
        ip_args: dict = {"floating_network_id": floating_network_id}
        if description:
            ip_args["description"] = description
        if fixed_ip_address:
            ip_args["fixed_ip_address"] = fixed_ip_address
        if port_id:
            ip_args["port_id"] = port_id
        if project_id:
            ip_args["project_id"] = project_id
        ip = conn.network.create_ip(**ip_args)
        return self._convert_to_floating_ip_model(ip)

    def attach_floating_ip_to_port(
        self,
        floating_ip_id: str,
        port_id: str,
        fixed_ip_address: str | None = None,
    ) -> FloatingIP:
        """
        Attach a Floating IP to a Port.

        :param floating_ip_id: Floating IP ID
        :param port_id: Port ID to attach
        :param fixed_ip_address: Specific fixed IP on the port (optional)
        :return: Updated Floating IP object
        """
        conn = get_openstack_conn()
        update_args: dict = {"port_id": port_id}
        if fixed_ip_address:
            update_args["fixed_ip_address"] = fixed_ip_address
        ip = conn.network.update_ip(floating_ip_id, **update_args)
        return self._convert_to_floating_ip_model(ip)

    def update_floating_ip(
        self,
        floating_ip_id: str,
        description: str | None = None,
        port_id: str | None = None,
        fixed_ip_address: str | None = None,
        clear_port: bool = False,
    ) -> FloatingIP:
        """
        Update Floating IP attributes. Only provided parameters are changed; omitted
        parameters remain untouched.

        Typical use-cases:
        - Attach to a port: port_id="port-1" (optionally fixed_ip_address="10.0.0.10").
        - Detach from its port: clear_port=True and omit port_id (sets port_id=None).
        - Keep current port: clear_port=False and omit port_id.
        - Update description: description="new desc" or clear with description=None.
        - Reassign to another port: port_id="new-port" (optionally with fixed_ip_address).

        Notes:
        - Passing None for description clears it.
        - clear_port controls whether to detach when no port_id is provided.
        - fixed_ip_address is optional and can be provided alongside port_id.

        :param floating_ip_id: Floating IP ID to update
        :param description: New description (omit to keep unchanged, None to clear)
        :param port_id: Port ID to attach; omit to keep or detach depending on clear_port
        :param clear_port: If True and port_id is omitted, detach (set port_id=None); if False and
                           port_id is omitted, keep current attachment
        :param fixed_ip_address: Specific fixed IP to map when attaching
        :return: Updated FloatingIP object
        """
        conn = get_openstack_conn()
        update_args: dict = {}
        if description:
            update_args["description"] = description
        if port_id:
            update_args["port_id"] = port_id
            if fixed_ip_address:
                update_args["fixed_ip_address"] = fixed_ip_address
        else:
            if clear_port:
                update_args["port_id"] = None
        if not update_args:
            current = conn.network.get_ip(floating_ip_id)
            return self._convert_to_floating_ip_model(current)
        ip = conn.network.update_ip(floating_ip_id, **update_args)
        return self._convert_to_floating_ip_model(ip)

    def delete_floating_ip(self, floating_ip_id: str) -> None:
        """
        Delete a Floating IP.

        :param floating_ip_id: Floating IP ID to delete
        :return: None
        """
        conn = get_openstack_conn()
        conn.network.delete_ip(floating_ip_id, ignore_missing=False)
        return None

    def create_floating_ips_bulk(
        self,
        floating_network_id: str,
        count: int,
    ) -> list[FloatingIP]:
        """
        Create multiple floating IPs on the specified external network.

        :param floating_network_id: External network ID
        :param count: Number of floating IPs to create (negative treated as 0)
        :return: List of created FloatingIP objects
        """
        conn = get_openstack_conn()
        created = []
        for _ in range(max(0, count)):
            ip = conn.network.create_ip(
                floating_network_id=floating_network_id,
            )
            created.append(self._convert_to_floating_ip_model(ip))
        return created

    def assign_first_available_floating_ip(
        self,
        floating_network_id: str,
        port_id: str,
    ) -> FloatingIP:
        """
        Assign the first available floating IP from a network to a port.
        If none are available, create a new one and assign it.

        :param floating_network_id: External network ID
        :param port_id: Target port ID
        :return: Updated FloatingIP object
        """
        conn = get_openstack_conn()
        existing = list(
            conn.network.ips(floating_network_id=floating_network_id),
        )
        available = next(
            (i for i in existing if not i.port_id),
            None,
        )
        if available is None:
            created = conn.network.create_ip(
                floating_network_id=floating_network_id,
            )
            target_id = created.id
        else:
            target_id = available.id
        ip = conn.network.update_ip(target_id, port_id=port_id)
        return self._convert_to_floating_ip_model(ip)

    def _convert_to_floating_ip_model(self, openstack_ip) -> FloatingIP:
        """
        Convert an OpenStack floating IP object to a FloatingIP pydantic model.

        :param openstack_ip: OpenStack floating IP object
        :return: Pydantic FloatingIP model
        """
        return FloatingIP(
            id=openstack_ip.id,
            name=openstack_ip.name,
            status=openstack_ip.status,
            description=openstack_ip.description,
            project_id=openstack_ip.project_id,
            floating_ip_address=openstack_ip.floating_ip_address,
            floating_network_id=openstack_ip.floating_network_id,
            fixed_ip_address=openstack_ip.fixed_ip_address,
            port_id=openstack_ip.port_id,
            router_id=openstack_ip.router_id,
        )

    def get_routers(
        self,
        status_filter: str | None = None,
        project_id: str | None = None,
        is_admin_state_up: bool | None = None,
    ) -> list[Router]:
        """
        Get the list of Routers with optional filtering.
        :param status_filter: Filter by router status (e.g., `ACTIVE`, `DOWN`)
        :param project_id: Filter by project ID
        :param is_admin_state_up: Filter by admin state
        :return: List of Router objects
        """
        conn = get_openstack_conn()
        filters: dict = {}
        if status_filter:
            filters["status"] = status_filter.upper()
        if project_id:
            filters["project_id"] = project_id
        if is_admin_state_up is not None:
            filters["admin_state_up"] = is_admin_state_up
        # Do not pass unsupported filters (e.g., status) to the server.
        server_filters = self._sanitize_server_filters(filters)
        routers = conn.network.routers(**server_filters)

        router_models = [self._convert_to_router_model(r) for r in routers]
        if status_filter:
            status_upper = status_filter.upper()
            router_models = [
                r
                for r in router_models
                if (r.status or "").upper() == status_upper
            ]
        return router_models

    def create_router(
        self,
        name: str | None = None,
        description: str | None = None,
        is_admin_state_up: bool = True,
        is_distributed: bool | None = None,
        project_id: str | None = None,
        external_gateway_info: ExternalGatewayInfo | None = None,
    ) -> Router:
        """
        Create a new Router.
        Typical use-cases:
        - Create basic router: name="r1" (defaults to admin_state_up=True)
        - Create distributed router: is_distributed=True
        - Create with external gateway for north-south traffic:
          external_gateway_info={"network_id": "ext-net", "enable_snat": True,
          "external_fixed_ips": [{"subnet_id": "ext-subnet", "ip_address": "203.0.113.10"}]}
        - Create with project ownership: project_id="proj-1"
        Notes:
        - external_gateway_info should follow Neutron schema: at minimum include
          "network_id"; optional keys include "enable_snat" and "external_fixed_ips".
        :param name: Router name
        :param description: Router description
        :param is_admin_state_up: Administrative state
        :param is_distributed: Distributed router flag
        :param project_id: Project ownership
        :param external_gateway_info: External gateway info dict
        :return: Created Router object
        """
        conn = get_openstack_conn()
        router_args: dict = {"admin_state_up": is_admin_state_up}
        if name:
            router_args["name"] = name
        if description:
            router_args["description"] = description
        if is_distributed is not None:
            router_args["distributed"] = is_distributed
        if project_id:
            router_args["project_id"] = project_id
        if external_gateway_info is not None:
            router_args["external_gateway_info"] = (
                external_gateway_info.model_dump(exclude_none=True)
            )
        router = conn.network.create_router(**router_args)
        return self._convert_to_router_model(router)

    def get_router_detail(self, router_id: str) -> Router:
        """
        Get detailed information about a specific Router.
        :param router_id: ID of the router to retrieve
        :return: Router details
        """
        conn = get_openstack_conn()
        router = conn.network.get_router(router_id)
        return self._convert_to_router_model(router)

    def update_router(
        self,
        router_id: str,
        name: str | None = None,
        description: str | None = None,
        is_admin_state_up: bool | None = None,
        is_distributed: bool | None = None,
        external_gateway_info: ExternalGatewayInfo | None = None,
        clear_external_gateway: bool = False,
        routes: list[Route] | None = None,
    ) -> Router:
        """
        Update Router attributes atomically. Only provided parameters are changed;
        omitted parameters remain untouched.
        Typical use-cases:
        - Rename and change description: name="r-new", description="d".
        - Toggle admin state: read current via get_router_detail(); pass inverted bool to is_admin_state_up.
        - Set distributed flag: is_distributed=True or False.
        - Set external gateway: external_gateway_info={"network_id": "ext-net", "enable_snat": True, "external_fixed_ips": [...]}.
        - Clear external gateway: clear_external_gateway=True (takes precedence over external_gateway_info).
        - Replace static routes: routes=[{"destination": "192.0.2.0/24", "nexthop": "10.0.0.1"}]. Pass [] to remove all routes.
        Notes:
        - For list-typed fields (routes), the provided list replaces the entire list on the server.
        - To clear external gateway, use clear_external_gateway=True. If both provided, clear_external_gateway takes precedence.
        :param router_id: ID of the router to update
        :param name: New router name
        :param description: New router description
        :param is_admin_state_up: Administrative state
        :param is_distributed: Distributed router flag
        :param external_gateway_info: External gateway info dict to set
        :param clear_external_gateway: If True, clear external gateway (set to None)
        :param routes: Static routes (replaces entire list)
        :return: Updated Router object
        """
        conn = get_openstack_conn()
        update_args: dict = {}
        if name:
            update_args["name"] = name
        if description:
            update_args["description"] = description
        if is_admin_state_up is not None:
            update_args["admin_state_up"] = is_admin_state_up
        if is_distributed is not None:
            update_args["distributed"] = is_distributed
        if clear_external_gateway:
            update_args["external_gateway_info"] = None
        elif external_gateway_info is not None:
            update_args["external_gateway_info"] = (
                external_gateway_info.model_dump(exclude_none=True)
            )
        if routes is not None:
            update_args["routes"] = [
                r.model_dump(exclude_none=True) for r in routes
            ]
        if not update_args:
            current = conn.network.get_router(router_id)
            return self._convert_to_router_model(current)
        router = conn.network.update_router(router_id, **update_args)
        return self._convert_to_router_model(router)

    def delete_router(self, router_id: str) -> None:
        """
        Delete a Router.
        :param router_id: ID of the router to delete
        :return: None
        """
        conn = get_openstack_conn()
        conn.network.delete_router(router_id, ignore_missing=False)
        return None

    def add_router_interface(
        self,
        router_id: str,
        subnet_id: str | None = None,
        port_id: str | None = None,
    ) -> RouterInterface:
        """
        Add an interface to a Router by subnet or port.
        Provide either subnet_id or port_id.

        :param router_id: Target router ID
        :param subnet_id: Subnet ID to attach (mutually exclusive with port_id)
        :param port_id: Port ID to attach (mutually exclusive with subnet_id)
        :return: Created/attached router interface information as RouterInterface
        """
        conn = get_openstack_conn()
        args: dict = {}
        args["subnet_id"] = subnet_id
        args["port_id"] = port_id
        res = conn.network.add_interface_to_router(router_id, **args)
        return RouterInterface(
            router_id=res.get("router_id", router_id),
            port_id=res.get("port_id"),
            subnet_id=res.get("subnet_id"),
        )

    def get_router_interfaces(self, router_id: str) -> list[RouterInterface]:
        """
        List interfaces attached to a Router.

        :param router_id: Target router ID
        :return: List of RouterInterface objects representing router-owned ports
        """
        conn = get_openstack_conn()
        filters = {
            "device_id": router_id,
            "device_owner": "network:router_interface",
        }
        ports = conn.network.ports(**filters)
        result: list[RouterInterface] = []
        for p in ports:
            subnet_id = None
            if getattr(p, "fixed_ips", None):
                first = p.fixed_ips[0]
                if isinstance(first, dict):
                    subnet_id = first.get("subnet_id")
            result.append(
                RouterInterface(
                    router_id=router_id,
                    port_id=p.id,
                    subnet_id=subnet_id,
                )
            )
        return result

    def remove_router_interface(
        self,
        router_id: str,
        subnet_id: str | None = None,
        port_id: str | None = None,
    ) -> RouterInterface:
        """
        Remove an interface from a Router by subnet or port.
        Provide either subnet_id or port_id.

        :param router_id: Target router ID
        :param subnet_id: Subnet ID to detach (mutually exclusive with port_id)
        :param port_id: Port ID to detach (mutually exclusive with subnet_id)
        :return: Detached interface information as RouterInterface
        """
        conn = get_openstack_conn()
        args: dict = {}
        if subnet_id:
            args["subnet_id"] = subnet_id
        if port_id:
            args["port_id"] = port_id
        res = conn.network.remove_interface_from_router(router_id, **args)
        return RouterInterface(
            router_id=res.get("router_id", router_id),
            port_id=res.get("port_id"),
            subnet_id=res.get("subnet_id"),
        )

    def _convert_to_router_model(self, openstack_router) -> Router:
        """
        Convert an OpenStack Router object to a Router pydantic model.
        :param openstack_router: OpenStack router object
        :return: Pydantic Router model
        """
        return Router(
            id=openstack_router.id,
            name=getattr(openstack_router, "name", None),
            status=getattr(openstack_router, "status", None),
            description=getattr(openstack_router, "description", None),
            project_id=getattr(openstack_router, "project_id", None),
            is_admin_state_up=getattr(
                openstack_router, "is_admin_state_up", None
            ),
            external_gateway_info=getattr(
                openstack_router, "external_gateway_info", None
            ),
            is_distributed=getattr(openstack_router, "is_distributed", None),
            is_ha=getattr(openstack_router, "is_ha", None),
            routes=getattr(openstack_router, "routes", None),
        )

    def _sanitize_server_filters(self, filters: dict) -> dict:
        """
        Remove unsupported query params before sending to Neutron.

        Currently removed keys:
        - "status": not universally supported for server-side filtering

        :param filters: original filter dict
        :return: cleaned filter dict safe for server query
        """
        if not filters:
            return {}
        attrs = dict(filters)
        attrs.pop("status", None)
        return attrs

    def get_security_groups(
        self,
        project_id: str | None = None,
        name: str | None = None,
        id: str | None = None,
    ) -> list[SecurityGroup]:
        """
        Get the list of Security Groups with optional filtering.

        :param project_id: Filter by project ID
        :param name: Filter by security group name
        :param id: Filter by security group ID
        :return: List of SecurityGroup objects
        """
        conn = get_openstack_conn()
        filters: dict = {}
        if project_id:
            filters["project_id"] = project_id
        if name:
            filters["name"] = name
        if id:
            filters["id"] = id
        security_groups = conn.network.security_groups(**filters)
        return [
            self._convert_to_security_group_model(sg) for sg in security_groups
        ]

    def create_security_group(
        self,
        name: str,
        description: str | None = None,
        project_id: str | None = None,
    ) -> SecurityGroup:
        """
        Create a new Security Group.

        :param name: Security group name
        :param description: Security group description
        :param project_id: Project ID to assign ownership
        :return: Created SecurityGroup object
        """
        conn = get_openstack_conn()
        args: dict = {"name": name}
        if description:
            args["description"] = description
        if project_id:
            args["project_id"] = project_id
        sg = conn.network.create_security_group(**args)
        return self._convert_to_security_group_model(sg)

    def get_security_group_detail(
        self, security_group_id: str
    ) -> SecurityGroup:
        """
        Get detailed information about a specific Security Group.

        :param security_group_id: ID of the security group to retrieve
        :return: SecurityGroup details
        """
        conn = get_openstack_conn()
        sg = conn.network.get_security_group(security_group_id)
        return self._convert_to_security_group_model(sg)

    def update_security_group(
        self,
        security_group_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> SecurityGroup:
        """
        Update an existing Security Group.

        :param security_group_id: ID of the security group to update
        :param name: New security group name
        :param description: New security group description
        :return: Updated SecurityGroup object
        """
        conn = get_openstack_conn()
        update_args: dict = {}
        if name:
            update_args["name"] = name
        if description:
            update_args["description"] = description
        if not update_args:
            current = conn.network.get_security_group(security_group_id)
            return self._convert_to_security_group_model(current)
        sg = conn.network.update_security_group(
            security_group_id, **update_args
        )
        return self._convert_to_security_group_model(sg)

    def delete_security_group(self, security_group_id: str) -> None:
        """
        Delete a Security Group.

        :param security_group_id: ID of the security group to delete
        :return: None
        """
        conn = get_openstack_conn()
        conn.network.delete_security_group(
            security_group_id, ignore_missing=False
        )
        return None

    def _convert_to_security_group_model(self, openstack_sg) -> SecurityGroup:
        """
        Convert an OpenStack Security Group object to a SecurityGroup pydantic model.

        :param openstack_sg: OpenStack security group object
        :return: Pydantic SecurityGroup model
        """
        rule_ids: list[str] | None = None
        rules = getattr(openstack_sg, "security_group_rules", None)
        if rules is not None:
            extracted: list[str] = []
            for r in rules:
                rid = (
                    r.get("id")
                    if isinstance(r, dict)
                    else getattr(r, "id", None)
                )
                if rid:
                    extracted.append(str(rid))
            rule_ids = extracted

        return SecurityGroup(
            id=openstack_sg.id,
            name=getattr(openstack_sg, "name", None),
            status=getattr(openstack_sg, "status", None),
            description=getattr(openstack_sg, "description", None),
            project_id=getattr(openstack_sg, "project_id", None),
            security_group_rule_ids=rule_ids,
        )

    def create_security_group_rule(
        self,
        security_group_id: str,
        direction: str = "ingress",
        ethertype: str = "IPv4",
        protocol: str | None = None,
        port_range_min: int | None = None,
        port_range_max: int | None = None,
        remote_ip_prefix: str | None = None,
        remote_group_id: str | None = None,
        description: str | None = None,
        project_id: str | None = None,
    ) -> SecurityGroupRule:
        """
        Create a Security Group Rule.

        :param security_group_id: Target security group ID
        :param direction: "ingress" or "egress"
        :param ethertype: "IPv4" or "IPv6"
        :param protocol: L4 protocol (e.g., "tcp", "udp", "icmp")
        :param port_range_min: Minimum port
        :param port_range_max: Maximum port
        :param remote_ip_prefix: Source/destination CIDR
        :param remote_group_id: Peer security group ID
        :param description: Rule description
        :param project_id: Project ownership
        :return: Created SecurityGroupRule
        """
        conn = get_openstack_conn()
        args: dict = {
            "security_group_id": security_group_id,
            "direction": direction,
            "ethertype": ethertype,
        }
        args["protocol"] = protocol
        args["port_range_min"] = port_range_min
        args["port_range_max"] = port_range_max
        args["remote_ip_prefix"] = remote_ip_prefix
        args["remote_group_id"] = remote_group_id
        args["description"] = description
        args["project_id"] = project_id
        rule = conn.network.create_security_group_rule(**args)
        return self._convert_to_security_group_rule_model(rule)

    def get_security_group_rule_detail(
        self, rule_id: str
    ) -> SecurityGroupRule:
        """
        Get detailed information about a specific Security Group Rule.

        :param rule_id: Rule ID
        :return: SecurityGroupRule detail
        """
        conn = get_openstack_conn()
        rule = conn.network.get_security_group_rule(rule_id)
        return self._convert_to_security_group_rule_model(rule)

    def delete_security_group_rule(self, rule_id: str) -> None:
        """
        Delete a Security Group Rule.

        :param rule_id: Rule ID to delete
        :return: None
        """
        conn = get_openstack_conn()
        conn.network.delete_security_group_rule(rule_id, ignore_missing=False)
        return None

    def create_security_group_rules_bulk(
        self,
        rules: list[dict],
    ) -> list[SecurityGroupRule]:
        """
        Create multiple Security Group Rules in bulk.

        Each rule dict should follow Neutron SG rule schema keys (e.g.,
        security_group_id, direction, ethertype, protocol, port_range_min,
        port_range_max, remote_ip_prefix, remote_group_id, description, project_id).

        :param rules: List of rule dictionaries
        :return: List of created SecurityGroupRule models
        """
        conn = get_openstack_conn()
        created = conn.network.create_security_group_rules(rules=rules)
        return [self._convert_to_security_group_rule_model(r) for r in created]

    def _convert_to_security_group_rule_model(
        self, openstack_rule
    ) -> SecurityGroupRule:
        """
        Convert an OpenStack Security Group Rule object to a pydantic model.

        :param openstack_rule: OpenStack rule object
        :return: SecurityGroupRule model
        """
        return SecurityGroupRule(
            id=getattr(openstack_rule, "id"),
            name=getattr(openstack_rule, "name", None),
            status=getattr(openstack_rule, "status", None),
            description=getattr(openstack_rule, "description", None),
            project_id=getattr(openstack_rule, "project_id", None),
            direction=getattr(openstack_rule, "direction", None),
            ethertype=getattr(openstack_rule, "ethertype", None),
            protocol=getattr(openstack_rule, "protocol", None),
            port_range_min=getattr(openstack_rule, "port_range_min", None),
            port_range_max=getattr(openstack_rule, "port_range_max", None),
            remote_ip_prefix=getattr(openstack_rule, "remote_ip_prefix", None),
            remote_group_id=getattr(openstack_rule, "remote_group_id", None),
            security_group_id=getattr(
                openstack_rule, "security_group_id", None
            ),
        )
