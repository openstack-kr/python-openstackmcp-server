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
    created_at: str | None = None
    is_bootable: bool | None = None
    is_encrypted: bool | None = None
    description: str | None = None
    attachments: list[VolumeAttachment] = []


class VolumeCreateResult(BaseModel):
    volume: Volume


class VolumeDeleteResult(BaseModel):
    volume_id: str
    volume_name: str | None = None
    force: bool


class VolumeExtendResult(BaseModel):
    volume_id: str
    volume_name: str | None = None
    current_size: int
    new_size: int
