from fastmcp import FastMCP

from .base import get_openstack_conn
from .response.block_storage import (
    Attachment,
    ConnectionInfo,
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

        mcp.tool()(self.get_attachment_details)
        mcp.tool()(self.get_attachments)

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
                        attachment_id=attachment.get("attachment_id"),
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
                    attachment_id=attachment.get("attachment_id"),
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
        image: str | None = None,
    ) -> Volume:
        """
        Create a new volume.

        :param name: Name for the new volume
        :param size: Size of the volume in GB
        :param description: Optional description for the volume
        :param volume_type: Optional volume type
        :param availability_zone: Optional availability zone
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

    def get_attachment_details(self, attachment_id: str) -> Attachment:
        """
        Get detailed information about a specific attachment.

        :param attachment_id: The ID of the attachment to get details for
        :return: An Attachment object with detailed information
        """
        conn = get_openstack_conn()

        attachment = conn.block_storage.get_attachment(attachment_id)

        # NOTE: We exclude the auth_* fields for security reasons
        connection_info = attachment.connection_info
        filtered_connection_info = ConnectionInfo(
            access_mode=connection_info.get("access_mode"),
            cacheable=connection_info.get("cacheable"),
            driver_volume_type=connection_info.get("driver_volume_type"),
            encrypted=connection_info.get("encrypted"),
            qos_specs=connection_info.get("qos_specs"),
            target_discovered=connection_info.get("target_discovered"),
            target_iqn=connection_info.get("target_iqn"),
            target_lun=connection_info.get("target_lun"),
            target_portal=connection_info.get("target_portal"),
        )

        params = {
            "id": attachment.id,
            "instance": attachment.instance,
            "volume_id": attachment.volume_id,
            "attached_at": attachment.attached_at,
            "detached_at": attachment.detached_at,
            "attach_mode": attachment.attach_mode,
            "connection_info": filtered_connection_info,
            "connector": attachment.connector,
        }

        return Attachment(**params)

    def get_attachments(
        self,
        volume_id: str | None = None,
        instance: str | None = None,
    ) -> list[Attachment]:
        """
        Get the list of attachments.

        :param volume_id: The ID of the volume.
        :param instance: The ID of the instance.
        :return: A list of Attachment objects.
        """
        conn = get_openstack_conn()

        filter = {}
        if volume_id:
            filter["volume_id"] = volume_id
        if instance:
            filter["instance"] = instance

        attachments = []
        for attachment in conn.block_storage.attachments(**filter):
            attachments.append(
                Attachment(
                    id=attachment.id,
                    instance=attachment.instance,
                    volume_id=attachment.volume_id,
                    status=attachment.status,
                    connection_info=attachment.connection_info,
                    attach_mode=attachment.attach_mode,
                    connector=attachment.connector,
                    attached_at=attachment.attached_at,
                    detached_at=attachment.detached_at,
                )
            )

        return attachments
