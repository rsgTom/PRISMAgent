#!/usr/bin/env python3
"""
Test Scaffolding Generator for PRISMAgent

This script analyzes the codebase to identify untested components and
generates test skeletons for them. It helps ensure test coverage for all
parts of the codebase.

Usage:
    python test_scaffolding.py [--module MODULE] [--output OUTPUT]

Options:
    --module MODULE    Specific module to generate tests for (e.g., engine, storage)
    --output OUTPUT    Output directory for generated tests (default: tests/)
"""

import ast
import sys
import os
import argparse
import importlib
import inspect
from typing import Dict, List, Set, Tuple, Optional, Any
from pathlib import Path


class FunctionInfo:
    """Information about a function or method."""
    
    def __init__(self, name: str, params: List[str], is_async: bool, 
                 docstring: Optional[str], module: str, cls: Optional[str] = None):
        self.name = name
        self.params = params
        self.is_async = is_async
        self.docstring = docstring
        self.module = module
        self.cls = cls
    
    def __str__(self) -> str:
        prefix = "async " if self.is_async else ""
        return f"{prefix}def {self.name}({', '.join(self.params)})"
    
    def get_full_name(self) -> str:
        """Returns the fully qualified name of the function."""
        if self.cls:
            return f"{self.module}.{self.cls}.{self.name}"
        return f"{self.module}.{self.name}"


class ClassInfo:
    """Information about a class."""
    
    def __init__(self, name: str, methods: List[FunctionInfo], module: str,
                 bases: List[str], docstring: Optional[str]):
        self.name = name
        self.methods = methods
        self.module = module
        self.bases = bases
        self.docstring = docstring
    
    def __str__(self) -> str:
        return f"class {self.name}({', '.join(self.bases)})"
    
    def get_full_name(self) -> str:
        """Returns the fully qualified name of the class."""
        return f"{self.module}.{self.name}"


class ModuleVisitor(ast.NodeVisitor):
    """AST visitor that collects information about module contents."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
        self.current_class: Optional[str] = None
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{base.value.id}.{base.attr}")
            else:
                bases.append("object")
        
        # Store current class name for method context
        prev_class = self.current_class
        self.current_class = node.name
        
        # Visit methods first so they are collected
        methods_before = len(self.functions)
        self.generic_visit(node)
        methods_after = len(self.functions)
        
        # Get methods added during the visit
        methods = self.functions[methods_before:methods_after]
        
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Create class info
        self.classes.append(
            ClassInfo(node.name, methods, self.module_name, bases, docstring)
        )
        
        # Restore previous class context
        self.current_class = prev_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        self._process_function(node, is_async=False)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        self._process_function(node, is_async=True)
    
    def _process_function(self, node: ast.FunctionDef, is_async: bool) -> None:
        """Process function or method definition."""
        params = []
        
        # Skip 'self' or 'cls' for instance/class methods
        skip_first = False
        if self.current_class and node.args.args and node.args.args[0].arg in ('self', 'cls'):
            skip_first = True
        
        # Get parameters
        for i, arg in enumerate(node.args.args):
            if i == 0 and skip_first:
                continue
            params.append(arg.arg)
        
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Create function info
        self.functions.append(
            FunctionInfo(node.name, params, is_async, docstring, 
                        self.module_name, self.current_class)
        )


def find_python_modules(root_dir: str, base_package: str) -> List[str]:
    """Find all Python modules in the given directory."""
    modules = []
    root_path = Path(root_dir)
    
    for path in root_path.rglob("*.py"):
        # Convert path to module name
        rel_path = path.relative_to(root_path.parent)
        module_name = str(rel_path).replace(os.sep, ".")[:-3]  # Remove .py
        
        # Skip __init__.py files
        if module_name.endswith("__init__"):
            module_name = module_name[:-9]
        
        if module_name:
            modules.append(module_name)
    
    return modules


def find_test_modules(test_dir: str) -> Set[str]:
    """Find all test modules and extract what they're testing."""
    tested_items = set()
    test_path = Path(test_dir)
    
    for path in test_path.rglob("test_*.py"):
        try:
            with open(path, "r") as f:
                tree = ast.parse(f.read())
                
                # Simple heuristic: look for import statements
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            tested_items.add(name.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            for name in node.names:
                                tested_items.add(f"{node.module}.{name.name}")
        except Exception as e:
            print(f"Error parsing {path}: {e}")
    
    return tested_items


def analyze_module(module_name: str) -> Tuple[List[FunctionInfo], List[ClassInfo]]:
    """Analyze a Python module to extract classes and functions."""
    try:
        # Try to import the module
        module = importlib.import_module(module_name)
        file_path = inspect.getfile(module)
        
        # Parse the module file
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())
            visitor = ModuleVisitor(module_name)
            visitor.visit(tree)
            
            return visitor.functions, visitor.classes
    except ImportError:
        print(f"Could not import module {module_name}")
        return [], []
    except Exception as e:
        print(f"Error analyzing module {module_name}: {e}")
        return [], []


