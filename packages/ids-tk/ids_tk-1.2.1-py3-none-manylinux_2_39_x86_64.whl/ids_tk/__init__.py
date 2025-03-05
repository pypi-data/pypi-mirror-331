"""
Incidence Density Sampling CLI Tool Python Package

This package provides Python bindings for the IDS-RS tool,
allowing you to perform incidence density sampling from Python.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

__version__ = "1.2.1"

def _find_binary():
    """Find the IDS binary."""
    # Common locations to check for the binary
    binary_name = "ids.exe" if sys.platform.startswith("win") else "ids"
    package_dir = Path(__file__).parent
    
    potential_paths = [
        # Check for binary installed alongside the package
        package_dir / binary_name,
        # Check for binary installed in Python scripts directory
        Path(sys.executable).parent / binary_name,
        # Check for binary in PATH
        Path(shutil.which(binary_name) or "")
    ]
    
    # Check for the binary in cargo target directory during development
    cargo_target_dirs = []
    workspace_root = Path(__file__).parent.parent.parent.parent.parent
    
    if (workspace_root / "Cargo.toml").exists():
        cargo_target_dirs.extend([
            workspace_root / "target" / "release" / binary_name,
            workspace_root / "target" / "debug" / binary_name
        ])
    
    potential_paths.extend(cargo_target_dirs)
    
    # Find the first path that exists
    for path in potential_paths:
        if path.exists():
            return str(path)
    
    # If binary not found, provide a helpful error message
    raise FileNotFoundError(
        f"Could not find IDS binary. Make sure the Rust binary is compiled and "
        f"available in one of these locations: {[str(p) for p in potential_paths]}"
    )

def log_debug(message):
    """Simple debug logging function."""
    if os.environ.get("IDS_DEBUG") == "1":
        print(f"[DEBUG] {message}", file=sys.stderr)

def get_mappings_dir():
    """Find the mappings directory."""
    package_dir = Path(__file__).parent
    
    # First check for mappings in the package directory
    mappings_dir = package_dir / "mappings"
    if mappings_dir.exists():
        log_debug(f"Found mappings directory in package: {mappings_dir}")
        return mappings_dir
    
    # Check for mappings in the workspace root during development
    workspace_root = Path(__file__).parent.parent.parent.parent.parent
    if (workspace_root / "mappings").exists():
        log_debug(f"Found mappings directory in workspace root: {workspace_root / 'mappings'}")
        return workspace_root / "mappings"
    
    log_debug("Mappings directory not found")
    return None

def get_schemas_dir():
    """Find the schemas directory."""
    package_dir = Path(__file__).parent
    
    # First check for schemas in the package directory
    schemas_dir = package_dir / "schemas"
    if schemas_dir.exists():
        log_debug(f"Found schemas directory in package: {schemas_dir}")
        return schemas_dir
    
    # Check for schemas in the workspace root during development
    workspace_root = Path(__file__).parent.parent.parent.parent.parent
    if (workspace_root / "schemas").exists():
        log_debug(f"Found schemas directory in workspace root: {workspace_root / 'schemas'}")
        return workspace_root / "schemas"
    
    log_debug("Schemas directory not found")
    return None

def run_ids(args=None):
    """
    Run the IDS CLI tool with the given arguments.
    
    Args:
        args: List of command-line arguments to pass to the IDS tool.
              If None, uses sys.argv[1:].
    
    Returns:
        The return code from the process.
    """
    if args is None:
        args = sys.argv[1:]
    
    binary_path = _find_binary()
    
    # Prepare environment variables with mapping and schema directories
    env = os.environ.copy()
    
    mappings_dir = get_mappings_dir()
    schemas_dir = get_schemas_dir()
    
    if mappings_dir:
        env["IDS_MAPPINGS_DIR"] = str(mappings_dir)
    
    if schemas_dir:
        env["IDS_SCHEMAS_DIR"] = str(schemas_dir)
    
    # Run the process and forward stdin/stdout/stderr
    process = subprocess.Popen(
        [binary_path] + args,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=env
    )
    
    return process.wait()

def get_mapping_file(mapping_name):
    """
    Get the path to a specific mapping file.
    
    Args:
        mapping_name: Name of the mapping file (without .json extension)
    
    Returns:
        Path to the mapping file if found, None otherwise
    """
    mappings_dir = get_mappings_dir()
    if not mappings_dir:
        return None
    
    mapping_file = mappings_dir / f"{mapping_name}.json"
    if mapping_file.exists():
        return mapping_file
    return None

def get_schema_file(schema_name):
    """
    Get the path to a specific schema file.
    
    Args:
        schema_name: Name of the schema file (without .json extension)
    
    Returns:
        Path to the schema file if found, None otherwise
    """
    schemas_dir = get_schemas_dir()
    if not schemas_dir:
        return None
    
    schema_file = schemas_dir / f"{schema_name}.json"
    if schema_file.exists():
        return schema_file
    return None

def list_mappings():
    """
    List all available mapping files.
    
    Returns:
        List of mapping file names (without .json extension)
    """
    mappings_dir = get_mappings_dir()
    if not mappings_dir:
        return []
    
    return [f.stem for f in mappings_dir.glob("*.json")]

def list_schemas():
    """
    List all available schema files.
    
    Returns:
        List of schema file names (without .json extension)
    """
    schemas_dir = get_schemas_dir()
    if not schemas_dir:
        return []
    
    return [f.stem for f in schemas_dir.glob("*.json")]

def main():
    """Entry point for the command-line script."""
    try:
        sys.exit(run_ids())
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()