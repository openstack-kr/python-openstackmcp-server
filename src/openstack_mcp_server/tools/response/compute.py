from pydantic import BaseModel


class Server(BaseModel):
    """A model to represent a Compute server."""

    name: str
    id: str
    status: str
