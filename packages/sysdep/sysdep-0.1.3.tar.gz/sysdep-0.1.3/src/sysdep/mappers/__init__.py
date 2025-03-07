# sysdep/mappers/__init__.py
"""Package for mapping Python packages to system dependencies."""

from .core import (
    get_system_dependencies_for_package,
    map_python_to_system_dependencies,
    print_dependency_mapping
)
from .name_normalizer import normalize_package_name

__all__ = [
    'get_system_dependencies_for_package',
    'map_python_to_system_dependencies',
    'print_dependency_mapping',
    'normalize_package_name'
] 