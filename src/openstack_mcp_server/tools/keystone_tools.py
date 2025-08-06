from fastmcp import FastMCP
from pydantic import BaseModel
from .base import get_openstack_conn

# NOTE: In openstacksdk, all of the fields are optional.
# In this case, we are only using description field as optional.
class Region(BaseModel):
    id: str
    description: str | None = ""

class KeystoneTools:
    """
    A class to encapsulate Keystone-related tools and utilities.
    """

    def register_tools(self, mcp: FastMCP):
        """
        Register Keystone-related tools with the FastMCP instance.
        """

        mcp.tool()(self.get_regions)
        mcp.tool()(self.create_region)
        mcp.tool()(self.delete_region)
        mcp.tool()(self.update_region)

    def get_regions(self) -> list[Region]:
        """
        Get the list of Keystone regions.
        
        :return: A list of Region objects representing the regions.
        """
        conn = get_openstack_conn()

        region_list = []
        for region in conn.identity.regions():
            region_list.append(Region(id=region.id, description=region.description))
            
        return region_list
    
    def create_region(self, id: str, description: str = "") -> Region:
        """
        Create a new region.
        
        :param id: The ID of the region. (required)
        :param description: The description of the region. It can be None. (optional)
        
        :return: The created Region object.
        """
        conn = get_openstack_conn()

        region = conn.identity.create_region(id=id, description=description)

        return Region(id=region.id, description=region.description)
    
    def delete_region(self, id: str) -> str:
        """
        Delete a region.
        
        :param id: The ID of the region. (required)
        
        :return: A message indicating the region was deleted successfully.
        """
        conn = get_openstack_conn()
        
        # ignore_missing is set to False to raise an exception if the region does not exist.
        conn.identity.delete_region(region=id, ignore_missing=False)
        
        return f"Region {id} deleted successfully."
