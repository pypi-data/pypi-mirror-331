#!/usr/bin/env python
"""
Integration test script for FlatForge and FlatForgeUI packages.

This script verifies that both packages can be imported and
that key modules are accessible.

Author: Akram Zaki (azpythonprojects@gmail.com)
"""

import sys
import importlib.util


def check_package(package_name, modules_to_check=None):
    """
    Check if a package can be imported and verify specific modules.
    
    Args:
        package_name (str): Name of the package to check
        modules_to_check (list): List of module names to verify
        
    Returns:
        bool: True if package and all modules can be imported, False otherwise
    """
    try:
        # Try to import the package
        package = __import__(package_name)
        print(f"✅ Successfully imported '{package_name}'")
        
        # Check specific modules if provided
        if modules_to_check:
            for module_name in modules_to_check:
                full_module_name = f"{package_name}.{module_name}"
                try:
                    module = __import__(full_module_name, fromlist=[module_name])
                    print(f"✅ Successfully imported '{full_module_name}'")
                except ImportError as e:
                    print(f"❌ Error importing '{full_module_name}': {str(e)}")
                    return False
        
        return True
    except ImportError as e:
        print(f"❌ Error importing '{package_name}': {str(e)}")
        return False


def main():
    """Run the integration tests."""
    print("Testing FlatForge packages...")
    print("-" * 40)
    
    # Check FlatForge package
    flatforge_ok = check_package("flatforge", ["utils", "config_parser", "processor"])
    
    # Check FlatForgeUI package
    flatforge_ui_ok = check_package("flatforge_ui", ["config_editor"])
    
    print("-" * 40)
    
    # Report overall status
    if flatforge_ok and flatforge_ui_ok:
        print("✅ Both packages are working correctly!")
        return 0
    else:
        print("❌ Both packages have issues")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 