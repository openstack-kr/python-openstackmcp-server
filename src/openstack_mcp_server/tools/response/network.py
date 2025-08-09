from pydantic import BaseModel


class Network(BaseModel):
    id: str
    name: str
    status: str
    description: str | None = None
    is_admin_state_up: bool = True
    is_shared: bool = False
    mtu: int | None = None
    provider_network_type: str | None = None
    provider_physical_network: str | None = None
    provider_segmentation_id: int | None = None
    project_id: str | None = None


class Subnet(BaseModel):
    id: str
    name: str
    status: str


class Port(BaseModel):
    id: str
    name: str
    status: str


class Router(BaseModel):
    id: str
    name: str
    status: str


class SecurityGroup(BaseModel):
    id: str
    name: str
    status: str


class SecurityGroupRule(BaseModel):
    id: str
    name: str
    status: str


class FloatingIP(BaseModel):
    id: str
    name: str
    status: str
