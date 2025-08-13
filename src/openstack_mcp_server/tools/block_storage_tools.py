from fastmcp import FastMCP

from .base import get_openstack_conn
from .response.block_storage import (
    Volume,
    VolumeAttachment,
)


class BlockStorageTools:
    """
    A class to encapsulate Block Storage-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Block Storage-related tools with the FastMCP instance.
        """
        mcp.tool()(self.get_volumes)
        mcp.tool()(self.get_volume_details)
        mcp.tool()(self.create_volume)
        mcp.tool()(self.delete_volume)
        mcp.tool()(self.extend_volume)

    def get_volumes(self) -> list[Volume]:
        """
        Get the list of Block Storage volumes.

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
                    ),
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
                ),
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
                ),
            )

        return Volume(
            id=volume.id,
            name=volume.name,
            status=volume.status,
            size=volume.size,
            volume_type=volume.volume_type,
            availability_zone=volume.availability_zone,
            created_at=str(volume.created_at),
            is_bootable=volume.is_bootable,
            is_encrypted=volume.is_encrypted,
            description=volume.description,
            attachments=attachments,
        )

    def create_volume(
        self,
        name: str,
        size: int,
        description: str | None = None,
        volume_type: str | None = None,
        availability_zone: str | None = None,
        bootable: bool | None = None,
        image: str | None = None,
    ) -> Volume:
        """
        Create a new volume.

        :param name: Name for the new volume
        :param size: Size of the volume in GB
        :param description: Optional description for the volume
        :param volume_type: Optional volume type
        :param availability_zone: Optional availability zone
        :param bootable: Optional flag to make the volume bootable
        :param image: Optional Image name, ID or object from which to create
        :return: The created Volume object
        """
        conn = get_openstack_conn()

        volume_kwargs = {
            "name": name,
        }

        if description is not None:
            volume_kwargs["description"] = description
        if volume_type is not None:
            volume_kwargs["volume_type"] = volume_type
        if availability_zone is not None:
            volume_kwargs["availability_zone"] = availability_zone

        volume = conn.block_storage.create_volume(
            size=size,
            image=image,
            bootable=bootable,
            **volume_kwargs,
        )

        volume_obj = Volume(
            id=volume.id,
            name=volume.name,
            status=volume.status,
            size=volume.size,
            volume_type=volume.volume_type,
            availability_zone=volume.availability_zone,
            created_at=str(volume.created_at),
            is_bootable=volume.is_bootable,
            is_encrypted=volume.is_encrypted,
            description=volume.description,
            attachments=[],
        )

        return volume_obj

    def delete_volume(self, volume_id: str, force: bool = False) -> None:
        """
        Delete a volume.

        :param volume_id: The ID of the volume to delete
        :param force: Whether to force delete the volume
        :return: None
        """
        conn = get_openstack_conn()

        conn.block_storage.delete_volume(
            volume_id,
            force=force,
            ignore_missing=False,
        )

    def extend_volume(self, volume_id: str, new_size: int) -> None:
        """
        Extend a volume to a new size.

        :param volume_id: The ID of the volume to extend
        :param new_size: The new size in GB (must be larger than current size)
        :return: None
        """
        conn = get_openstack_conn()

        conn.block_storage.extend_volume(volume_id, new_size)
