from typing import Set, Type, get_type_hints, Any
import inspect
import ast
from dataclasses import is_dataclass

class TypeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.type_names = set()
        
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.type_names.add(node.id)
        self.generic_visit(node)

def get_type_dependencies(type_obj: Type) -> Set[Type]:
    """Get all type objects that a given type depends on"""
    deps = set()
    
    # Get type hints from annotations
    try:
        hints = get_type_hints(type_obj)
        # Add the types from hints
        for hint_type in hints.values():
            if isinstance(hint_type, type):
                deps.add(hint_type)
    except Exception:
        pass  # Skip if we can't get type hints
        
    # Special handling for dataclasses
    if is_dataclass(type_obj):
        for field in type_obj.__dataclass_fields__.values():
            if isinstance(field.type, type):
                deps.add(field.type)
    
    # Remove self-reference and basic types
    basic_types = {str, int, float, bool, list, dict, set, tuple}
    deps = {d for d in deps if d not in basic_types and d != type_obj}
    
    return deps

def get_type_definition_code(type_obj: Type) -> str:
    """Get the complete source code needed to define a type, including imports"""
    try:
        # Get the basic source code
        source = inspect.getsource(type_obj)
        
        # Get dependencies
        deps = get_type_dependencies(type_obj)
        
        # Add imports for dependencies
        imports = []
        if deps:
            # This is simplified - in reality we'd need to determine the correct import paths
            imports.append("from typing import Optional, List, Dict, Set, Tuple")
            
        # Combine imports and source
        return "\n".join(imports + [""] + [source])
    except Exception as e:
        return f"# Failed to get source: {e}\n"
