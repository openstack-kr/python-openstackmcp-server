from fastmcp import FastMCP

from openstack_mcp_server.tools.response.network import Network

from .base import get_openstack_conn


class NetworkTools:
    """
    A class to encapsulate Neutron-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Neutron-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_networks)
        mcp.tool()(self.create_network)
        mcp.tool()(self.get_network_detail)
        mcp.tool()(self.update_network)
        mcp.tool()(self.delete_network)

    def get_networks(
        self,
        status_filter: str | None = None,
        shared_only: bool = False,
    ) -> list[Network]:
        """
        Get the list of Neutron networks with optional filtering.

        Args:
            status_filter: Filter networks by status (e.g., 'ACTIVE', 'DOWN')
            shared_only: If True, only show shared networks

        Returns:
            List of Network objects
        """
        conn = get_openstack_conn()

        filters = {}

        if status_filter:
            filters["status"] = status_filter.upper()

        if shared_only:
            filters["shared"] = True

        networks = conn.list_networks(filters=filters)

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
    ) -> Network:
        """
        Create a new Neutron network.

        Args:
            name: Network name
            description: Network description
            is_admin_state_up: Administrative state
            is_shared: Whether the network is shared
            provider_network_type: Provider network type (e.g., 'vlan', 'flat', 'vxlan')
            provider_physical_network: Physical network name
            provider_segmentation_id: Segmentation ID for VLAN/VXLAN

        Returns:
            Created Network object
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
        Get detailed information about a specific Neutron network.

        Args:
            network_id: ID of the network to retrieve

        Returns:
            Network object with detailed information
        """
        conn = get_openstack_conn()

        network = conn.network.get_network(network_id)
        if not network:
            raise Exception(f"Network with ID {network_id} not found")

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
        Update an existing Neutron network.

        Args:
            network_id: ID of the network to update
            name: New network name
            description: New network description
            is_admin_state_up: New administrative state
            is_shared: New shared state

        Returns:
            Updated Network object
        """
        conn = get_openstack_conn()

        update_args = {}

        if name is not None:
            update_args["name"] = name
        if description is not None:
            update_args["description"] = description
        if is_admin_state_up is not None:
            update_args["admin_state_up"] = is_admin_state_up
        if is_shared is not None:
            update_args["shared"] = is_shared

        if not update_args:
            raise Exception("No update parameters provided")

        network = conn.network.update_network(network_id, **update_args)

        return self._convert_to_network_model(network)

    def delete_network(self, network_id: str) -> None:
        """
        Delete a Neutron network.

        Args:
            network_id: ID of the network to delete

        Returns:
            None
        """
        conn = get_openstack_conn()

        network = conn.network.get_network(network_id)
        if not network:
            raise Exception(f"Network with ID {network_id} not found")

        conn.network.delete_network(network_id, ignore_missing=False)

        return None

    def _convert_to_network_model(self, openstack_network) -> Network:
        """
        Convert an OpenStack network object to a Network pydantic model.

        Args:
            openstack_network: OpenStack network object

        Returns:
            Network pydantic model
        """
        return Network(
            id=openstack_network.id,
            name=openstack_network.name or "",
            status=openstack_network.status or "",
            description=openstack_network.description or None,
            is_admin_state_up=openstack_network.admin_state_up or False,
            is_shared=openstack_network.shared or False,
            mtu=openstack_network.mtu or None,
            provider_network_type=openstack_network.provider_network_type
            or None,
            provider_physical_network=openstack_network.provider_physical_network
            or None,
            provider_segmentation_id=openstack_network.provider_segmentation_id
            or None,
            project_id=openstack_network.project_id or None,
        )
