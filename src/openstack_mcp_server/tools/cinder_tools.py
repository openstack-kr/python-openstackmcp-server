from .base import get_openstack_conn
from fastmcp import FastMCP


class CinderTools:
    """
    A class to encapsulate Cinder-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Cinder-related tools with the FastMCP instance.
        """
        mcp.tool()(self.get_cinder_volumes)
        mcp.tool()(self.get_volume_details)
        mcp.tool()(self.create_volume)
        mcp.tool()(self.delete_volume)
        mcp.tool()(self.extend_volume)
        mcp.tool()(self.attach_volume_to_server)
        mcp.tool()(self.detach_volume_from_server)

    def get_cinder_volumes(self) -> str:
        """
        Get the list of Cinder volumes by invoking the registered tool.

        :return: A string containing the names, IDs, and statuses of the volumes.
        """
        # Initialize connection
        conn = get_openstack_conn()

        # List the volumes
        volume_list = []
        for volume in conn.block_storage.volumes():
            volume_list.append(
                f"{volume.name} ({volume.id}) - Status: {volume.status}"
            )

        return "\n".join(volume_list)

    def get_volume_details(self, volume_id: str) -> str:
        """
        Get detailed information about a specific volume.

        :param volume_id: The ID of the volume to get details for
        :return: A string containing detailed volume information
        """
        conn = get_openstack_conn()
        
        try:
            volume = conn.block_storage.get_volume(volume_id)
            
            details = [
                f"Volume Details:",
                f"  Name: {volume.name or 'N/A'}",
                f"  ID: {volume.id}",
                f"  Status: {volume.status}",
                f"  Size: {volume.size} GB",
                f"  Volume Type: {volume.volume_type or 'N/A'}",
                f"  Availability Zone: {volume.availability_zone or 'N/A'}",
                f"  Created At: {volume.created_at}",
                f"  Bootable: {volume.is_bootable}",
                f"  Encrypted: {volume.is_encrypted}",
                f"  Attachments: {len(volume.attachments)} attachment(s)",
            ]
            
            # Add attachment details if any
            if volume.attachments:
                details.append("  Attachment Details:")
                for attachment in volume.attachments:
                    details.append(f"    - Server ID: {attachment.get('server_id', 'N/A')}")
                    details.append(f"      Device: {attachment.get('device', 'N/A')}")
            
            return "\n".join(details)
            
        except Exception as e:
            return f"Error retrieving volume details: {str(e)}"

    def create_volume(self, name: str, size: int, description: str = "", 
                     volume_type: str = "", availability_zone: str = "") -> str:
        """
        Create a new volume.

        :param name: Name for the new volume
        :param size: Size of the volume in GB
        :param description: Optional description for the volume
        :param volume_type: Optional volume type
        :param availability_zone: Optional availability zone
        :return: A string containing the creation result
        """
        conn = get_openstack_conn()
        
        try:
            volume_kwargs = {
                'name': name,
                'size': size,
            }
            
            if description:
                volume_kwargs['description'] = description
            if volume_type:
                volume_kwargs['volume_type'] = volume_type
            if availability_zone:
                volume_kwargs['availability_zone'] = availability_zone
            
            volume = conn.block_storage.create_volume(**volume_kwargs)
            
            return (f"Volume creation initiated:\n"
                   f"  Name: {volume.name}\n"
                   f"  ID: {volume.id}\n"
                   f"  Size: {volume.size} GB\n"
                   f"  Status: {volume.status}")
                   
        except Exception as e:
            return f"Error creating volume: {str(e)}"

    def delete_volume(self, volume_id: str, force: bool = False) -> str:
        """
        Delete a volume.

        :param volume_id: The ID of the volume to delete
        :param force: Whether to force delete the volume
        :return: A string containing the deletion result
        """
        conn = get_openstack_conn()
        
        try:
            # Get volume info before deletion
            volume = conn.block_storage.get_volume(volume_id)
            volume_name = volume.name or "Unnamed"
            
            # Delete the volume
            conn.block_storage.delete_volume(volume_id, force=force)
            
            return (f"Volume deletion initiated:\n"
                   f"  Name: {volume_name}\n"
                   f"  ID: {volume_id}\n"
                   f"  Force: {force}")
                   
        except Exception as e:
            return f"Error deleting volume: {str(e)}"

    def extend_volume(self, volume_id: str, new_size: int) -> str:
        """
        Extend a volume to a new size.

        :param volume_id: The ID of the volume to extend
        :param new_size: The new size in GB (must be larger than current size)
        :return: A string containing the extension result
        """
        conn = get_openstack_conn()
        
        try:
            # Get current volume info
            volume = conn.block_storage.get_volume(volume_id)
            current_size = volume.size
            
            if new_size <= current_size:
                return f"Error: New size ({new_size} GB) must be larger than current size ({current_size} GB)"
            
            # Extend the volume
            conn.block_storage.extend_volume(volume_id, new_size)
            
            return (f"Volume extension initiated:\n"
                   f"  Name: {volume.name or 'Unnamed'}\n"
                   f"  ID: {volume_id}\n"
                   f"  Current Size: {current_size} GB\n"
                   f"  New Size: {new_size} GB")
                   
        except Exception as e:
            return f"Error extending volume: {str(e)}"

    def attach_volume_to_server(self, server_id: str, volume_id: str, device: str = "") -> str:
        """
        Attach a volume to a server instance.

        :param server_id: The ID of the server to attach to
        :param volume_id: The ID of the volume to attach
        :param device: Optional device name (e.g., /dev/vdb)
        :return: A string containing the attachment result
        """
        conn = get_openstack_conn()
        
        try:
            # Get server and volume info
            server = conn.compute.get_server(server_id)
            volume = conn.block_storage.get_volume(volume_id)
            
            # Prepare attachment parameters
            attach_kwargs = {
                'server': server_id,
                'volume': volume_id,
            }
            
            if device:
                attach_kwargs['device'] = device
            
            # Attach the volume
            attachment = conn.compute.create_volume_attachment(**attach_kwargs)
            
            return (f"Volume attachment initiated:\n"
                   f"  Server: {server.name} ({server_id})\n"
                   f"  Volume: {volume.name or 'Unnamed'} ({volume_id})\n"
                   f"  Device: {device or 'Auto-assigned'}\n"
                   f"  Attachment ID: {attachment.id}")
                   
        except Exception as e:
            return f"Error attaching volume: {str(e)}"

    def detach_volume_from_server(self, server_id: str, volume_id: str) -> str:
        """
        Detach a volume from a server instance.

        :param server_id: The ID of the server to detach from
        :param volume_id: The ID of the volume to detach
        :return: A string containing the detachment result
        """
        conn = get_openstack_conn()
        
        try:
            # Get server and volume info
            server = conn.compute.get_server(server_id)
            volume = conn.block_storage.get_volume(volume_id)
            
            # Detach the volume
            conn.compute.delete_volume_attachment(volume_id, server_id)
            
            return (f"Volume detachment initiated:\n"
                   f"  Server: {server.name} ({server_id})\n"
                   f"  Volume: {volume.name or 'Unnamed'} ({volume_id})")
                   
        except Exception as e:
            return f"Error detaching volume: {str(e)}"
