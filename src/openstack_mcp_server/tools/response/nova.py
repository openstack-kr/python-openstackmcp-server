from pydantic import BaseModel


class Server(BaseModel):
    """A model to represent a Nova server."""

    name: str
    id: str
    status: str
