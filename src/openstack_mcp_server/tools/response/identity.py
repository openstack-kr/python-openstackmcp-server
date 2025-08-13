from pydantic import BaseModel


# NOTE: In openstacksdk, all of the fields are optional.
# In this case, we are only using description field as optional.
class Region(BaseModel):
    id: str
    description: str = ""


class Domain(BaseModel):
    id: str
    name: str
    description: str = ""
    is_enabled: bool = False
