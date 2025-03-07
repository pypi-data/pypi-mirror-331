# sysdep/setuptools_integration.py
import os
import sys
import warnings
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools import Command

from . import check_dependencies
from .parsers.manifest import parse_manifest_file
from .utils import print_dependency_report

class SysdepCommand(Command):
    """Custom setuptools command to check system dependencies."""
    
    description = "Check system dependencies required by the package"
    user_options = [
        ('manifest-file=', 'm', 'Path to dependency manifest file'),
        ('strict', 's', 'Fail installation if dependencies are missing'),
    ]
    
    def initialize_options(self):
        self.manifest_file = None
        self.strict = False
        
    def finalize_options(self):
        if not self.manifest_file:
            # Look for default manifest file
            if os.path.exists('system_requirements.txt'):
                self.manifest_file = 'system_requirements.txt'
            
    def run(self):
        if not self.manifest_file:
            warnings.warn("No system dependency manifest file found. Skipping dependency check.")
            return
            
        # Parse and check dependencies
        dependencies = parse_manifest_file(self.manifest_file)
        
        if not dependencies:
            self.announce("No system dependencies specified.")
            return
            
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
                
        # Print results
        print_dependency_report(results)
        
        # Fail if strict mode is enabled and dependencies are missing
        if self.strict and not results["all_installed"]:
            sys.exit(1)

class SysdepInstallCommand(install):
    """Custom install command that checks system dependencies before installation."""
    
    def run(self):
        # Run sysdep command first
        self.run_command('sysdep')
        # Then run the original install command
        install.run(self)

class SysdepDevelopCommand(develop):
    """Custom develop command that checks system dependencies before installation."""
    
    def run(self):
        # Run sysdep command first
        self.run_command('sysdep')
        # Then run the original develop command
        develop.run(self)

def setup_integration(setup_kwargs):
    """
    Integrate sysdep with setuptools.
    
    Usage in setup.py:
    
    from sysdep.setuptools_integration import setup_integration
    
    setup_kwargs = {
        'name': 'your-package',
        'version': '0.1.0',
        # other setup arguments...
    }
    
    setup_integration(setup_kwargs)
    setup(**setup_kwargs)
    """
    # Register commands
    cmdclass = setup_kwargs.get('cmdclass', {})
    cmdclass.update({
        'sysdep': SysdepCommand,
        'install': SysdepInstallCommand,
        'develop': SysdepDevelopCommand,
    })
    setup_kwargs['cmdclass'] = cmdclass