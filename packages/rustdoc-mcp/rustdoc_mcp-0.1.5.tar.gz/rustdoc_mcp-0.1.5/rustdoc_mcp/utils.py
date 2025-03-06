"""
Utility functions for rustdoc-mcp
"""

import os
import subprocess
from typing import Optional, Tuple

from rich.console import Console

console = Console(stderr=True)


def check_rust_installation() -> bool:
    """Check if Rust and necessary tools are installed"""
    tools = [
        ("rustc", "--version"),
        ("cargo", "--version"),
        ("rustdoc", "--version"),
        ("rustup", "--version"),
    ]

    missing = []

    for tool, arg in tools:
        try:
            subprocess.run([tool, arg], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            missing.append(tool)

    if missing:
        console.log(
            f"[bold red]Missing required tools: {', '.join(missing)}[/bold red]"
        )
        return False

    return True


def resolve_path(
    path: str, working_dir: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Convert different types of paths to rustdoc-compatible paths

    Args:
        path: The path to resolve (file path or crate path)
        working_dir: Optional working directory for relative paths

    Returns:
        Tuple of (resolved_path, error_message)
    """
    # If path is a file path
    if os.path.exists(path):
        # Find crate root
        current = os.path.abspath(path)
        while current != os.path.dirname(current):  # Stop at root
            if os.path.exists(os.path.join(current, "Cargo.toml")):
                # Found the project root
                rel_path = os.path.relpath(path, current)

                # Try to convert to crate path (simplified approach)
                # A more robust implementation would parse the Cargo.toml and project structure
                package_name = get_package_name(current)
                if package_name:
                    # Convert path/to/file.rs to package::path::to::file
                    parts = rel_path.replace(".rs", "").split(os.sep)
                    if parts[0] == "src":
                        parts = parts[1:]  # Remove src prefix
                    crate_path = f"{package_name}::" + "::".join(parts)
                    return crate_path, None

                return None, f"Could not determine crate path for {path}"
            current = os.path.dirname(current)

        return None, f"Not a Rust project: {path}"

    # If path already contains :: (crate path)
    elif "::" in path:
        return path, None

    # Just a crate name
    else:
        return path, None


def get_package_name(cargo_dir: str) -> Optional[str]:
    """Extract package name from Cargo.toml"""
    cargo_path = os.path.join(cargo_dir, "Cargo.toml")
    try:
        with open(cargo_path, "r") as f:
            for line in f:
                if line.strip().startswith("name"):
                    # Extract package name from line like 'name = "package"'
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        # Remove quotes and whitespace
                        return parts[1].strip().strip("\"'")
    except Exception as e:
        console.log(f"Error reading Cargo.toml: {e}")

    return None
