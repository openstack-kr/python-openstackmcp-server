from pydantic import BaseModel, ConfigDict, Field


class ServerFlavor(BaseModel):
    id: str | None = Field(default=None, exclude=True)
    name: str = Field(validation_alias="original_name")
    model_config = ConfigDict(validate_by_name=True)


class ServerImage(BaseModel):
    id: str


class ServerIp(BaseModel):
    addr: str
    version: int
    type: str = Field(validation_alias="OS-EXT-IPS:type")

    model_config = ConfigDict(validate_by_name=True)


class ServerSecurityGroup(BaseModel):
    name: str


class Server(BaseModel):
    id: str
    name: str
    status: str | None = None
    flavor: ServerFlavor | None = None
    image: ServerImage | None = None
    addresses: dict[str, list[ServerIp]] | None = None
    key_name: str | None = None
    security_groups: list[ServerSecurityGroup] | None = None


class Flavor(BaseModel):
    id: str
    name: str
    vcpus: int
    ram: int
    disk: int
    swap: int | None = None
    is_public: bool = Field(validation_alias="os-flavor-access:is_public")

    model_config = ConfigDict(validate_by_name=True)
