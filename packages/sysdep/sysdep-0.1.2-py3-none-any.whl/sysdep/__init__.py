# sysdep/__init__.py
from .checkers.executable import ExecutableDependency
from .parsers.manifest import parse_manifest_file
from .config import DEFAULT_MANIFEST_FILE
from .utils import with_progress, parallel_map

__version__ = "0.1.0"

def check_dependencies(manifest_file=None, show_progress=True, max_workers=None):
    """
    Check if all dependencies specified in the manifest file are installed.
    
    Args:
        manifest_file: Path to the manifest file. If None, looks for default files.
        show_progress: Whether to show a progress bar during the check.
        max_workers: Maximum number of worker threads for parallel processing.
        
    Returns:
        A dictionary with results of the dependency checks.
    """
    manifest_file = manifest_file or DEFAULT_MANIFEST_FILE
    dependencies = parse_manifest_file(manifest_file)
    
    results = {
        "all_installed": True,
        "dependencies": [],
        "missing": []
    }
    
    # Check dependencies in parallel
    dependency_infos = parallel_map(
        lambda dep: dep.get_installation_info(),
        dependencies,
        desc="Checking dependencies",
        show_progress=show_progress,
        max_workers=max_workers
    )
    
    # Process results
    for info in dependency_infos:
        if info:
            results["dependencies"].append(info)
            if not info["installed"]:
                results["all_installed"] = False
                results["missing"].append(info)
    
    return results