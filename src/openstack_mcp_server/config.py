import os
from pathlib import Path


# Transport protocol
MCP_TRANSPORT: str = os.environ.get("TRANSPORT", "stdio")

# Openstack client settings
MCP_CLOUD_NAME: str = os.environ.get("CLOUD_NAME", "openstack")
MCP_DEBUG_MODE: bool = os.environ.get("DEBUG_MODE", "true").lower() == "true"

# Application paths
BASE_DIR = Path(__file__).parent.parent.parent
