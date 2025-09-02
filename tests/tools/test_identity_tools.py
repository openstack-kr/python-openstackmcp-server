from unittest.mock import Mock

import pydantic
import pytest

from openstack import exceptions

from openstack_mcp_server.tools.identity_tools import IdentityTools
from openstack_mcp_server.tools.response.identity import (
    Domain,
    Project,
    Region,
)


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
        mock_region.description = None

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
        mock_region.description = None

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
            description=None,
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
            Domain(
                id="domainone",
                name="DomainOne",
                description="Domain One description",
                is_enabled=True,
            ),
            Domain(
                id="domaintwo",
                name="DomainTwo",
                description="Domain Two description",
                is_enabled=False,
            ),
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
        mock_domain.id = "d01a81393377480cbd75c0210442e687"
        mock_domain.name = "domainone"
        mock_domain.description = "domainone description"
        mock_domain.is_enabled = True

        # Configure mock domain.get_domain()
        mock_conn.identity.find_domain.return_value = mock_domain

        # Test get_domain()
        identity_tools = self.get_identity_tools()
        result = identity_tools.get_domain(name="domainone")

        # Verify results
        assert result == Domain(
            id="d01a81393377480cbd75c0210442e687",
            name="domainone",
            description="domainone description",
            is_enabled=True,
        )

        # Verify mock calls
        mock_conn.identity.find_domain.assert_called_once_with(
            name_or_id="domainone",
        )

    def test_get_domain_not_found(self, mock_get_openstack_conn_identity):
        """Test getting a identity domain that does not exist."""
        mock_conn = mock_get_openstack_conn_identity

        # Configure mock to raise NotFoundException
        mock_conn.identity.find_domain.side_effect = (
            exceptions.NotFoundException(
                "Domain 'domainone' not found",
            )
        )

        # Test get_domain()
        identity_tools = self.get_identity_tools()

        # Verify exception is raised
        with pytest.raises(
            exceptions.NotFoundException,
            match="Domain 'domainone' not found",
        ):
            identity_tools.get_domain(name="domainone")

        # Verify mock calls
        mock_conn.identity.find_domain.assert_called_once_with(
            name_or_id="domainone",
        )

    def test_create_domain_success(self, mock_get_openstack_conn_identity):
        """Test creating a identity domain successfully."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock domain object
        mock_domain = Mock()
        mock_domain.id = "d01a81393377480cbd75c0210442e687"
        mock_domain.name = "domainone"
        mock_domain.description = "domainone description"
        mock_domain.is_enabled = True

        # Configure mock domain.create_domain()
        mock_conn.identity.create_domain.return_value = mock_domain

        # Test create_domain()
        identity_tools = self.get_identity_tools()
        result = identity_tools.create_domain(
            name="domainone",
            description="domainone description",
            is_enabled=True,
        )

        # Verify results
        assert result == Domain(
            id="d01a81393377480cbd75c0210442e687",
            name="domainone",
            description="domainone description",
            is_enabled=True,
        )

        # Verify mock calls
        mock_conn.identity.create_domain.assert_called_once_with(
            name="domainone",
            description="domainone description",
            enabled=True,
        )

    def test_create_domain_without_name(
        self,
        mock_get_openstack_conn_identity,
    ):
        """Test creating a identity domain without a name."""

        # Test create_domain()
        identity_tools = self.get_identity_tools()

        # Verify pydantic validation exception is raised
        with pytest.raises(pydantic.ValidationError):
            identity_tools.create_domain(
                name="",
                description="domainone description",
                is_enabled=False,
            )

    def test_create_domain_without_description(
        self,
        mock_get_openstack_conn_identity,
    ):
        """Test creating a identity domain without a description."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock domain object
        mock_domain = Mock()
        mock_domain.id = "d01a81393377480cbd75c0210442e687"
        mock_domain.name = "domainone"
        mock_domain.description = None
        mock_domain.is_enabled = False

        # Configure mock domain.create_domain()
        mock_conn.identity.create_domain.return_value = mock_domain

        # Test create_domain()
        identity_tools = self.get_identity_tools()
        result = identity_tools.create_domain(name="domainone")

        # Verify results
        assert result == Domain(
            id="d01a81393377480cbd75c0210442e687",
            name="domainone",
            description=None,
            is_enabled=False,
        )

        # Verify mock calls
        mock_conn.identity.create_domain.assert_called_once_with(
            name="domainone",
            description=None,
            enabled=False,
        )

    def test_delete_domain_success(self, mock_get_openstack_conn_identity):
        """Test deleting a identity domain successfully."""
        mock_conn = mock_get_openstack_conn_identity

        # mock
        mock_domain = Mock()
        mock_domain.id = "d01a81393377480cbd75c0210442e687"
        mock_domain.name = "domainone"
        mock_domain.description = "domainone description"
        mock_domain.is_enabled = True

        mock_conn.identity.find_domain.return_value = mock_domain

        # Test delete_domain()
        identity_tools = self.get_identity_tools()
        result = identity_tools.delete_domain(name="domainone")

        # Verify results
        assert result is None

        # Verify mock calls
        mock_conn.identity.find_domain.assert_called_once_with(
            name_or_id="domainone",
        )
        mock_conn.identity.delete_domain.assert_called_once_with(
            domain=mock_domain,
            ignore_missing=False,
        )

    def test_delete_domain_not_found(self, mock_get_openstack_conn_identity):
        """Test deleting a identity domain that does not exist."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock domain object
        mock_domain = Mock()
        mock_domain.id = "d01a81393377480cbd75c0210442e687"
        mock_domain.name = "domainone"
        mock_domain.description = "domainone description"
        mock_domain.is_enabled = True

        mock_conn.identity.find_domain.return_value = mock_domain

        # Configure mock to raise NotFoundException
        mock_conn.identity.delete_domain.side_effect = (
            exceptions.NotFoundException(
                "Domain 'domainone' not found",
            )
        )

        # Test delete_domain()
        identity_tools = self.get_identity_tools()

        # Verify exception is raised
        with pytest.raises(
            exceptions.NotFoundException,
            match="Domain 'domainone' not found",
        ):
            identity_tools.delete_domain(name="domainone")

        # Verify mock calls
        mock_conn.identity.find_domain.assert_called_once_with(
            name_or_id="domainone",
        )
        mock_conn.identity.delete_domain.assert_called_once_with(
            domain=mock_domain,
            ignore_missing=False,
        )

    def test_update_domain_with_all_fields_success(
        self,
        mock_get_openstack_conn_identity,
    ):
        """Test updating a identity domain successfully."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock domain object
        mock_domain = Mock()
        mock_domain.id = "d01a81393377480cbd75c0210442e687"
        mock_domain.name = "domainone"
        mock_domain.description = "domainone description"
        mock_domain.is_enabled = True

        # Configure mock domain.update_domain()
        mock_conn.identity.update_domain.return_value = mock_domain

        # Test update_domain()
        identity_tools = self.get_identity_tools()
        result = identity_tools.update_domain(
            id="d01a81393377480cbd75c0210442e687",
            name="domainone",
            description="domainone description",
            is_enabled=True,
        )

        # Verify results
        assert result == Domain(
            id="d01a81393377480cbd75c0210442e687",
            name="domainone",
            description="domainone description",
            is_enabled=True,
        )

        # Verify mock calls
        mock_conn.identity.update_domain.assert_called_once_with(
            domain="d01a81393377480cbd75c0210442e687",
            name="domainone",
            description="domainone description",
            is_enabled=True,
        )

    def test_update_domain_with_empty_args(
        self,
        mock_get_openstack_conn_identity,
    ):
        """Test updating a identity domain with empty arguments."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock domain object
        mock_domain = Mock()
        mock_domain.id = "d01a81393377480cbd75c0210442e687"
        mock_domain.name = "domainone"
        mock_domain.description = "domainone description"
        mock_domain.is_enabled = True

        # Configure mock domain.update_domain()
        mock_conn.identity.update_domain.return_value = mock_domain

        # Test update_domain()
        identity_tools = self.get_identity_tools()
        result = identity_tools.update_domain(
            id="d01a81393377480cbd75c0210442e687",
        )

        # Verify results
        assert result == Domain(
            id="d01a81393377480cbd75c0210442e687",
            name="domainone",
            description="domainone description",
            is_enabled=True,
        )

        # Verify mock calls
        mock_conn.identity.update_domain.assert_called_once_with(
            domain="d01a81393377480cbd75c0210442e687",
        )

    def test_update_domain_with_empty_id(
        self,
        mock_get_openstack_conn_identity,
    ):
        """Test updating a identity domain with an empty name."""
        mock_conn = mock_get_openstack_conn_identity

        mock_conn.identity.update_domain.side_effect = (
            exceptions.BadRequestException(
                "Field required",
            )
        )

        # Test update_domain()
        identity_tools = self.get_identity_tools()

        # Verify exception is raised
        with pytest.raises(
            exceptions.BadRequestException,
            match="Field required",
        ):
            identity_tools.update_domain(id="")

        # Verify mock calls
        mock_conn.identity.update_domain.assert_called_once_with(domain="")

    def test_get_projects_success(self, mock_get_openstack_conn_identity):
        """Test getting identity projects successfully."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock project objects
        mock_project1 = Mock()
        mock_project1.id = "project1111111111111111111111111"
        mock_project1.name = "ProjectOne"
        mock_project1.description = "Project One description"
        mock_project1.is_enabled = True
        mock_project1.domain_id = "domain1111111111111111111111111"
        mock_project1.parent_id = "parentproject1111111111111111111"

        mock_project2 = Mock()
        mock_project2.id = "project2222222222222222222222222"
        mock_project2.name = "ProjectTwo"
        mock_project2.description = "Project Two description"
        mock_project2.is_enabled = False
        mock_project2.domain_id = "domain22222222222222222222222222"
        mock_project2.parent_id = "default"

        # Configure mock project.projects()
        mock_conn.identity.projects.return_value = [
            mock_project1,
            mock_project2,
        ]

        # Test get_projects()
        identity_tools = self.get_identity_tools()
        result = identity_tools.get_projects()

        # Verify results
        assert result == [
            Project(
                id="project1111111111111111111111111",
                name="ProjectOne",
                description="Project One description",
                is_enabled=True,
                domain_id="domain1111111111111111111111111",
                parent_id="parentproject1111111111111111111",
            ),
            Project(
                id="project2222222222222222222222222",
                name="ProjectTwo",
                description="Project Two description",
                is_enabled=False,
                domain_id="domain22222222222222222222222222",
                parent_id="default",
            ),
        ]

        # Verify mock calls
        mock_conn.identity.projects.assert_called_once()

    def test_get_projects_empty_list(self, mock_get_openstack_conn_identity):
        """Test getting identity projects when there are no projects."""
        mock_conn = mock_get_openstack_conn_identity

        # Empty project list
        mock_conn.identity.projects.return_value = []

        # Test get_projects()
        identity_tools = self.get_identity_tools()
        result = identity_tools.get_projects()

        # Verify results
        assert result == []

        # Verify mock calls
        mock_conn.identity.projects.assert_called_once()

    def test_get_project_success(self, mock_get_openstack_conn_identity):
        """Test getting a identity project successfully."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock project object
        mock_project = Mock()
        mock_project.id = "project1111111111111111111111111"
        mock_project.name = "ProjectOne"
        mock_project.description = "Project One description"
        mock_project.is_enabled = True
        mock_project.domain_id = "domain1111111111111111111111111"
        mock_project.parent_id = "parentproject1111111111111111111"

        # Configure mock project.find_project()
        mock_conn.identity.find_project.return_value = mock_project

        # Test get_project()
        identity_tools = self.get_identity_tools()
        result = identity_tools.get_project(name="ProjectOne")

        # Verify results
        assert result == Project(
            id="project1111111111111111111111111",
            name="ProjectOne",
            description="Project One description",
            is_enabled=True,
            domain_id="domain1111111111111111111111111",
            parent_id="parentproject1111111111111111111",
        )

        # Verify mock calls
        mock_conn.identity.find_project.assert_called_once_with(
            name_or_id="ProjectOne",
            ignore_missing=False,
        )

    def test_get_project_not_found(self, mock_get_openstack_conn_identity):
        """Test getting a identity project that does not exist."""
        mock_conn = mock_get_openstack_conn_identity

        # Configure mock to raise NotFoundException
        mock_conn.identity.find_project.side_effect = (
            exceptions.NotFoundException(
                "Project 'ProjectOne' not found",
            )
        )

        # Test get_project()
        identity_tools = self.get_identity_tools()

        # Verify exception is raised
        with pytest.raises(
            exceptions.NotFoundException,
            match="Project 'ProjectOne' not found",
        ):
            identity_tools.get_project(name="ProjectOne")

        # Verify mock calls
        mock_conn.identity.find_project.assert_called_once_with(
            name_or_id="ProjectOne",
            ignore_missing=False,
        )

    def test_create_project_success_with_all_fields(
        self, mock_get_openstack_conn_identity
    ):
        """Test creating a identity project successfully."""
        mock_conn = mock_get_openstack_conn_identity

        # Create mock project object
        mock_project = Mock()
        mock_project.id = "project1111111111111111111111111"
        mock_project.name = "ProjectOne"
        mock_project.description = "Project One description"
        mock_project.is_enabled = True
        mock_project.domain_id = "domain1111111111111111111111111"
        mock_project.parent_id = "parentproject1111111111111111111"

        # Configure mock project.create_project()
        mock_conn.identity.create_project.return_value = mock_project

        # Test create_project()
        identity_tools = self.get_identity_tools()
        result = identity_tools.create_project(
            name="ProjectOne",
            description="Project One description",
            is_enabled=True,
            domain_id="domain1111111111111111111111111",
            parent_id="parentproject1111111111111111111",
        )

        # Verify results
        assert result == Project(
            id="project1111111111111111111111111",
            name="ProjectOne",
            description="Project One description",
            is_enabled=True,
            domain_id="domain1111111111111111111111111",
            parent_id="parentproject1111111111111111111",
        )

        # Verify mock calls
        mock_conn.identity.create_project.assert_called_once_with(
            name="ProjectOne",
            description="Project One description",
            is_enabled=True,
            domain_id="domain1111111111111111111111111",
            parent_id="parentproject1111111111111111111",
        )

    def test_create_project_without_all_fields(
        self, mock_get_openstack_conn_identity
    ):
        """Test creating a identity project without all fields."""
        mock_conn = mock_get_openstack_conn_identity

        mock_conn.identity.create_project.side_effect = (
            exceptions.BadRequestException(
                "Field required",
            )
        )

        # Test create_project()
        identity_tools = self.get_identity_tools()

        with pytest.raises(
            exceptions.BadRequestException,
            match="Field required",
        ):
            identity_tools.create_project(
                name="ProjectOne",
                description="Project One description",
                is_enabled=True,
                domain_id=None,
                parent_id=None,
            )

        # Verify mock calls
        mock_conn.identity.create_project.assert_called_once_with(
            name="ProjectOne",
            description="Project One description",
            is_enabled=True,
            domain_id=None,
            parent_id=None,
        )
