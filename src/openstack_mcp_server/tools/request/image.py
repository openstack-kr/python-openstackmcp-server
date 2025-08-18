from __future__ import annotations

from pydantic import BaseModel, Field


class CreateImage(BaseModel):
    """OpenStack Glance Image Creation Request Pydantic Model"""

    id: str | None = Field(default=None)
    volume: str | None = Field(default=None)
    name: str | None = Field(default=None)
    container: str | None = Field(default=None)
    container_format: str | None = Field(default=None)
    allow_duplicates: bool = Field(default=False)
    disk_format: str | None = Field(default=None)
    min_disk: int | None = Field(default=None)
    min_ram: int | None = Field(default=None)
    tags: list[str] | None = Field(default=[])
    protected: bool | None = Field(default=False)
    visibility: str | None = Field(default="public")
    import_options: ImportOptions | None = Field(default=None)

    class ImportOptions(BaseModel):
        """Options for image import"""

        import_method: str | None = Field(default=None)
        stores: list[str] | None = Field(default=None)
        uri: str | None = Field(default=None)
        glance_region: str | None = Field(default=None)
        glance_image_id: str | None = Field(default=None)
        glance_service_interface: str | None = Field(default=None)
