# sysdep/cli.py
# Standard library imports
import argparse
import json
import os
import sys
from typing import Dict, List, Optional, Any

# Local imports
from . import check_dependencies, __version__
from .parsers.code_scanner import DependencyScanner
from .parsers.manifest import parse_manifest_file
from .parsers.python_deps import (
    get_python_dependencies,
    parse_requirements_txt
)
from .platforms import get_platform_manager
from .utils import Colors, print_dependency_report, install_dependencies, DEFAULT_WORKERS
from .mappers import map_python_to_system_dependencies, print_dependency_mapping

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Check and manage system dependencies for Python projects.\n"
                    "For the best experience with progress bars, install with: pip install sysdep[ui]"
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'%(prog)s {__version__}'
    )
    
    # Add global options
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Disable progress bars for operations'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=DEFAULT_WORKERS,
        help=f'Number of parallel workers (default: {DEFAULT_WORKERS})'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check dependencies')
    check_parser.add_argument(
        '-f', '--file', 
        help='Path to dependency manifest file'
    )
    check_parser.add_argument(
        '-d', '--dir', 
        help='Scan directory for dependency annotations in Python files'
    )
    check_parser.add_argument(
        '-j', '--json', 
        action='store_true',
        help='Output results as JSON'
    )
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install dependencies')
    install_parser.add_argument(
        '-f', '--file', 
        help='Path to dependency manifest file'
    )
    install_parser.add_argument(
        '-d', '--dir', 
        help='Scan directory for dependency annotations in Python files'
    )
    install_parser.add_argument(
        '-y', '--yes', 
        action='store_true',
        help='Answer yes to all prompts'
    )
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate a dependency manifest file')
    generate_parser.add_argument(
        'directory', 
        nargs='?', 
        default='.',
        help='Directory to scan for Python files'
    )
    generate_parser.add_argument(
        '-o', '--output', 
        default='system_requirements.txt',
        help='Output manifest file path'
    )
    generate_parser.add_argument(
        '-p', '--from-python-deps',
        action='store_true',
        help='Generate from Python dependencies (requirements.txt, pyproject.toml, setup.py)'
    )
    generate_parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Force overwrite existing file'
    )
    
    # Map command
    map_parser = subparsers.add_parser('map', help='Show system dependencies for Python packages')
    map_parser.add_argument(
        'packages',
        nargs='*',
        help='Python package names to map'
    )
    map_parser.add_argument(
        '-f', '--file',
        help='Path to requirements.txt file'
    )
    map_parser.add_argument(
        '-d', '--dir',
        help='Project directory containing dependency files'
    )
    
    args = parser.parse_args()
    show_progress = not args.no_progress
    max_workers = args.workers
    
    if not args.command:
        parser.print_help()
        return 1
        
    try:
        if args.command == 'check':
            if args.dir:
                # Check dependencies from code annotations
                scanner = DependencyScanner()
                dependencies = scanner.scan_directory(
                    args.dir,
                    show_progress=show_progress,
                    max_workers=max_workers
                )
                
                # Convert to the same format as check_dependencies returns
                results = {
                    "all_installed": True,
                    "dependencies": [],
                    "missing": []
                }
                
                for dep in dependencies:
                    info = dep.get_installation_info()
                    results["dependencies"].append(info)
                    
                    if not info["installed"]:
                        results["all_installed"] = False
                        results["missing"].append(info)
            else:
                # Check dependencies from manifest file
                results = check_dependencies(
                    args.file,
                    show_progress=show_progress,
                    max_workers=max_workers
                )
            
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print_dependency_report(results)
                
            if not results["all_installed"]:
                sys.exit(1)
        elif args.command == 'install':
            if args.dir:
                # Install dependencies from code annotations
                scanner = DependencyScanner()
                dependencies = scanner.scan_directory(
                    args.dir,
                    show_progress=show_progress,
                    max_workers=max_workers
                )
                
                # Get installation info for each dependency
                to_install = []
                for dep in dependencies:
                    info = dep.get_installation_info()
                    if not info["installed"]:
                        to_install.append(info)
            else:
                # Install dependencies from manifest file
                results = check_dependencies(
                    args.file,
                    show_progress=show_progress,
                    max_workers=max_workers
                )
                to_install = results["missing"]
                
            if to_install:
                print(f"\n{Colors.BOLD}Found {len(to_install)} missing dependencies{Colors.ENDC}\n")
                
                # Prompt user to continue
                if not args.yes:
                    answer = input(f"Install {len(to_install)} dependencies? [y/N] ")
                    if answer.lower() != 'y':
                        print("Aborted")
                        return 1
                
                # Install dependencies
                install_dependencies(to_install, show_progress=show_progress, max_workers=max_workers)
            else:
                print(f"\n{Colors.GREEN}✓ All dependencies are already installed!{Colors.ENDC}\n")
        elif args.command == 'generate':
            # Check if output file exists and not forced to overwrite
            if os.path.exists(args.output) and not args.force:
                print(f"Error: Output file '{args.output}' already exists. Use -f to force overwrite.")
                return 1
                
            if args.from_python_deps:
                # Generate from Python dependencies
                if not os.path.exists(args.directory):
                    print(f"Error: Directory '{args.directory}' does not exist.")
                    return 1
                    
                # Parse Python dependencies from requirements.txt, pyproject.toml, etc.
                python_deps = get_python_dependencies(args.directory)
                
                print(f"{Colors.BOLD}Found {len(python_deps)} Python packages{Colors.ENDC}")
                if not python_deps:
                    print(f"{Colors.YELLOW}Warning: No Python dependencies found{Colors.ENDC}")
                    return 0
                
                # Map Python dependencies to system dependencies
                system_deps = map_python_to_system_dependencies(
                    python_deps,
                    show_progress=show_progress,
                    max_workers=max_workers
                )
                
                if not system_deps:
                    print(f"{Colors.YELLOW}Warning: No system dependencies mapped from Python packages{Colors.ENDC}")
                    return 0
                
                # Write to file
                with open(args.output, 'w') as f:
                    f.write("# System dependencies generated from Python packages\n")
                    f.write("# Generated with sysdep\n\n")
                    
                    for dep in system_deps:
                        # Handle both dictionary-style dependencies and class instances
                        if hasattr(dep, 'to_manifest_line'):
                            # Class instance with to_manifest_line method
                            f.write(f"{dep.to_manifest_line()}\n")
                        elif hasattr(dep, 'name'):
                            # Class instance with attributes
                            dep_type = dep.__class__.__name__.lower().replace('dependency', '')
                            version_str = f" >= {dep.version}" if hasattr(dep, 'version') and dep.version else ""
                            f.write(f"{dep_type}: {dep.name}{version_str}\n")
                        elif isinstance(dep, dict):
                            # Dictionary-style dependency
                            if dep.get('version'):
                                f.write(f"{dep['type']}: {dep['name']} >= {dep['version']}\n")
                            else:
                                f.write(f"{dep['type']}: {dep['name']}\n")
                
                print(f"{Colors.GREEN}✓ Mapped {len(system_deps)} system dependencies to {args.output}{Colors.ENDC}")
            else:
                # Generate from code annotations
                scanner = DependencyScanner()
                dependencies = scanner.scan_directory(args.directory, show_progress=show_progress)
                
                if not dependencies:
                    print(f"{Colors.YELLOW}Warning: No dependency annotations found in {args.directory}{Colors.ENDC}")
                    return 0
                
                # Write to file
                with open(args.output, 'w') as f:
                    f.write("# System dependencies generated from code annotations\n")
                    f.write("# Generated with sysdep\n\n")
                    
                    for dep in dependencies:
                        info = dep.to_manifest_line()
                        f.write(f"{info}\n")
                
                print(f"{Colors.GREEN}✓ Generated manifest with {len(dependencies)} dependencies to {args.output}{Colors.ENDC}")
                
            return 0
        elif args.command == 'map':
            python_deps = []
            
            # Parse packages from command line arguments
            if args.packages:
                python_deps.extend(args.packages)
            
            # Parse packages from requirements.txt file
            if args.file:
                if not os.path.exists(args.file):
                    print(f"Error: File '{args.file}' does not exist.")
                    return 1
                    
                packages = parse_requirements_txt(args.file)
                python_deps.extend(packages)
            
            # Parse packages from project directory
            if args.dir:
                if not os.path.exists(args.dir):
                    print(f"Error: Directory '{args.dir}' does not exist.")
                    return 1
                    
                packages = get_python_dependencies(args.dir)
                python_deps.extend(packages)
            
            if not python_deps:
                print("Error: No Python packages specified. Use command line arguments, -f, or -d.")
                return 1
            
            # Map Python dependencies to system dependencies
            system_deps = map_python_to_system_dependencies(python_deps, show_progress=show_progress)
            
            # Print the mapping
            print_dependency_mapping(python_deps, system_deps)
            
            return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
        
    return 0

