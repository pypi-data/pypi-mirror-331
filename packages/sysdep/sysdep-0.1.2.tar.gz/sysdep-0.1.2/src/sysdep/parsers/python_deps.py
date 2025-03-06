# sysdep/parsers/python_deps.py
import os
import re
from typing import Dict, List, Optional, Set

def parse_requirements_txt(file_path: str) -> List[str]:
    """
    Parse a requirements.txt file and extract package names.
    
    Args:
        file_path: Path to requirements.txt file
        
    Returns:
        List of package names
    """
    if not os.path.exists(file_path):
        return []
        
    packages = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
                
            # Skip options like --extra-index-url
            if line.startswith('-'):
                continue
                
            # Skip URLs and other non-standard formats
            if line.startswith('http') or line.startswith('git+'):
                continue
                
            # Extract the package name (without version specifier)
            package_name = re.split(r'[=<>~!]', line)[0].strip()
            packages.append(package_name)
                
    return packages

def parse_pyproject_toml(file_path: str) -> List[str]:
    """
    Parse a pyproject.toml file and extract package names.
    
    Args:
        file_path: Path to pyproject.toml file
        
    Returns:
        List of package names
    """
    if not os.path.exists(file_path):
        return []
        
    try:
        import tomli
    except ImportError:
        try:
            import tomllib as tomli
        except ImportError:
            # Fallback to a simple parser for older Python versions
            return _simple_parse_pyproject_toml(file_path)
            
    with open(file_path, 'rb') as f:
        data = tomli.load(f)
        
    packages = []
    
    # Handle different pyproject.toml formats
    
    # Poetry dependencies
    if 'tool' in data and 'poetry' in data['tool'] and 'dependencies' in data['tool']['poetry']:
        for pkg, ver in data['tool']['poetry']['dependencies'].items():
            if pkg != 'python':  # Skip python version specifier
                packages.append(pkg)
                
    # PEP 621 dependencies
    elif 'project' in data and 'dependencies' in data['project']:
        deps = data['project']['dependencies']
        for dep in deps:
            # Extract just the package name
            pkg = re.split(r'[=<>~!]', dep)[0].strip()
            packages.append(pkg)
            
    # setuptools dependencies
    elif 'build-system' in data and 'requires' in data['build-system']:
        for req in data['build-system']['requires']:
            if req != 'setuptools' and req != 'wheel':
                pkg = re.split(r'[=<>~!]', req)[0].strip()
                packages.append(pkg)
                
    return packages

def _simple_parse_pyproject_toml(file_path: str) -> List[str]:
    """
    Simple fallback parser for pyproject.toml without requiring tomli.
    """
    packages = []
    dependencies_section = False
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Check if we're in the dependencies section
            if line.startswith('[') and 'dependencies' in line:
                dependencies_section = True
                continue
            elif line.startswith('[') and dependencies_section:
                dependencies_section = False
                
            # Skip non-dependencies
            if not dependencies_section:
                continue
                
            # Parse dependency lines (very simplified)
            if '=' in line:
                package = line.split('=')[0].strip().strip('"\'')
                if package != 'python':
                    packages.append(package)
                    
    return packages

def parse_setup_py(file_path: str) -> List[str]:
    """
    Parse a setup.py file and extract package names.
    Note: This is a very simplified parser and might not work for complex setup.py files.
    
    Args:
        file_path: Path to setup.py file
        
    Returns:
        List of package names
    """
    if not os.path.exists(file_path):
        return []
        
    with open(file_path, 'r') as f:
        content = f.read()
        
    # Look for install_requires list/array
    pattern = r'install_requires\s*=\s*\[(.*?)\]'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return []
        
    # Extract package names from the matched string
    deps_str = match.group(1)
    
    # Split by commas and clean up
    deps = []
    for dep in re.findall(r'["\']([^"\']+)["\']', deps_str):
        # Extract just the package name
        pkg = re.split(r'[=<>~!]', dep)[0].strip()
        deps.append(pkg)
        
    return deps

def get_python_dependencies(project_dir: str) -> List[str]:
    """
    Scan a project directory for Python dependencies.
    
    Args:
        project_dir: Path to project directory
        
    Returns:
        List of Python package names
    """
    packages = []
    
    # Try to parse pyproject.toml
    pyproject_path = os.path.join(project_dir, 'pyproject.toml')
    if os.path.exists(pyproject_path):
        packages.extend(parse_pyproject_toml(pyproject_path))
        
    # Try to parse requirements.txt
    req_path = os.path.join(project_dir, 'requirements.txt')
    if os.path.exists(req_path):
        packages.extend(parse_requirements_txt(req_path))
        
    # Try to parse setup.py
    setup_path = os.path.join(project_dir, 'setup.py')
    if os.path.exists(setup_path):
        packages.extend(parse_setup_py(setup_path))
        
    # Remove duplicates while preserving order
    seen = set()
    result = []
    for pkg in packages:
        if pkg not in seen:
            seen.add(pkg)
            result.append(pkg)
            
    return result