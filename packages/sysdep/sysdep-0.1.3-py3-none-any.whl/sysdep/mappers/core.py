# sysdep/mappers/core.py
"""Core functionality for mapping Python packages to system dependencies."""

# Standard library imports
from typing import List, Set, Optional

# Local imports
from ..checkers.base import Dependency
from .dependency_data import PACKAGE_DEPENDENCIES
from .name_normalizer import normalize_package_name
from ..utils import with_progress, parallel_map

def get_system_dependencies_for_package(package_name: str) -> List[Dependency]:
    """
    Get system dependencies for a Python package.
    
    Args:
        package_name: Name of the Python package
        
    Returns:
        List of system dependencies for the package
    """
    normalized_name = normalize_package_name(package_name)
    return PACKAGE_DEPENDENCIES.get(normalized_name, [])

def map_python_to_system_dependencies(python_packages: List[str], show_progress: bool = True, max_workers: Optional[int] = None) -> Set[Dependency]:
    """
    Map a list of Python packages to their system dependencies.
    
    Args:
        python_packages: List of Python package names
        show_progress: Whether to show progress bar
        max_workers: Maximum number of worker threads for parallel processing
        
    Returns:
        Set of unique system dependencies required by the packages
    """
    # Map packages to dependencies in parallel
    all_deps = parallel_map(
        get_system_dependencies_for_package,
        python_packages,
        desc="Mapping dependencies",
        show_progress=show_progress,
        max_workers=max_workers
    )
    
    # Combine all dependencies into a unique set
    system_deps = set()
    for deps in all_deps:
        if deps:
            system_deps.update(deps)
    
    return system_deps

def print_dependency_mapping(python_packages: List[str], system_deps=None):
    """
    Print the mapping of Python packages to system dependencies.
    
    Args:
        python_packages: List of Python package names
        system_deps: Optional pre-computed system dependencies
    """
    if system_deps is None:
        system_deps = map_python_to_system_dependencies(python_packages)
        
    for pkg in python_packages:
        normalized_pkg = normalize_package_name(pkg)
        if pkg != normalized_pkg:
            pkg_display = f"{pkg} (normalized to {normalized_pkg})"
        else:
            pkg_display = pkg
            
        sys_deps = get_system_dependencies_for_package(pkg)
        if not sys_deps:
            print(f"{pkg_display}: No known system dependencies")
        else:
            print(f"{pkg_display}:")
            for dep in sys_deps:
                if hasattr(dep, 'name'):
                    dep_type = dep.__class__.__name__.lower().replace('dependency', '')
                    print(f"  - {dep_type}: {dep.name}") 