def cmd_check(args):
    """Run the check command."""
    dependencies = []
    
    # Parse manifest file if provided
    if args.file:
        dependencies.extend(parse_manifest_file(args.file))
    
    # Scan directory if provided
    if args.dir:
        scanner = DependencyScanner()
        dependencies.extend(scanner.scan_directory(args.dir))
        
    # Check dependencies
    results = {
        "all_installed": True,
        "dependencies": [],
        "missing": []
    }
    
    for dep in dependencies:
        info = dep.get_installation_info()
        results["dependencies"].append(info)
        
        if not info["installed"]:
            results["all_installed"] = False
            results["missing"].append(info)
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_dependency_report(results)
        
    return 0 if results["all_installed"] else 1

def cmd_install(args):
    """Run the install command."""
    dependencies = []
    
    # Parse manifest file if provided
    if args.file:
        dependencies.extend(parse_manifest_file(args.file))
    
    # Scan directory if provided
    if args.dir:
        scanner = DependencyScanner()
        dependencies.extend(scanner.scan_directory(args.dir))
        
    # Check dependencies
    missing_deps = []
    for dep in dependencies:
        info = dep.get_installation_info()
        if not info["installed"]:
            missing_deps.append(info)
            
    # Install missing dependencies
    if not missing_deps:
        print(f"\n  {Colors.BOLD}{Colors.GREEN}✓ All dependencies are already installed!{Colors.ENDC}\n")
        return 0
        
    print(f"\n  {Colors.BOLD}{Colors.CYAN}⚡ Installation Required{Colors.ENDC}")
    print(f"  {Colors.BOLD}Found {len(missing_deps)} missing dependencies:{Colors.ENDC}")
    for dep in missing_deps:
        print(f"    {Colors.YELLOW}◆{Colors.ENDC} {dep['name']}")
        
    if not args.yes:
        response = input(f"\n  {Colors.BOLD}Do you want to install these dependencies? [y/N]{Colors.ENDC} ")
        if response.lower() not in ('y', 'yes'):
            print(f"\n  {Colors.YELLOW}Installation cancelled.{Colors.ENDC}")
            return 1
            
    success = install_dependencies(missing_deps)
    return 0 if success else 1

