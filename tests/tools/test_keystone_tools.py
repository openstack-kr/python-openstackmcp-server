import pytest
from unittest.mock import Mock
from openstack import exceptions
from openstack_mcp_server.tools.keystone_tools import KeystoneTools, Region


class TestKeystoneTools:
    """Test cases for KeystoneTools class."""

    def get_keystone_tools(self) -> KeystoneTools:
        """Get an instance of KeystoneTools."""
        return KeystoneTools()
    
    def test_get_regions_success(self, mock_get_openstack_conn_keystone):
        """Test getting keystone regions successfully."""
        mock_conn = mock_get_openstack_conn_keystone
        
        # Arrange
        # Create mock region objects
        mock_region1 = Mock()
        mock_region1.id = "RegionOne"
        mock_region1.description = "Region One description"

        mock_region2 = Mock()
        mock_region2.id = "RegionTwo"
        mock_region2.description = "Region Two description"
                
        # Configure mock identity.regions()
        mock_conn.identity.regions.return_value = [mock_region1, mock_region2]
        
        # Act
        keystone_tools = self.get_keystone_tools()
        result = keystone_tools.get_regions()

        # Assert
        assert result == [Region(id="RegionOne", description="Region One description"),
                          Region(id="RegionTwo", description="Region Two description")]

        # Verify mock calls
        mock_conn.identity.regions.assert_called_once()

    def test_get_regions_empty_list(self, mock_get_openstack_conn_keystone):
        """Test getting keystone regions when there are no regions."""
        mock_conn = mock_get_openstack_conn_keystone
        
        # Arrange
        mock_conn.identity.regions.return_value = []
        
        # Act
        keystone_tools = self.get_keystone_tools()
        result = keystone_tools.get_regions()

        # Assert
        assert result == []

        # Verify mock calls
        mock_conn.identity.regions.assert_called_once()

    def test_create_region_success(self, mock_get_openstack_conn_keystone):
        """Test creating a keystone region successfully."""
        mock_conn = mock_get_openstack_conn_keystone
        
        # Arrange
        mock_region = Mock()
        mock_region.id = "RegionOne"
        mock_region.description = "Region One description"
        
        mock_conn.identity.create_region.return_value = mock_region
        
        # Act
        keystone_tools = self.get_keystone_tools()
        result = keystone_tools.create_region(id="RegionOne", description="Region One description")
        
        # Assert
        assert result == Region(id="RegionOne", description="Region One description")

        # Verify mock calls
        mock_conn.identity.create_region.assert_called_once_with(id="RegionOne", description="Region One description")
    
    def test_create_region_without_description(self, mock_get_openstack_conn_keystone):
        """Test creating a keystone region without a description."""
        mock_conn = mock_get_openstack_conn_keystone
        
        # Arrange
        mock_region = Mock()
        mock_region.id = "RegionOne"
        mock_region.description = None
        
        mock_conn.identity.create_region.return_value = mock_region
        
        # Act
        keystone_tools = self.get_keystone_tools()
        result = keystone_tools.create_region(id="RegionOne")
        
        # Assert
        assert result == Region(id="RegionOne")

    def test_create_region_invalid_id_format(self, mock_get_openstack_conn_keystone):
        """Test creating a keystone region with an invalid ID format."""
        mock_conn = mock_get_openstack_conn_keystone
        
        # Arrange
        mock_conn.identity.create_region.side_effect = exceptions.BadRequestException(
            "Invalid input for field 'id': Expected string, got integer"
        )
        
        # Act
        keystone_tools = self.get_keystone_tools()
        with pytest.raises(exceptions.BadRequestException, match="Invalid input for field 'id': Expected string, got integer"):
            keystone_tools.create_region(id=1, description="Region One description")
        
        # Assert
        mock_conn.identity.create_region.assert_called_once_with(id=1, description="Region One description") 
    