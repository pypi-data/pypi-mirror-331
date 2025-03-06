"""
MCP server implementation for Rust documentation
"""

import atexit
import json
import os
import subprocess
import sys
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from rich.console import Console

from .cache import DocumentationCache
from .documentation import DocRetriever
from .utils import check_rust_installation, resolve_path

console = Console(stderr=True)

# Define tool description
TOOL_DESCRIPTION = """Get Rust documentation for a crate, module, type, trait, function, or method.
This is the preferred and most efficient way to understand Rust crates, providing official documentation
in a concise format. Use this before attempting to read source files directly.

Best Practices:
1. ALWAYS try this tool first before reading Rust source code
2. Start with basic crate documentation before looking at source code or specific symbols
3. Use --document-private-items flag when you need comprehensive documentation
4. Only look up specific symbols after understanding the crate overview
5. For external crates, provide the project_path to help find local documentation

Common Usage Patterns:
- Standard library: Use fully qualified path (e.g., "std::collections::HashMap", "std::vec::Vec")
- External crates: Use fully qualified path (e.g., "serde::Serialize", "tokio::sync::Mutex")
- Local code: Use fully qualified path relative to the crate root
- Project docs: Include project_path for documentation of local project dependencies

The documentation is cached for 5 minutes to improve performance.

Note: This tool prioritizes using locally installed documentation first, generating it only when needed."""

# Ensure dependencies are installed
def install_dependencies():
    """Install required Python dependencies if not already installed"""
    try:
        # Check if beautifulsoup4 is installed
        import importlib
        try:
            importlib.import_module('bs4')
            console.log("BeautifulSoup already installed")
        except ImportError:
            console.log("Installing BeautifulSoup for better HTML parsing...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "beautifulsoup4"],
                check=True,
                capture_output=True
            )
            console.log("BeautifulSoup installed successfully")
    except Exception as e:
        console.log(f"Warning: Could not install dependencies: {str(e)}")
        console.log("Documentation will use simple regex-based HTML parsing")
        
# Install dependencies if needed
install_dependencies()


def create_server() -> FastMCP:
    """Create and configure the MCP server"""

    # Check if Rust tools are installed
    if not check_rust_installation():
        console.log("[bold red]Error: Required Rust tools are missing[/bold red]")
        console.log("Please install Rust using rustup: https://rustup.rs/")
        sys.exit(1)

    # Initialize the server
    mcp = FastMCP(
        "rustdoc-mcp", version="0.1.0", description="MCP server for Rust documentation",
        # Include debug option to help diagnose issues
        debug=True
    )

    # Store needed state
    state = {
        "doc_retriever": DocRetriever(),
        "cache": DocumentationCache(),
        "temp_dirs": [],
    }

    # Define cleanup function
    def cleanup():
        """Clean up temporary directories on shutdown"""
        console.log("Cleaning up resources...")
        retriever = state["doc_retriever"]
        retriever.cleanup_temp_dirs(state["temp_dirs"])
        state["temp_dirs"] = []
        console.log("Cleanup complete")

    # Register cleanup with atexit to ensure it runs when Python exits
    atexit.register(cleanup)
    console.log("[yellow]Note: Using atexit for cleanup on program exit[/yellow]")

    @mcp.tool(name="get_doc", description=TOOL_DESCRIPTION)
    def get_doc(
        path: str,
        target: Optional[str] = None,
        flags: Optional[List[str]] = None,
        working_dir: Optional[str] = None,
        project_path: Optional[str] = None,
    ) -> dict:
        """
        Get Rust documentation for a crate, module, or item.

        Args:
            path: Path to the Rust crate, module or item (e.g., 'std::collections', 'serde::Deserialize')
            target: Optional specific item to document (struct, enum, function, etc.)
            flags: Optional additional rustdoc command flags
            working_dir: Optional working directory for cargo-aware documentation
            project_path: Optional path to a local Rust project that contains documentation for needed crates

        Returns:
            Documentation text for the requested item
        """
        console.log(
            f"get_doc called with path={path}, target={target}, flags={flags}, working_dir={working_dir}, project_path={project_path}"
        )

        # Validate working directory if provided
        if working_dir and not os.path.isdir(working_dir):
            error_message = f"Error: Invalid working directory: {working_dir}"
            return {
                "content": [
                    {"type": "text", "text": error_message}
                ]
            }
            
        # Validate project path if provided
        if project_path and not os.path.isdir(project_path):
            error_message = f"Error: Invalid project path: {project_path}"
            return {
                "content": [
                    {"type": "text", "text": error_message}
                ]
            }

        # Resolve path if it's a file path
        resolved_path, error = resolve_path(path, working_dir)
        if error:
            error_message = f"Error: {error}"
            return {
                "content": [
                    {"type": "text", "text": error_message}
                ]
            }

        if resolved_path and resolved_path != path:
            console.log(f"Resolved path '{path}' to '{resolved_path}'")
            path = resolved_path

        # Generate cache key
        cache_key = f"{working_dir or ''}|{project_path or ''}|{path}|{target or ''}|{','.join(flags or [])}"

        # Check cache first
        cached = state["cache"].get(cache_key)
        if cached:
            return {
                "content": [
                    {"type": "text", "text": cached}
                ]
            }

        # Create temporary project if needed
        if not working_dir:
            temp_dir = state["doc_retriever"].create_temp_project(path)
            state["temp_dirs"].append(temp_dir)
            working_dir = temp_dir

        # Get documentation based on path type
        retriever = state["doc_retriever"]

        if retriever.is_std_lib(path):
            # Standard library
            doc = retriever.get_std_lib_doc(path, target)
        elif os.path.exists(path):
            # Local file path
            doc = retriever.get_local_doc(path, target, working_dir, flags)
        else:
            # External crate
            doc = retriever.get_crate_doc(path, target, working_dir, flags, project_path)

        # Cache the result
        state["cache"].set(cache_key, doc)

        return {
            "content": [
                {"type": "text", "text": doc}
            ]
        }

    @mcp.tool(name="cache_stats")
    def cache_stats() -> dict:
        """Get cache statistics"""
        stats = state["cache"].get_stats()
        stats_json = json.dumps(stats, indent=2)
        return {
            "content": [
                {"type": "text", "text": stats_json}
            ]
        }

    @mcp.tool(name="clear_cache")
    def clear_cache() -> dict:
        """Clear the documentation cache"""
        state["cache"].clear()
        return {
            "content": [
                {"type": "text", "text": "Cache cleared"}
            ]
        }

    return mcp
