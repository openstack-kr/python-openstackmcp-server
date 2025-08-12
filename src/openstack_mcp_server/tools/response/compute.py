from pydantic import BaseModel, ConfigDict, Field


class Flavor(BaseModel):
    id: str | None = Field(default=None, exclude=True)
    name: str = Field(validation_alias="original_name")
    model_config = ConfigDict(validate_by_name=True)


class Image(BaseModel):
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
    flavor: Flavor | None = None
    image: Image | None = None
    addresses: dict[str, list[ServerIp]] | None = None
    key_name: str | None = None
    security_groups: list[ServerSecurityGroup] | None = None
