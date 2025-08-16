from pydantic import BaseModel, ConfigDict, Field


class OwnerSpecified(BaseModel):
    """Owner specified metadata for OpenStack images"""

    openstack_object: str | None = Field(
        default=None,
        alias="owner_specified.openstack.object",
    )
    openstack_sha256: str | None = Field(
        default=None,
        alias="'owner_specified.openstack.sha256'",
    )
    openstack_md5: str | None = Field(
        default=None,
        alias="'owner_specified.openstack.md5'",
    )

    model_config = ConfigDict(validate_by_name=True)


class Image(BaseModel):
    """OpenStack Glance Image Pydantic Model"""

    id: str
    name: str | None = Field(default=None)
    checksum: str | None = Field(default=None)
    container_format: str | None = Field(default=None)
    disk_format: str | None = Field(default=None)
    file: str | None = Field(default=None)
    min_disk: int | None = Field(default=None)
    min_ram: int | None = Field(default=None)
    os_hash_algo: str | None = Field(default=None)
    os_hash_value: str | None = Field(default=None)
    size: int | None = Field(default=None)
    virtual_size: int | None = Field(default=None)
    owner: str | None = Field(default=None)
    visibility: str | None = Field(default=None)
    hw_rng_model: str | None = Field(default=None)
    status: str | None = Field(default=None)
    schema_: str | None = Field(default=None, alias="schema")
    protected: bool | None = Field(default=None)
    os_hidden: bool | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    properties: OwnerSpecified | None = Field(default=None)
    model_config = ConfigDict(validate_by_name=True)

    created_at: str | None = Field(default=None)
    updated_at: str | None = Field(default=None)
