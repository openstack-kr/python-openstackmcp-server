import os
from pathlib import Path


# Transport protocol
MCP_TRANSPORT = os.environ.get("TRANSPORT", "stdio")

# Application paths
BASE_DIR = Path(__file__).parent.parent.parent
