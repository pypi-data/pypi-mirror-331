from datetime import datetime
from functools import wraps
from typing import Optional, Callable, TypeVar, Any, get_type_hints

T = TypeVar('T')


def autoconvert(
        description: Optional[str] = None,
        generated_date: Optional[str] = None,
        test_file: Optional[str] = None,
        test_hash: Optional[str] = None
) -> Callable[[T], T]:
    """Decorator to mark a function as an autoconvert function
    
    Args:
        description: Optional description of what the conversion does
        generated_date: Generation timestamp (defaults to current date)
        test_file: Name of the test file (auto-generated if None)
        test_hash: Hash of the test file contents (auto-generated if None)
        
    Returns:
        Decorated function
    """

    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        # Store all metadata
        wrapper._autoconvert = True
        wrapper._description = description
        wrapper._generated = generated_date or datetime.now().strftime('%Y-%m-%d')

        # Get the type hints from the function
        type_hints = get_type_hints(func)
        wrapper._from_type = type_hints.get('data')  # Input parameter type
        wrapper._to_type = type_hints.get('return')  # Return type

        # Auto-generate test file name if not provided
        if test_file is None and wrapper._from_type and wrapper._to_type:
            from_name = wrapper._from_type.__name__.lower()
            to_name = wrapper._to_type.__name__.lower()
            wrapper._test_file = f"test_{from_name}_to_{to_name}.py"
        else:
            wrapper._test_file = test_file

        wrapper._test_hash = test_hash

        return wrapper

    # Handle case where decorator is used without parentheses
    if callable(description):
        func, description = description, None
        return decorator(func)

    return decorator