def cmd_generate(args):
    """Run the generate command."""
    if args.from_python_deps:
        try:
            from .generators.requirements_generator import generate_system_requirements
            output_path = generate_system_requirements(
                args.directory, 
                output_file=args.output, 
                overwrite=args.force
            )
            print(f"\n  {Colors.BOLD}{Colors.GREEN}✓ System requirements file generated!{Colors.ENDC}")
            print(f"    Location: {Colors.CYAN}{output_path}{Colors.ENDC}")
            print(f"\n  {Colors.BOLD}Generated from:{Colors.ENDC}")
            print(f"    {Colors.YELLOW}◆{Colors.ENDC} {args.directory}/requirements.txt")
            print(f"    {Colors.YELLOW}◆{Colors.ENDC} {args.directory}/pyproject.toml")
            print(f"    {Colors.YELLOW}◆{Colors.ENDC} {args.directory}/setup.py\n")
            return 0
        except FileExistsError:
            print(f"\n  {Colors.BOLD}{Colors.RED}Error:{Colors.ENDC} Output file {Colors.CYAN}{args.output}{Colors.ENDC} already exists.")
            print(f"  Use {Colors.YELLOW}--force{Colors.ENDC} to overwrite.\n")
            return 1
        except ValueError as e:
            print(f"\n  {Colors.BOLD}{Colors.RED}Error:{Colors.ENDC} {e}\n")
            return 1
    else:
        # Original behavior - scan for annotations
        scanner = DependencyScanner()
        dependencies = scanner.scan_directory(args.directory)
        
        if not dependencies:
            print(f"\n  {Colors.BOLD}{Colors.YELLOW}No dependency annotations found in {args.directory}.{Colors.ENDC}\n")
            return 1
            
        if os.path.exists(args.output) and not args.force:
            print(f"\n  {Colors.BOLD}{Colors.RED}Error:{Colors.ENDC} Output file {Colors.CYAN}{args.output}{Colors.ENDC} already exists.")
            print(f"  Use {Colors.YELLOW}--force{Colors.ENDC} to overwrite.\n")
            return 1
            
        with open(args.output, 'w') as f:
            f.write("# System dependencies for this project\n")
            f.write("# Generated by sysdep from code annotations\n\n")
            
            for dep in sorted(dependencies, key=lambda d: d.name):
                if dep.version:
                    f.write(f"executable: {dep.name} >= {dep.version}\n")
                else:
                    f.write(f"executable: {dep.name}\n")
                    
        print(f"\n  {Colors.BOLD}{Colors.GREEN}✓ Manifest file generated!{Colors.ENDC}")
        print(f"    Location: {Colors.CYAN}{args.output}{Colors.ENDC}\n")
        return 0

