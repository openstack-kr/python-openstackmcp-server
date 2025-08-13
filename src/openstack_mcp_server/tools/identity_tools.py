from fastmcp import FastMCP

from .base import get_openstack_conn
from .response.identity import Domain, Region


class IdentityTools:
    """
    A class to encapsulate Identity-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Identity-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_regions)
        mcp.tool()(self.get_region)
        mcp.tool()(self.create_region)
        mcp.tool()(self.delete_region)
        mcp.tool()(self.update_region)

        mcp.tool()(self.get_domains)
        mcp.tool()(self.get_domain)

    def get_regions(self) -> list[Region]:
        """
        Get the list of Identity regions.

        :return: A list of Region objects representing the regions.
        """
        conn = get_openstack_conn()

        region_list = []
        for region in conn.identity.regions():
            region_list.append(
                Region(id=region.id, description=region.description),
            )

        return region_list

    def get_region(self, id: str) -> Region:
        """
        Get a region.

        :param id: The ID of the region. (required)

        :return: The Region object.
        """
        conn = get_openstack_conn()

        region = conn.identity.get_region(region=id)

        return Region(id=region.id, description=region.description)

    def create_region(self, id: str, description: str = "") -> Region:
        """
        Create a new region.

        :param id: The ID of the region. (required)
        :param description: The description of the region. (optional)

        :return: The created Region object.
        """
        conn = get_openstack_conn()

        region = conn.identity.create_region(id=id, description=description)

        return Region(id=region.id, description=region.description)

    def delete_region(self, id: str) -> None:
        """
        Delete a region.

        :param id: The ID of the region. (required)

        :return: None
        """
        conn = get_openstack_conn()

        # ignore_missing is set to False to raise an exception if the region does not exist.
        conn.identity.delete_region(region=id, ignore_missing=False)

        return None

    def update_region(self, id: str, description: str = "") -> Region:
        """
        Update a region.

        :param id: The ID of the region. (required)
        :param description: The string description of the region. (optional)

        :return: The updated Region object.
        """
        conn = get_openstack_conn()

        updated_region = conn.identity.update_region(
            region=id,
            description=description,
        )

        return Region(
            id=updated_region.id,
            description=updated_region.description,
        )

    def get_domains(self) -> list[Domain]:
        """
        Get the list of Identity domains.

        :return: A list of Domain objects representing the domains.
        """
        conn = get_openstack_conn()

        domain_list = []
        for domain in conn.identity.domains():
            domain_list.append(
                Domain(
                    id=domain.id,
                    name=domain.name,
                    description=domain.description,
                    is_enabled=domain.is_enabled,
                ),
            )
        return domain_list

    def get_domain(self, id: str) -> Domain:
        """
        Get a domain.

        :param id: The ID of the domain. (required)

        :return: The Domain object.
        """
        conn = get_openstack_conn()

        domain = conn.identity.get_domain(domain=id)

        return Domain(
            id=domain.id,
            name=domain.name,
            description=domain.description,
            is_enabled=domain.is_enabled,
        )
