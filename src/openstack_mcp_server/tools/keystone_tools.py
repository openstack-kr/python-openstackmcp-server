from fastmcp import FastMCP
from pydantic import BaseModel

from .base import get_openstack_conn

class Region(BaseModel):
    id: str
    description: Optional[str] = None

class KeystoneTools:
    """
    A class to encapsulate Keystone-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Keystone-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_regions)

    def get_regions(self) -> list[Region]:
        """
        Get the list of Keystone regions.
        
        :return: A list of Region objects representing the regions.
        """
        # Initialize connection
        conn = get_openstack_conn()

        # List the regions
        region_list = []
        for region in conn.identity.regions():
            region_list.append(Region(id=region.id, name=region.name, description=region.description))
            
        return region_list
    
    