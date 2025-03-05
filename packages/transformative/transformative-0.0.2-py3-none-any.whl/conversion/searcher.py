"""Functions for finding autoconvert functions in Python files"""

import ast
import importlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

from src.utils.print_utils import print_warning, print_status
from src.utils.code_wrangling import get_module_path
from .types import ConversionSignature


@dataclass
class AutoconvertMetadata:
    """Metadata from an autoconvert-decorated function"""
    signature: ConversionSignature
    generated: datetime
    test_file: str
    test_hash: str
    description: Optional[str] = None


def get_decorator_metadata(node: ast.FunctionDef) -> Optional[dict]:
    """Extract metadata from an autoconvert decorator"""
    for decorator in node.decorator_list:
        # Handle both @autoconvert and @autoconvert()
        if isinstance(decorator, ast.Name) and decorator.id == 'autoconvert':
            return {'description': None}
        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == 'autoconvert':
            metadata = {}
            # Extract keyword arguments
            for kw in decorator.keywords:
                if isinstance(kw.value, ast.Constant):
                    metadata[kw.arg] = kw.value.value
            return metadata
    return None


def scan_file_for_conversions(file_path: Path, debug: bool = False) -> List[Tuple[str, Optional[AutoconvertMetadata]]]:
    """Scan a Python file for decorated conversion functions
    
    Args:
        file_path: Path to the Python file to scan
        debug: If True, print debug information during scanning
    """
    conversions = []

    try:
        with open(file_path, 'r') as f:
            content = f.read()
            tree = ast.parse(content)

        module_name = file_path.stem
        if debug:
            print_status(f"Parsing module: {module_name}")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if debug:
                    print_status(f"\nFound function: {node.name}")
                    print_status(f"Decorators: {[d for d in node.decorator_list]}")

                metadata_dict = get_decorator_metadata(node)
                if metadata_dict is not None:
                    if debug:
                        print_status(f"Found autoconvert decorator with metadata: {metadata_dict}")
                    # Get type hints from function signature
                    args = node.args.args
                    returns = node.returns
                    if debug:
                        print_status(f"Function signature:")
                        print_status(f"  Args: {[a.annotation for a in args]}")
                        print_status(f"  Returns: {returns}")

                    if len(args) != 1 or not args[0].annotation or not returns:
                        if debug:
                            print_status("Skipping function - invalid signature")
                        continue

                    # Get the actual types from the module
                    try:
                        # Import the module to get the actual types
                        module_path = f"{get_module_path(file_path.parent)}.{module_name}"
                        if debug:
                            print_status(f"Importing module: {module_path}")
                        module = importlib.import_module(module_path)
                        if debug:
                            print_status(f"Getting function: {node.name}")
                        func = getattr(module, node.name)

                        # Get types from the function's metadata
                        from_type = func._from_type
                        to_type = func._to_type

                        metadata = AutoconvertMetadata(
                            signature=ConversionSignature(
                                from_type=from_type,
                                to_type=to_type,
                                description=metadata_dict.get('description')
                            ),
                            generated=datetime.strptime(
                                metadata_dict.get('generated_date', datetime.now().strftime('%Y-%m-%d')),
                                '%Y-%m-%d'
                            ),
                            test_file=metadata_dict.get('test_file'),
                            test_hash=metadata_dict.get('test_hash')
                        )

                        full_name = f"{module_name}.{node.name}"
                        conversions.append((full_name, metadata))
                    except Exception as e:
                        # print_warning(f"Error importing types for {node.name}: {str(e)}")
                        raise e

    except Exception as e:
        # print_warning(f"Error scanning {file_path}: {str(e)}")
        raise e

    return conversions


def scan_directory_for_conversions(directory: Path, debug: bool = False) -> Dict[str, AutoconvertMetadata]:
    """Recursively scan a directory for Python files containing conversion functions
    
    Returns a dictionary mapping function names to their metadata
    """
    if debug:
        print_status(f"\nScanning directory: {directory}")
    conversions = {}

    if not directory.exists():
        print_warning(f"Directory does not exist: {directory}")
        return conversions

    for file_path in directory.rglob("*.py"):
        # Skip __init__.py files
        if file_path.name == "__init__.py":
            continue

        if debug:
            print_status(f"\nScanning file: {file_path}")
        for func_name, metadata in scan_file_for_conversions(file_path, debug=debug):
            if metadata:  # Only add functions with valid metadata
                conversions[func_name] = metadata
                if debug:
                    print_status(f"  Found function: {func_name}")

    return conversions
