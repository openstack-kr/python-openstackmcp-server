import pytest
from unittest.mock import Mock
from openstack import exceptions
from openstack_mcp_server.tools.identity_tools import IdentityTools, Region

class TestIdentityTools:
    """Test cases for IdentityTools class."""

    def get_identity_tools(self) -> IdentityTools:
        """Get an instance of IdentityTools."""
        return IdentityTools()
    
    def test_get_regions_success(self, mock_get_openstack_conn_identity):
        """Test getting identity regions successfully."""
        mock_conn = mock_get_openstack_conn_identity
        
        # Create mock region objects
        mock_region1 = Mock()
        mock_region1.id = "RegionOne"
        mock_region1.description = "Region One description"

        mock_region2 = Mock()
        mock_region2.id = "RegionTwo"
        mock_region2.description = "Region Two description"
        
        # Configure mock region.regions()
        mock_conn.identity.regions.return_value = [mock_region1, mock_region2]

        # Test get_regions()
        identity_tools = self.get_identity_tools()
        result = identity_tools.get_regions()
        
        # Verify results
        assert result == [Region(id="RegionOne", description="Region One description"),
                          Region(id="RegionTwo", description="Region Two description")]

        # Verify mock calls
        mock_conn.identity.regions.assert_called_once()

    def test_get_regions_empty_list(self, mock_get_openstack_conn_identity):
        """Test getting identity regions when there are no regions."""
        mock_conn = mock_get_openstack_conn_identity
        
        # Empty region list
        mock_conn.identity.regions.return_value = []
        
        # Test get_regions()
        identity_tools = self.get_identity_tools()
        result = identity_tools.get_regions()
        
        # Verify results
        assert result == []

        # Verify mock calls
        mock_conn.identity.regions.assert_called_once()

    def test_create_region_success(self, mock_get_openstack_conn_identity):
        """Test creating a identity region successfully."""
        mock_conn = mock_get_openstack_conn_identity
        
        # Create mock region object
        mock_region = Mock()
        mock_region.id = "RegionOne"
        mock_region.description = "Region One description"

        # Configure mock region.create_region()
        mock_conn.identity.create_region.return_value = mock_region

        # Test create_region()
        identity_tools = self.get_identity_tools()
        result = identity_tools.create_region(id="RegionOne", description="Region One description")
        
        # Verify results
        assert result == Region(id="RegionOne", description="Region One description")

        # Verify mock calls
        mock_conn.identity.create_region.assert_called_once_with(id="RegionOne", description="Region One description")
    
    def test_create_region_without_description(self, mock_get_openstack_conn_identity):
        """Test creating a identity region without a description."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock region object
        mock_region = Mock()
        mock_region.id = "RegionOne"
        mock_region.description = None

        # Configure mock region.create_region()
        mock_conn.identity.create_region.return_value = mock_region

        # Test create_region()
        identity_tools = self.get_identity_tools()
        result = identity_tools.create_region(id="RegionOne")

        # Verify results
        assert result == Region(id="RegionOne")

    def test_create_region_invalid_id_format(self, mock_get_openstack_conn_identity):
        """Test creating a identity region with an invalid ID format."""
        mock_conn = mock_get_openstack_conn_identity

        # Configure mock region.create_region() to raise an exception
        mock_conn.identity.create_region.side_effect = exceptions.BadRequestException(
            "Invalid input for field 'id': Expected string, got integer"
        )

        # Test create_region()
        identity_tools = self.get_identity_tools()

        # Verify results
        with pytest.raises(exceptions.BadRequestException, match="Invalid input for field 'id': Expected string, got integer"):
            identity_tools.create_region(id=1, description="Region One description")

        # Verify mock calls
        mock_conn.identity.create_region.assert_called_once_with(id=1, description="Region One description") 
    