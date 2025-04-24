#!/usr/bin/env python3
"""
Parameter Audit Tool for PRISMAgent

This script analyzes the codebase to identify parameter mismatches
between function definitions and their call sites. It helps detect
inconsistencies that could lead to runtime errors.

Usage:
    python parameter_audit.py [--fix]

Options:
    --fix    Generate suggested fixes for identified issues
"""

import ast
import sys
import os
import argparse
from typing import Dict, List, Set, Tuple, Optional, Any
from pathlib import Path


class FunctionDef:
    """Represents a function definition with its parameters."""
    
    def __init__(self, name: str, params: List[str], defaults: List[Any], 
                 file_path: str, line_num: int):
        self.name = name
        self.params = params
        self.defaults = defaults
        self.file_path = file_path
        self.line_num = line_num
        
    def __str__(self) -> str:
        return f"{self.name}({', '.join(self.params)})"
    
    def get_location(self) -> str:
        """Returns a human-readable location string."""
        return f"{self.file_path}:{self.line_num}"


class FunctionCall:
    """Represents a function call with its arguments."""
    
    def __init__(self, name: str, args: List[str], kwargs: Dict[str, str], 
                 file_path: str, line_num: int):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.file_path = file_path
        self.line_num = line_num
        
    def __str__(self) -> str:
        args_str = ", ".join(self.args)
        kwargs_str = ", ".join([f"{k}={v}" for k, v in self.kwargs.items()])
        all_args = [s for s in [args_str, kwargs_str] if s]
        return f"{self.name}({', '.join(all_args)})"
    
    def get_location(self) -> str:
        """Returns a human-readable location string."""
        return f"{self.file_path}:{self.line_num}"


class FunctionVisitor(ast.NodeVisitor):
    """AST visitor that collects function definitions and calls."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.functions: List[FunctionDef] = []
        self.calls: List[FunctionCall] = []
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        params = []
        defaults = []
        
        # Get positional parameters
        for arg in node.args.args:
            params.append(arg.arg)
        
        # Get default values
        for default in node.args.defaults:
            if isinstance(default, ast.Constant):
                defaults.append(default.value)
            else:
                defaults.append("unknown")
        
        # Add *args if present
        if node.args.vararg:
            params.append(f"*{node.args.vararg.arg}")
        
        # Add **kwargs if present
        if node.args.kwarg:
            params.append(f"**{node.args.kwarg.arg}")
        
        self.functions.append(
            FunctionDef(node.name, params, defaults, self.file_path, node.lineno)
        )
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls."""
        # Get function name
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        else:
            self.generic_visit(node)
            return
        
        # Get positional arguments
        args = []
        for arg in node.args:
            if isinstance(arg, ast.Constant):
                args.append(str(arg.value))
            elif isinstance(arg, ast.Name):
                args.append(arg.id)
            else:
                args.append("complex_expr")
        
        # Get keyword arguments
        kwargs = {}
        for kwarg in node.keywords:
            if isinstance(kwarg.value, ast.Constant):
                kwargs[kwarg.arg] = str(kwarg.value.value)
            elif isinstance(kwarg.value, ast.Name):
                kwargs[kwarg.arg] = kwarg.value.id
            else:
                kwargs[kwarg.arg] = "complex_expr"
        
        self.calls.append(
            FunctionCall(func_name, args, kwargs, self.file_path, node.lineno)
        )
        
        self.generic_visit(node)


def find_python_files(root_dir: str) -> List[str]:
    """Find all Python files in the given directory."""
    files = []
    for path in Path(root_dir).rglob("*.py"):
        files.append(str(path))
    return files


def analyze_file(file_path: str) -> Tuple[List[FunctionDef], List[FunctionCall]]:
    """Analyze a Python file to extract function definitions and calls."""
    with open(file_path, "r") as f:
        try:
            tree = ast.parse(f.read())
            visitor = FunctionVisitor(file_path)
            visitor.visit(tree)
            return visitor.functions, visitor.calls
        except SyntaxError:
            print(f"Syntax error in {file_path}, skipping")
            return [], []


def find_mismatches(all_functions: Dict[str, List[FunctionDef]], 
                    all_calls: Dict[str, List[FunctionCall]]) -> Dict[str, List[str]]:
    """Find parameter mismatches between function definitions and calls."""
    mismatches = {}
    
    for func_name, calls in all_calls.items():
        # Skip if no functions found with this name
        if func_name not in all_functions:
            continue
        
        defs = all_functions[func_name]
        if not defs:
            continue
        
        # Use the first definition as reference (could improve to check all)
        func_def = defs[0]
        
        for call in calls:
            issues = []
            
            # Check for missing required parameters
            required_params = func_def.params[:len(func_def.params) - len(func_def.defaults)]
            provided_params = set(call.args)
            provided_params.update(call.kwargs.keys())
            
            # Skip *args and **kwargs from required check
            required_params = [p for p in required_params if not p.startswith("*")]
            
            for param in required_params:
                if param not in provided_params:
                    issues.append(f"Missing required parameter: {param}")
            
            # Check for unknown parameters
            valid_params = set(func_def.params)
            for kwarg in call.kwargs:
                if kwarg not in valid_params and "**" not in "".join(func_def.params):
                    issues.append(f"Unknown parameter: {kwarg}")
            
            if issues:
                key = f"{func_name} at {call.get_location()}"
                mismatches[key] = issues
    
    return mismatches


def main():
    parser = argparse.ArgumentParser(description="Audit function parameter mismatches")
    parser.add_argument("--fix", action="store_true", help="Generate suggested fixes")
    args = parser.parse_args()
    
    print("Parameter Audit Tool for PRISMAgent")
    print("===================================")
    
    # Find the src directory
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(repo_dir, "src")
    
    if not os.path.exists(src_dir):
        print(f"Error: Source directory not found at {src_dir}")
        sys.exit(1)
    
    print(f"Analyzing source code in {src_dir}...")
    
    # Find all Python files
    python_files = find_python_files(src_dir)
    print(f"Found {len(python_files)} Python files")
    
    # Analyze files
    all_functions = {}
    all_calls = {}
    
    for file_path in python_files:
        functions, calls = analyze_file(file_path)
        
        for func in functions:
            if func.name not in all_functions:
                all_functions[func.name] = []
            all_functions[func.name].append(func)
        
        for call in calls:
            if call.name not in all_calls:
                all_calls[call.name] = []
            all_calls[call.name].append(call)
    
    print(f"Found {sum(len(funcs) for funcs in all_functions.values())} function definitions")
    print(f"Found {sum(len(calls) for calls in all_calls.values())} function calls")
    
    # Find mismatches
    mismatches = find_mismatches(all_functions, all_calls)
    
    if not mismatches:
        print("\nNo parameter mismatches found!")
        return
    
    print(f"\nFound {len(mismatches)} parameter mismatches:")
    for func, issues in mismatches.items():
        print(f"\n{func}:")
        for issue in issues:
            print(f"  - {issue}")
    
    if args.fix:
        print("\nGenerating suggested fixes...")
        # This would require more complex AST manipulation to generate fixes
        print("Fix generation not yet implemented")


if __name__ == "__main__":
    main()