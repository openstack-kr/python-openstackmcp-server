from pydantic import BaseModel


class Route(BaseModel):
    """Static route for a router."""

    destination: str
    nexthop: str


class ExternalFixedIP(BaseModel):
    """External fixed IP assignment for router gateway."""

    subnet_id: str | None = None
    ip_address: str | None = None


class ExternalGatewayInfo(BaseModel):
    """External gateway information for a router.
    At minimum include `network_id`. Optionally include `enable_snat` and
    `external_fixed_ips`.
    """

    network_id: str
    enable_snat: bool | None = None
    external_fixed_ips: list[ExternalFixedIP] | None = None