def generate_test_file(module_name: str, functions: List[FunctionInfo], 
                      classes: List[ClassInfo], output_dir: str) -> None:
    """Generate a test file for the given module."""
    # Create test directory structure
    module_parts = module_name.split(".")
    test_dir = os.path.join(output_dir, *module_parts[:-1])
    os.makedirs(test_dir, exist_ok=True)
    
    # Generate test file path
    test_file = os.path.join(test_dir, f"test_{module_parts[-1]}.py")
    
    # Skip if test file already exists
    if os.path.exists(test_file):
        print(f"Test file already exists: {test_file}")
        return
    
    print(f"Generating test file: {test_file}")
    
    # Generate file content
    content = [
        f'"""\'',
        f'Unit tests for {module_name}',
        f'"""\'',
        "",
        "import pytest",
        "from unittest.mock import patch, MagicMock",
        "",
        f"from {module_name} import *",
        "",
    ]
    
    # Add test functions for classes
    for cls in classes:
        content.append(f"# Tests for {cls.name}")
        content.append("")
        
        # Class setup
        content.append(f"class Test{cls.name}:")
        content.append("")
        content.append("    @pytest.fixture")
        content.append(f"    def {cls.name.lower()}_instance(self):")
        content.append(f"        # TODO: Set up an instance of {cls.name}")
        content.append(f"        return {cls.name}()")
        content.append("")
        
        # Test methods
        for method in cls.methods:
            # Skip private methods
            if method.name.startswith("_") and not method.name.startswith("__"):
                continue
            
            # Generate test method name
            test_name = f"test_{method.name}"
            
            # Create test method
            content.append(f"    def {test_name}(self, {cls.name.lower()}_instance):")
            if method.docstring:
                content.append(f'        """{method.docstring}"""')
            content.append(f"        # TODO: Test {method.name} method")
            content.append(f"        # result = {cls.name.lower()}_instance.{method.name}()")
            content.append(f"        # assert result is not None")
            content.append("")
    
    # Add test functions for standalone functions
    for func in functions:
        # Skip private functions
        if func.name.startswith("_") and not func.name.startswith("__"):
            continue
        
        # Skip class methods (already handled)
        if func.cls:
            continue
        
        # Generate test function name
        test_name = f"test_{func.name}"
        
        # Create test function
        content.append(f"def {test_name}():")
        if func.docstring:
            content.append(f'    """{func.docstring}"""')
        content.append(f"    # TODO: Test {func.name} function")
        
        # Add example of mocking if it looks like it might use external services
        if any(ext in func.name for ext in ["api", "client", "http", "request", "fetch"]):
            content.append(f"    # with patch('{module_name}.some_dependency') as mock_dep:")
            content.append(f"    #     mock_dep.return_value = 'test_value'")
            content.append(f"    #     result = {func.name}()")
            content.append(f"    #     assert result is not None")
        else:
            content.append(f"    # result = {func.name}()")
            content.append(f"    # assert result is not None")
        content.append("")
    
    # Write test file
    with open(test_file, "w") as f:
        f.write("\n".join(content))


def main():
    parser = argparse.ArgumentParser(description="Generate test scaffolding")
    parser.add_argument("--module", help="Specific module to generate tests for")
    parser.add_argument("--output", default="tests", help="Output directory for tests")
    args = parser.parse_args()
    
    print("Test Scaffolding Generator for PRISMAgent")
    print("=========================================")
    
    # Find the src directory
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(repo_dir, "src")
    test_dir = os.path.join(repo_dir, args.output)
    
    if not os.path.exists(src_dir):
        print(f"Error: Source directory not found at {src_dir}")
        sys.exit(1)
    
    # Add src to Python path to allow importing modules
    sys.path.insert(0, os.path.dirname(src_dir))
    
    # Find modules to analyze
    base_package = "PRISMAgent"
    if args.module:
        modules = [f"{base_package}.{args.module}"]
    else:
        modules = find_python_modules(src_dir, base_package)
    
    print(f"Found {len(modules)} modules to analyze")
    
    # Find already tested modules
    tested_items = find_test_modules(test_dir)
    print(f"Found {len(tested_items)} items already tested")
    
    # Count stats
    untested_modules = 0
    generated_files = 0
    
    # Analyze modules and generate test files
    for module_name in modules:
        # Skip if module is already tested
        if module_name in tested_items:
            continue
        
        print(f"Analyzing {module_name}...")
        functions, classes = analyze_module(module_name)
        
        if functions or classes:
            untested_modules += 1
            generate_test_file(module_name, functions, classes, test_dir)
            generated_files += 1
    
    print(f"\nSummary:")
    print(f"- Found {untested_modules} untested modules")
    print(f"- Generated {generated_files} test files")
    print(f"- Test files written to {test_dir}")


if __name__ == "__main__":
    main()