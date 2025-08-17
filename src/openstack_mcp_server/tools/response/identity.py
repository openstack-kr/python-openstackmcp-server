from pydantic import BaseModel


# NOTE: In openstacksdk, all of the fields are optional.
# In this case, we are only using description field as optional.
class Region(BaseModel):
    id: str
    description: str | None = None


class Domain(BaseModel):
    id: str
    name: str
    description: str | None = None
    is_enabled: bool | None = None
