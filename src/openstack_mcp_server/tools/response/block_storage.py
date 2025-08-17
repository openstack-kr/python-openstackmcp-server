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
