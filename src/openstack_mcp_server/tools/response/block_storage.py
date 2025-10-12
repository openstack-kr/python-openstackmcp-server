from pydantic import BaseModel


class VolumeAttachment(BaseModel):
    server_id: str | None = None
    device: str | None = None
    attachment_id: str | None = None


class Volume(BaseModel):
    id: str
    name: str | None = None
    status: str
    size: int
    volume_type: str | None = None
    availability_zone: str | None = None
    created_at: str
    is_bootable: bool | None = None
    is_encrypted: bool | None = None
    description: str | None = None
    attachments: list[VolumeAttachment] = []


class ConnectionInfo(BaseModel):
    access_mode: str | None = None
    cacheable: bool | None = None
    driver_volume_type: str | None = None
    encrypted: bool | None = None
    qos_specs: str | None = None
    target_discovered: bool | None = None
    target_iqn: str | None = None
    target_lun: int | None = None
    target_portal: str | None = None


class Attachment(BaseModel):
    id: str
    instance: str
    volume_id: str
    attached_at: str | None = None
    detached_at: str | None = None
    attach_mode: str | None = None
    connection_info: ConnectionInfo | None = None
    connector: str | None = None


class AttachmentSummary(BaseModel):
    id: str
    instance: str
    volume_id: str
    status: str
