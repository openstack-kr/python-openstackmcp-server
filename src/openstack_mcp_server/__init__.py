import argparse
import logging
import signal
import sys


# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("openstack-mcp-server")


def handle_interrupt(signum, frame):
    """Handle keyboard interrupt (Ctrl+C) gracefully."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


def main():
    """Openstack MCP Server main entry point."""
    try:
        # Import here to avoid circular imports
        from openstack_mcp_server.config import MCP_TRANSPORT
        from openstack_mcp_server.server import serve

        parser = argparse.ArgumentParser(
            description="Openstack MCP Server",
        )

        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, handle_interrupt)
        signal.signal(signal.SIGTERM, handle_interrupt)

        # Validate transport protocol
        if MCP_TRANSPORT not in ["stdio", "streamable-http"]:
            logger.error(
                f"Invalid transport protocol: {MCP_TRANSPORT}. Using stdio instead.",
            )
            transport = "stdio"
        else:
            transport = MCP_TRANSPORT

        # Start the server
        logger.info(
            f"Starting Openstack MCP Server with {transport} transport",
        )

        args = parser.parse_args()

        serve(transport=transport, **vars(args))

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down gracefully...")
        sys.exit(0)


if __name__ == "__main__":
    main()