def cmd_map(args):
    """Run the map command to show system dependencies for Python packages."""
    packages = []
    
    # Get packages from command line arguments
    if args.packages:
        packages.extend(args.packages)
        
    # Get packages from requirements.txt file
    if args.file:
        if not os.path.exists(args.file):
            print(f"\n  {Colors.BOLD}{Colors.RED}Error:{Colors.ENDC} Requirements file {Colors.CYAN}{args.file}{Colors.ENDC} not found.\n")
            return 1
        file_packages = parse_requirements_txt(args.file)
        if file_packages:
            print(f"  {Colors.BOLD}Found {len(file_packages)} packages in {Colors.CYAN}{args.file}{Colors.ENDC}")
        else:
            print(f"  {Colors.YELLOW}No packages found in {args.file}{Colors.ENDC}")
            
    # Get packages from project directory
    if args.dir:
        if not os.path.exists(args.dir):
            print(f"\n  {Colors.BOLD}{Colors.RED}Error:{Colors.ENDC} Directory {Colors.CYAN}{args.dir}{Colors.ENDC} not found.\n")
            return 1
        dir_packages = get_python_dependencies(args.dir)
        if dir_packages:
            print(f"  {Colors.BOLD}Found {len(dir_packages)} packages in {Colors.CYAN}{args.dir}{Colors.ENDC}")
        else:
            print(f"  {Colors.YELLOW}No packages found in {args.dir}{Colors.ENDC}")
            
    # Remove duplicates
    packages = list(dict.fromkeys(packages))
    
    if not packages:
        print(f"\n  {Colors.BOLD}{Colors.RED}Error:{Colors.ENDC} No Python packages specified.")
        print(f"  Use {Colors.YELLOW}--file{Colors.ENDC} to specify a requirements.txt file,")
        print(f"  {Colors.YELLOW}--dir{Colors.ENDC} to scan a project directory,")
        print(f"  or provide package names as arguments.\n")
        return 1
    
    # Print mapping
    print_dependency_mapping(packages)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())