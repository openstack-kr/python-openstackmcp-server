from enum import Enum
from typing import Any

from fastmcp import FastMCP

from openstack_mcp_server.tools.response.compute import (
    Flavor,
    Server,
)

from .base import get_openstack_conn


class ServerActionEnum(str, Enum):
    """available actions without parameter for compute tools"""

    PAUSE = "pause"
    UNPAUSE = "unpause"
    SUSPEND = "suspend"
    RESUME = "resume"
    LOCK = "lock"
    UNLOCK = "unlock"
    RESCUE = "rescue"
    UNRESCUE = "unrescue"
    START = "start"
    STOP = "stop"
    SHELVE = "shelve"
    SHELVE_OFFLOAD = "shelve_offload"
    UNSHELVE = "unshelve"


class ComputeTools:
    """
    A class to encapsulate Compute-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Compute-related tools with the FastMCP instance.
        """
        mcp.tool()(self.get_servers)
        mcp.tool()(self.get_server)
        mcp.tool()(self.create_server)
        mcp.tool()(self.get_flavors)
        mcp.tool()(self.action_server)
        mcp.tool()(self.update_server)
        mcp.tool()(self.delete_server)
        mcp.tool()(self.attach_volume)
        mcp.tool()(self.detach_volume)

    def get_servers(self) -> list[Server]:
        """
        Get the list of Compute servers.

        :return: A list of Server objects.
        """
        conn = get_openstack_conn()
        server_list = []
        for server in conn.compute.servers():
            server_list.append(Server(**server))

        return server_list

    def get_server(self, id: str) -> Server:
        """
        Get a specific Compute server.

        :param id: The ID of the server to retrieve.
        :return: A Server object.
        """
        conn = get_openstack_conn()
        server = conn.compute.get_server(id)
        return Server(**server)

    def create_server(
        self,
        name: str,
        image: str,
        flavor: int,
        network: str,
        key_name: str | None = None,
        security_groups: list[str] | None = None,
        user_data: str | None = None,
    ) -> Server:
        """
        Create a new Compute server.

        :param name: The name of the server.
        :param image: The ID of the image to use.
        :param flavor: The ID of the flavor to use.
        :param network: The ID of the network to attach.
        :param key_name: The name of the key pair to use.
        :param security_groups: A list of security group names to attach.
        :param user_data: User data to pass to the server.
        :return: A Server object
        """
        conn = get_openstack_conn()
        server_params: dict[str, Any] = {
            "name": name,
            "flavorRef": flavor,
            "imageRef": image,
            "networks": [{"uuid": network}],
            "key_name": key_name,
            "security_groups": security_groups,
            "user_data": user_data,
        }
        server_params = {
            k: v for k, v in server_params.items() if v is not None
        }

        resp = conn.compute.create_server(**server_params)
        # NOTE: The create_server method returns a server object with minimal information.
        # To get the full server details, we need to fetch it again.
        server = conn.compute.get_server(resp.id)

        return Server(**server)

    def get_flavors(self) -> list[Flavor]:
        """
        Get flavors (server hardware configurations).

        :return: A list of Flavor objects.
        """
        conn = get_openstack_conn()
        flavor_list = []
        for flavor in conn.compute.flavors():
            flavor_list.append(Flavor(**flavor))
        return flavor_list

    def action_server(self, id: str, action: str) -> None:
        """
        Perform an action on a Compute server.

        :param id: The ID of the server.
        :param action: The action to perform.
                      Available actions:
                      - pause: Pauses a server. Changes its status to PAUSED
                      - unpause: Unpauses a paused server and changes its status to ACTIVE
                      - suspend: Suspends a server and changes its status to SUSPENDED
                      - resume: Resumes a suspended server and changes its status to ACTIVE
                      - lock: Locks a server
                      - unlock: Unlocks a locked server
                      - rescue: Puts a server in rescue mode and changes its status to RESCUE
                      - unrescue: Unrescues a server. Changes status to ACTIVE
                      - start: Starts a stopped server and changes its status to ACTIVE
                      - stop: Stops a running server and changes its status to SHUTOFF
                      - shelve: Shelves a server
                      - shelve_offload: Shelf-offloads, or removes, a shelved server
                      - unshelve: Unshelves, or restores, a shelved server
                      Only above actions are currently supported
        :raises ValueError: If the action is not supported or invalid(ConflictException).
        """
        conn = get_openstack_conn()

        action_methods = {
            ServerActionEnum.PAUSE.value: conn.compute.pause_server,
            ServerActionEnum.UNPAUSE.value: conn.compute.unpause_server,
            ServerActionEnum.SUSPEND.value: conn.compute.suspend_server,
            ServerActionEnum.RESUME.value: conn.compute.resume_server,
            ServerActionEnum.LOCK.value: conn.compute.lock_server,
            ServerActionEnum.UNLOCK.value: conn.compute.unlock_server,
            ServerActionEnum.RESCUE.value: conn.compute.rescue_server,
            ServerActionEnum.UNRESCUE.value: conn.compute.unrescue_server,
            ServerActionEnum.START.value: conn.compute.start_server,
            ServerActionEnum.STOP.value: conn.compute.stop_server,
            ServerActionEnum.SHELVE.value: conn.compute.shelve_server,
            ServerActionEnum.SHELVE_OFFLOAD.value: conn.compute.shelve_offload_server,
            ServerActionEnum.UNSHELVE.value: conn.compute.unshelve_server,
        }

        if action not in action_methods:
            raise ValueError(f"Unsupported action: {action}")

        action_methods[action](id)
        return None

    def update_server(
        self,
        id: str,
        accessIPv4: str | None = None,
        accessIPv6: str | None = None,
        name: str | None = None,
        hostname: str | None = None,
        description: str | None = None,
    ) -> Server:
        """
        Update a Compute server's name, hostname, or description.

        :param id: The UUID of the server.
        :param accessIPv4: IPv4 address that should be used to access this server.
        :param accessIPv6: IPv6 address that should be used to access this server.
        :param name: The server name.
        :param hostname: The hostname to configure for the instance in the metadata service.
        :param description: A free form description of the server.
        :return: The updated Server object.
        """
        conn = get_openstack_conn()
        server_params = {
            "accessIPv4": accessIPv4,
            "accessIPv6": accessIPv6,
            "name": name,
            "hostname": hostname,
            "description": description,
        }
        server_params = {
            k: v for k, v in server_params.items() if v is not None
        }
        server = conn.compute.update_server(id, **server_params)
        return Server(**server)

    def delete_server(self, id: str) -> None:
        """
        Delete a Compute server.

        :param id: The UUID of the server.
        """
        conn = get_openstack_conn()
        conn.compute.delete_server(id)

    def attach_volume(
        self, server_id: str, volume_id: str, device: str | None = None
    ) -> None:
        """
        Attach a volume to a Compute server.

        :param server_id: The UUID of the server.
        :param volume_id: The UUID of the volume to attach.
        :param device: Name of the device such as, /dev/vdb. If you specify this parameter, the device must not exist in the guest operating system.
        """
        conn = get_openstack_conn()
        conn.compute.create_volume_attachment(
            server_id, volume_id=volume_id, device=device
        )

    def detach_volume(self, server_id: str, volume_id: str) -> None:
        """
        Detach a volume from a Compute server.

        :param server_id: The UUID of the server.
        :param volume_id: The UUID of the volume to detach.
        """
        conn = get_openstack_conn()
        conn.compute.delete_volume_attachment(server_id, volume_id)
