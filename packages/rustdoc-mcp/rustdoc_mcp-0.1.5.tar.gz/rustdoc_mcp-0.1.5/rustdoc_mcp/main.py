"""
Main entry point for the rustdoc-mcp tool.
"""

import argparse
import os
import sys

from rich.console import Console

from .server import create_server

console = Console(stderr=True)


def main() -> int:
    """Main entry point for the tool."""
    parser = argparse.ArgumentParser(description="MCP server for Rust documentation")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport type to use (stdio or sse)",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to use for SSE transport"
    )

    args = parser.parse_args()

    # Create the server
    mcp = create_server()

    # Set environment variables for transport configuration
    if args.transport == "sse":
        # Start server with HTTP/SSE transport
        console.log(f"Serving on HTTP port {args.port}")
        os.environ["MCP_TRANSPORT"] = "sse"
        os.environ["MCP_PORT"] = str(args.port)
    else:
        # Start server with stdio transport (default)
        console.log("Serving on stdio transport")
        os.environ["MCP_TRANSPORT"] = "stdio"

    # Run the server
    mcp.run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
