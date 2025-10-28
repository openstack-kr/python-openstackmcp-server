# Test Suite Documentation

This directory contains comprehensive unit tests for the OpenStack MCP Server project.

## Overview

- **Total Tests**: 156
- **Test Classes**: 5
- **Test Coverage**: 85%+
- **Test Framework**: pytest

## Directory Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── tools/
│   ├── test_block_storage_tools.py   # Cinder (Block Storage) tests
│   ├── test_compute_tools.py         # Nova (Compute) tests
│   ├── test_identity_tools.py        # Keystone (Identity) tests
│   ├── test_image_tools.py           # Glance (Image) tests
│   └── test_network_tools.py         # Neutron (Network) tests
└── README.md                # This file
```

## Running Tests

### Run All Tests

```bash
# Using uv
uv run --group test pytest

# Using tox
tox -e py3
```

### Run Specific Test File

```bash
uv run --group test pytest tests/tools/test_compute_tools.py
```

### Run Tests by Marker

```bash
# Run only unit tests
uv run --group test pytest -m unit

# Run only integration tests
uv run --group test pytest -m integration

# Run only slow tests
uv run --group test pytest -m slow
```

### Run with Verbose Output

```bash
uv run --group test pytest -v
```

### Run with Coverage

```bash
# Using tox
tox -e cover

# Generate HTML coverage report
uv run --group test pytest --cov=openstack_mcp_server --cov-report=html
```

## Test Markers

Tests are categorized using pytest markers for better organization:

- `@pytest.mark.unit` - Unit tests that don't require external dependencies
- `@pytest.mark.integration` - Integration tests that may require OpenStack services
- `@pytest.mark.slow` - Tests that take longer than 1 second to run

## Fixtures

### Shared Fixtures (conftest.py)

#### `mock_openstack_conn_factory`
Factory fixture to create mock OpenStack connections for any module.

**Usage:**
```python
def test_something(mock_openstack_conn_factory):
    mock_conn = mock_openstack_conn_factory('compute')
    # Use mock_conn in your test
```

**Available modules:**
- `compute` - Nova compute service
- `image` - Glance image service
- `identity` - Keystone identity service
- `network` - Neutron network service
- `block_storage` - Cinder block storage service
- `base` - Base module

#### Legacy Fixtures (Deprecated)
The following fixtures are maintained for backward compatibility but will be removed in future versions:
- `mock_get_openstack_conn` (use `mock_openstack_conn_factory('compute')` instead)
- `mock_get_openstack_conn_image` (use `mock_openstack_conn_factory('image')` instead)
- `mock_get_openstack_conn_identity` (use `mock_openstack_conn_factory('identity')` instead)
- `mock_openstack_connect_network` (use `mock_openstack_conn_factory('network')` instead)
- `mock_get_openstack_conn_block_storage` (use `mock_openstack_conn_factory('block_storage')` instead)
- `mock_openstack_base` (use `mock_openstack_conn_factory('base')` instead)

## Test Coverage by Module

| Module | Tests | Coverage | Notes |
|--------|-------|----------|-------|
| **Compute Tools** | 40 | 100% | Nova server and flavor management |
| **Image Tools** | 10 | 89% | Glance image operations |
| **Identity Tools** | 34 | 86% | Keystone users, projects, roles |
| **Network Tools** | 48 | 85% | Neutron networks, ports, routers, security groups |
| **Block Storage Tools** | 24 | 98% | Cinder volume management |

## Writing New Tests

### Test Structure Standard

All test files should follow this structure:

```python
"""Unit tests for [ModuleName] class.

This module contains comprehensive tests for the [ModuleName] class,
which provides functionality for [brief description].

Test Coverage:
    - [Feature 1]
    - [Feature 2]
    - [Feature 3]
"""

import pytest
from openstack_mcp_server.tools.[module] import [Class]


@pytest.mark.unit
class Test[ClassName]:
    """Test cases for [ClassName] class."""

    def test_[feature]_success(self, mock_get_openstack_conn_[module]):
        """Test [feature description].

        Verifies that [method_name]() correctly [what it does].
        """
        # Arrange
        mock_conn = mock_get_openstack_conn_[module]
        # ... setup mocks

        # Act
        result = [Class]().[method]()

        # Assert
        assert result == expected_output
        mock_conn.[service].[method].assert_called_once()
```

### Docstring Guidelines

1. **Module-level docstring**: Describe what the test file covers
2. **Class-level docstring**: Brief description of the class being tested
3. **Test method docstring**:
   - First line: What the test does
   - Second paragraph: What it verifies

### Example Test

```python
def test_get_server_success(self, mock_get_openstack_conn):
    """Test retrieving a specific server by ID.

    Verifies that get_server() correctly retrieves and returns
    a Server object for a given server ID.
    """
    mock_conn = mock_get_openstack_conn
    mock_server = {"id": "server-123", "name": "web-01"}
    mock_conn.compute.get_server.return_value = mock_server

    result = ComputeTools().get_server("server-123")

    assert result.id == "server-123"
    assert result.name == "web-01"
```

## Mock Data Guidelines

### Factory Methods

Use factory methods to create consistent mock data:

```python
@staticmethod
def server_factory(**overrides):
    """Factory method to create mock server data.

    Args:
        **overrides: Key-value pairs to override default values

    Returns:
        Dictionary with mock server data
    """
    defaults = {
        "id": str(uuid.uuid4()),
        "name": "test-server",
        "status": "ACTIVE",
        # ... other fields
    }
    defaults.update(overrides)
    return defaults
```

## Common Test Patterns

### Testing Success Cases

```python
def test_operation_success(self, fixture):
    """Test successful operation."""
    # Setup mock
    mock_conn = fixture
    mock_conn.service.method.return_value = expected_data

    # Execute
    result = ToolClass().method()

    # Verify
    assert result == expected_output
    mock_conn.service.method.assert_called_once()
```

### Testing with Filters

```python
def test_get_with_filter(self, fixture):
    """Test filtering by specific criteria."""
    mock_conn = fixture
    mock_conn.service.list.return_value = [filtered_item]

    result = ToolClass().get_items(status="active")

    mock_conn.service.list.assert_called_once_with(status="active")
```

### Testing Empty Results

```python
def test_get_empty_list(self, fixture):
    """Test when no items exist."""
    mock_conn = fixture
    mock_conn.service.list.return_value = []

    result = ToolClass().get_items()

    assert result == []
```

## Troubleshooting

### Tests Fail After Changes

1. Run tests with verbose output: `pytest -v`
2. Check if fixtures need updating
3. Verify mock data structure matches response models

### Import Errors

Make sure you're in the project root and run:
```bash
uv sync --group test
```

### Marker Not Found

If you get "unknown marker" warnings, ensure `pyproject.toml` has the markers configured in `[tool.pytest.ini_options]`.

## Contributing

When adding new tests:

1. Follow the test structure standard
2. Add appropriate markers (`@pytest.mark.unit`, etc.)
3. Write comprehensive docstrings
4. Use factory methods for mock data
5. Ensure tests are independent and can run in any order
6. Maintain or improve coverage (currently 85%+)

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [OpenStack SDK documentation](https://docs.openstack.org/openstacksdk/)
