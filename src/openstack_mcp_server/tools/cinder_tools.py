from ..resources.cinder import (
    Volume,
    VolumeAttachment,
    VolumeAttachResult,
    VolumeCreateResult,
    VolumeDeleteResult,
    VolumeDetachResult,
    VolumeExtendResult,
)
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

    def get_cinder_volumes(self) -> list[Volume]:
        """
        Get the list of Cinder volumes.

        :return: A list of Volume objects representing the volumes.
        """
        conn = get_openstack_conn()

        # List the volumes
        volume_list = []
        for volume in conn.block_storage.volumes():
            attachments = []
            for attachment in volume.attachments or []:
                attachments.append(
                    VolumeAttachment(
                        server_id=attachment.get("server_id"),
                        device=attachment.get("device"),
                        attachment_id=attachment.get("id"),
                    )
                )

            volume_list.append(
                Volume(
                    id=volume.id,
                    name=volume.name,
                    status=volume.status,
                    size=volume.size,
                    volume_type=volume.volume_type,
                    availability_zone=volume.availability_zone,
                    created_at=str(volume.created_at)
                    if volume.created_at
                    else None,
                    is_bootable=volume.is_bootable,
                    is_encrypted=volume.is_encrypted,
                    description=volume.description,
                    attachments=attachments,
                )
            )

        return volume_list

    def get_volume_details(self, volume_id: str) -> Volume:
        """
        Get detailed information about a specific volume.

        :param volume_id: The ID of the volume to get details for
        :return: A Volume object with detailed information
        """
        conn = get_openstack_conn()

        volume = conn.block_storage.get_volume(volume_id)

        attachments = []
        for attachment in volume.attachments or []:
            attachments.append(
                VolumeAttachment(
                    server_id=attachment.get("server_id"),
                    device=attachment.get("device"),
                    attachment_id=attachment.get("id"),
                )
            )

        return Volume(
            id=volume.id,
            name=volume.name,
            status=volume.status,
            size=volume.size,
            volume_type=volume.volume_type,
            availability_zone=volume.availability_zone,
            created_at=str(volume.created_at) if volume.created_at else None,
            is_bootable=volume.is_bootable,
            is_encrypted=volume.is_encrypted,
            description=volume.description,
            attachments=attachments,
        )

    def create_volume(
        self,
        name: str,
        size: int,
        description: str = "",
        volume_type: str = "",
        availability_zone: str = "",
    ) -> VolumeCreateResult:
        """
        Create a new volume.

        :param name: Name for the new volume
        :param size: Size of the volume in GB
        :param description: Optional description for the volume
        :param volume_type: Optional volume type
        :param availability_zone: Optional availability zone
        :return: A VolumeCreateResult object with the created volume and result message
        """
        conn = get_openstack_conn()

        volume_kwargs = {
            "name": name,
            "size": size,
        }

        if description:
            volume_kwargs["description"] = description
        if volume_type:
            volume_kwargs["volume_type"] = volume_type
        if availability_zone:
            volume_kwargs["availability_zone"] = availability_zone

        volume = conn.block_storage.create_volume(**volume_kwargs)

        volume_obj = Volume(
            id=volume.id,
            name=volume.name,
            status=volume.status,
            size=volume.size,
            volume_type=volume.volume_type,
            availability_zone=volume.availability_zone,
            created_at=str(volume.created_at) if volume.created_at else None,
            is_bootable=volume.is_bootable,
            is_encrypted=volume.is_encrypted,
            description=volume.description,
            attachments=[],
        )

        return VolumeCreateResult(
            volume=volume_obj, message="Volume creation initiated successfully"
        )

    def delete_volume(
        self, volume_id: str, force: bool = False
    ) -> VolumeDeleteResult:
        """
        Delete a volume.

        :param volume_id: The ID of the volume to delete
        :param force: Whether to force delete the volume
        :return: A VolumeDeleteResult object with deletion details
        """
        conn = get_openstack_conn()

        # Get volume info before deletion
        volume = conn.block_storage.get_volume(volume_id)
        volume_name = volume.name

        # Delete the volume
        conn.block_storage.delete_volume(volume_id, force=force)

        return VolumeDeleteResult(
            volume_id=volume_id,
            volume_name=volume_name,
            force=force,
            message="Volume deletion initiated successfully",
        )

    def extend_volume(
        self, volume_id: str, new_size: int
    ) -> VolumeExtendResult:
        """
        Extend a volume to a new size.

        :param volume_id: The ID of the volume to extend
        :param new_size: The new size in GB (must be larger than current size)
        :return: A VolumeExtendResult object with extension details
        """
        conn = get_openstack_conn()

        # Get current volume info
        volume = conn.block_storage.get_volume(volume_id)
        current_size = volume.size

        if new_size <= current_size:
            raise ValueError(
                f"New size ({new_size} GB) must be larger than current size ({current_size} GB)"
            )

        # Extend the volume
        conn.block_storage.extend_volume(volume_id, new_size)

        return VolumeExtendResult(
            volume_id=volume_id,
            volume_name=volume.name,
            current_size=current_size,
            new_size=new_size,
            message="Volume extension initiated successfully",
        )

    def attach_volume_to_server(
        self, server_id: str, volume_id: str, device: str = ""
    ) -> VolumeAttachResult:
        """
        Attach a volume to a server instance.

        :param server_id: The ID of the server to attach to
        :param volume_id: The ID of the volume to attach
        :param device: Optional device name (e.g., /dev/vdb)
        :return: A VolumeAttachResult object with attachment details
        """
        conn = get_openstack_conn()

        # Get server and volume info
        server = conn.compute.get_server(server_id)
        volume = conn.block_storage.get_volume(volume_id)

        # Prepare attachment parameters
        attach_kwargs = {
            "server": server_id,
            "volume": volume_id,
        }

        if device:
            attach_kwargs["device"] = device

        # Attach the volume
        attachment = conn.compute.create_volume_attachment(**attach_kwargs)

        return VolumeAttachResult(
            server_id=server_id,
            server_name=server.name,
            volume_id=volume_id,
            volume_name=volume.name,
            device=device if device else None,
            attachment_id=attachment.id,
            message="Volume attachment initiated successfully",
        )

    def detach_volume_from_server(
        self, server_id: str, volume_id: str
    ) -> VolumeDetachResult:
        """
        Detach a volume from a server instance.

        :param server_id: The ID of the server to detach from
        :param volume_id: The ID of the volume to detach
        :return: A VolumeDetachResult object with detachment details
        """
        conn = get_openstack_conn()

        # Get server and volume info
        server = conn.compute.get_server(server_id)
        volume = conn.block_storage.get_volume(volume_id)

        # Detach the volume
        conn.compute.delete_volume_attachment(volume_id, server_id)

        return VolumeDetachResult(
            server_id=server_id,
            server_name=server.name,
            volume_id=volume_id,
            volume_name=volume.name,
            message="Volume detachment initiated successfully",
        )
