import importlib
from pathlib import Path
from typing import Tuple, Type, Optional


def get_module_path(path: Path) -> str:
    """Convert a directory path to its Python module import path
    
    Attempts to find project root (containing pyproject.toml) and returns
    the proper Python module path relative to it.
    
    Args:
        path: Path to convert to module path
        
    Returns:
        String representing the Python module import path
    """
    try:
        # Try to get path relative to project root (where pyproject.toml is)
        project_root = path
        while not (project_root / "pyproject.toml").exists():
            project_root = project_root.parent
            if project_root == project_root.parent:  # Reached root directory
                raise FileNotFoundError("Could not find project root (pyproject.toml)")
                
        rel_path = path.relative_to(project_root)
        return str(rel_path).replace('/', '.').replace('\\', '.')
    except (ValueError, FileNotFoundError):
        # Fallback: just use the directory name
        return path.name


def _get_actual_module_file(type_obj: Type) -> Tuple[Optional[Path], str]:
    """Get the actual file and module name where a type is defined"""
    if type_obj.__module__ == '__main__':
        # Get the file that's actually running
        import __main__
        file_path = Path(__main__.__file__).resolve()
        # Convert file path to module path
        relative_path = file_path.relative_to(Path(__file__).parent.parent.parent)
        module_name = str(relative_path.with_suffix('')).replace('/', '.')
        return file_path, module_name
    else:
        # For non-main modules, try to find the actual file
        try:
            module = importlib.import_module(type_obj.__module__)
            if hasattr(module, '__file__'):
                return Path(module.__file__).resolve(), type_obj.__module__
        except ImportError:
            pass
    return None, type_obj.__module__
