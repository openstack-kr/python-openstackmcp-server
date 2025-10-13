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
    name: str | None = None
    status: str | None = None
    description: str | None = None
    project_id: str | None = None
    network_id: str | None = None
    cidr: str | None = None
    ip_version: int | None = None
    gateway_ip: str | None = None
    is_dhcp_enabled: bool | None = None
    allocation_pools: list[dict] | None = None
    dns_nameservers: list[str] | None = None
    host_routes: list[dict] | None = None


class Port(BaseModel):
    id: str
    name: str | None = None
    status: str | None = None
    description: str | None = None
    project_id: str | None = None
    network_id: str | None = None
    is_admin_state_up: bool | None = None
    device_id: str | None = None
    device_owner: str | None = None
    mac_address: str | None = None
    fixed_ips: list[dict] | None = None
    security_group_ids: list[str] | None = None


class Router(BaseModel):
    id: str
    name: str | None = None
    status: str | None = None
    description: str | None = None
    project_id: str | None = None
    is_admin_state_up: bool | None = None
    external_gateway_info: dict | None = None
    is_distributed: bool | None = None
    is_ha: bool | None = None
    routes: list[dict] | None = None


class RouterInterface(BaseModel):
    router_id: str
    port_id: str
    subnet_id: str | None = None


class SecurityGroup(BaseModel):
    id: str
    name: str | None = None
    status: str | None = None
    description: str | None = None
    project_id: str | None = None
    security_group_rule_ids: list[str] | None = None


class SecurityGroupRule(BaseModel):
    id: str
    name: str | None = None
    status: str | None = None
    description: str | None = None
    project_id: str | None = None
    direction: str | None = None
    ethertype: str | None = None
    protocol: str | None = None
    port_range_min: int | None = None
    port_range_max: int | None = None
    remote_ip_prefix: str | None = None
    remote_group_id: str | None = None
    security_group_id: str | None = None


class FloatingIP(BaseModel):
    id: str
    name: str | None = None
    status: str | None = None
    description: str | None = None
    project_id: str | None = None
    floating_ip_address: str | None = None
    floating_network_id: str | None = None
    fixed_ip_address: str | None = None
    port_id: str | None = None
    router_id: str | None = None
