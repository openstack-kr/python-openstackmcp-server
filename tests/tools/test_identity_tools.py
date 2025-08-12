from unittest.mock import Mock

import pytest

from openstack import exceptions

from openstack_mcp_server.tools.identity_tools import IdentityTools
from openstack_mcp_server.tools.response.identity import Region, Domain


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
        assert result == [
            Region(id="RegionOne", description="Region One description"),
            Region(id="RegionTwo", description="Region Two description"),
        ]

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
        result = identity_tools.create_region(
            id="RegionOne",
            description="Region One description",
        )

        # Verify results
        assert result == Region(
            id="RegionOne",
            description="Region One description",
        )

        # Verify mock calls
        mock_conn.identity.create_region.assert_called_once_with(
            id="RegionOne",
            description="Region One description",
        )

    def test_create_region_without_description(
        self,
        mock_get_openstack_conn_identity,
    ):
        """Test creating a identity region without a description."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock region object
        mock_region = Mock()
        mock_region.id = "RegionOne"
        mock_region.description = ""

        # Configure mock region.create_region()
        mock_conn.identity.create_region.return_value = mock_region

        # Test create_region()
        identity_tools = self.get_identity_tools()
        result = identity_tools.create_region(id="RegionOne")

        # Verify results
        assert result == Region(id="RegionOne")

    def test_create_region_invalid_id_format(
        self,
        mock_get_openstack_conn_identity,
    ):
        """Test creating a identity region with an invalid ID format."""
        mock_conn = mock_get_openstack_conn_identity

        # Configure mock region.create_region() to raise an exception
        mock_conn.identity.create_region.side_effect = (
            exceptions.BadRequestException(
                "Invalid input for field 'id': Expected string, got integer",
            )
        )

        # Test create_region()
        identity_tools = self.get_identity_tools()

        # Verify results
        with pytest.raises(
            exceptions.BadRequestException,
            match="Invalid input for field 'id': Expected string, got integer",
        ):
            identity_tools.create_region(
                id=1,
                description="Region One description",
            )

        # Verify mock calls
        mock_conn.identity.create_region.assert_called_once_with(
            id=1,
            description="Region One description",
        )

    def test_delete_region_success(self, mock_get_openstack_conn_identity):
        """Test deleting a identity region successfully."""
        mock_conn = mock_get_openstack_conn_identity

        # Test delete_region()
        identity_tools = self.get_identity_tools()
        result = identity_tools.delete_region(id="RegionOne")

        # Verify results
        assert result is None

        # Verify mock calls
        mock_conn.identity.delete_region.assert_called_once_with(
            region="RegionOne",
            ignore_missing=False,
        )

    def test_delete_region_not_found(self, mock_get_openstack_conn_identity):
        """Test deleting a identity region that does not exist."""
        mock_conn = mock_get_openstack_conn_identity

        # Configure mock to raise NotFoundException
        mock_conn.identity.delete_region.side_effect = (
            exceptions.NotFoundException(
                "Region 'RegionOne' not found",
            )
        )

        # Test delete_region()
        identity_tools = self.get_identity_tools()

        # Verify exception is raised
        with pytest.raises(
            exceptions.NotFoundException,
            match="Region 'RegionOne' not found",
        ):
            identity_tools.delete_region(id="RegionOne")

        # Verify mock calls
        mock_conn.identity.delete_region.assert_called_once_with(
            region="RegionOne",
            ignore_missing=False,
        )

    def test_update_region_success(self, mock_get_openstack_conn_identity):
        """Test updating a identity region successfully."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock region object
        mock_region = Mock()
        mock_region.id = "RegionOne"
        mock_region.description = "Region One description"

        # Configure mock region.update_region()
        mock_conn.identity.update_region.return_value = mock_region

        # Test update_region()
        identity_tools = self.get_identity_tools()
        result = identity_tools.update_region(
            id="RegionOne",
            description="Region One description",
        )

        # Verify results
        assert result == Region(
            id="RegionOne",
            description="Region One description",
        )

        # Verify mock calls
        mock_conn.identity.update_region.assert_called_once_with(
            region="RegionOne",
            description="Region One description",
        )

    def test_update_region_without_description(
        self,
        mock_get_openstack_conn_identity,
    ):
        """Test updating a identity region without a description."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock region object
        mock_region = Mock()
        mock_region.id = "RegionOne"
        mock_region.description = ""

        # Configure mock region.update_region()
        mock_conn.identity.update_region.return_value = mock_region

        # Test update_region()
        identity_tools = self.get_identity_tools()
        result = identity_tools.update_region(id="RegionOne")

        # Verify results
        assert result == Region(id="RegionOne")

        # Verify mock calls
        mock_conn.identity.update_region.assert_called_once_with(
            region="RegionOne",
            description="",
        )

    def test_update_region_invalid_id_format(
        self,
        mock_get_openstack_conn_identity,
    ):
        """Test updating a identity region with an invalid ID format."""
        mock_conn = mock_get_openstack_conn_identity

        # Configure mock region.update_region() to raise an exception
        mock_conn.identity.update_region.side_effect = (
            exceptions.BadRequestException(
                "Invalid input for field 'id': Expected string, got integer",
            )
        )

        # Test update_region()
        identity_tools = self.get_identity_tools()

        # Verify exception is raised
        with pytest.raises(
            exceptions.BadRequestException,
            match="Invalid input for field 'id': Expected string, got integer",
        ):
            identity_tools.update_region(
                id=1,
                description="Region One description",
            )

        # Verify mock calls
        mock_conn.identity.update_region.assert_called_once_with(
            region=1,
            description="Region One description",
        )

    def test_get_region_success(self, mock_get_openstack_conn_identity):
        """Test getting a identity region successfully."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock region object
        mock_region = Mock()
        mock_region.id = "RegionOne"
        mock_region.description = "Region One description"

        # Configure mock region.get_region()
        mock_conn.identity.get_region.return_value = mock_region

        # Test get_region()
        identity_tools = self.get_identity_tools()
        result = identity_tools.get_region(id="RegionOne")

        # Verify results
        assert result == Region(
            id="RegionOne",
            description="Region One description",
        )

        # Verify mock calls
        mock_conn.identity.get_region.assert_called_once_with(
            region="RegionOne",
        )

    def test_get_region_not_found(self, mock_get_openstack_conn_identity):
        """Test getting a identity region that does not exist."""
        mock_conn = mock_get_openstack_conn_identity

        # Configure mock to raise NotFoundException
        mock_conn.identity.get_region.side_effect = (
            exceptions.NotFoundException(
                "Region 'RegionOne' not found",
            )
        )

        # Test get_region()
        identity_tools = self.get_identity_tools()

        # Verify exception is raised
        with pytest.raises(
            exceptions.NotFoundException,
            match="Region 'RegionOne' not found",
        ):
            identity_tools.get_region(id="RegionOne")

        # Verify mock calls
        mock_conn.identity.get_region.assert_called_once_with(
            region="RegionOne",
        )
        
    def test_get_domains_success(self, mock_get_openstack_conn_identity):
        """Test getting identity domains successfully."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock domain objects
        mock_domain1 = Mock()
        mock_domain1.id = "domainone"
        mock_domain1.name = "DomainOne"
        mock_domain1.description = "Domain One description"
        mock_domain1.is_enabled = True

        mock_domain2 = Mock()
        mock_domain2.id = "domaintwo"
        mock_domain2.name = "DomainTwo"
        mock_domain2.description = "Domain Two description"
        mock_domain2.is_enabled = False
        
        # Configure mock domain.domains()
        mock_conn.identity.domains.return_value = [mock_domain1, mock_domain2]

        # Test get_domains()
        identity_tools = self.get_identity_tools()
        result = identity_tools.get_domains()
        
        # Verify results
        assert result == [
            Domain(id="domainone", name="DomainOne", description="Domain One description", is_enabled=True),
            Domain(id="domaintwo", name="DomainTwo", description="Domain Two description", is_enabled=False),
        ]

        # Verify mock calls
        mock_conn.identity.domains.assert_called_once()

    def test_get_domains_empty_list(self, mock_get_openstack_conn_identity):
        """Test getting identity domains when there are no domains."""
        mock_conn = mock_get_openstack_conn_identity
        
        # Empty domain list
        mock_conn.identity.domains.return_value = []

        # Test get_domains()
        identity_tools = self.get_identity_tools()
        result = identity_tools.get_domains()
        
        # Verify results
        assert result == []
        
        # Verify mock calls
        mock_conn.identity.domains.assert_called_once()

    def test_get_domain_success(self, mock_get_openstack_conn_identity):
        """Test getting a identity domain successfully."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock domain object
        mock_domain = Mock()
        mock_domain.id = "domainone"
        mock_domain.name = "DomainOne"
        mock_domain.description = "Domain One description"
        mock_domain.is_enabled = True
        
        # Configure mock domain.get_domain()
        mock_conn.identity.get_domain.return_value = mock_domain
        
        # Test get_domain()
        identity_tools = self.get_identity_tools()
        result = identity_tools.get_domain(id="domainone")
        
        # Verify results
        assert result == Domain(id="domainone", name="DomainOne", description="Domain One description", is_enabled=True)
        
        # Verify mock calls
        mock_conn.identity.get_domain.assert_called_once_with(domain="domainone")
        
    def test_get_domain_not_found(self, mock_get_openstack_conn_identity):
        """Test getting a identity domain that does not exist."""
        mock_conn = mock_get_openstack_conn_identity

        # Configure mock to raise NotFoundException
        mock_conn.identity.get_domain.side_effect = exceptions.NotFoundException(
            "Domain 'domainone' not found",
        )
        
        # Test get_domain()
        identity_tools = self.get_identity_tools()
        
        # Verify exception is raised
        with pytest.raises(exceptions.NotFoundException, match="Domain 'domainone' not found"):
            identity_tools.get_domain(id="domainone")
        
        # Verify mock calls
        mock_conn.identity.get_domain.assert_called_once_with(domain="domainone")
