"""Functions for generating and confirming conversion function names"""

from typing import Optional, Tuple

from src.utils.litellm_tools import get_completion
from src.utils.print_utils import print_status, print_warning
from .types import ConversionSignature


def suggest_names(signature: ConversionSignature) -> Tuple[str, str]:
    """Get LLM suggestions for file and function names
    
    Args:
        signature: The conversion signature
        
    Returns:
        Tuple of (file_name, function_name)
    """
    prompt = f"""Given a function that converts from {signature.from_type.__name__} to {signature.to_type.__name__},
with this description: {signature.description or 'No additional description provided'}

Suggest a good file name (without .py) and function name that follows these rules:
1. File name should be snake_case and descriptive
2. Function name should be snake_case. It might start with 'convert_'
3. Names should be concise but clear
4. If the description suggests a specific type of conversion, incorporate that
5. Don't include type names if they're very long

Return exactly two lines:
file_name
function_name"""

    try:
        response = get_completion(prompt)
        file_name, func_name = response.strip().split('\n')
        return file_name, func_name
    except Exception as e:
        print_warning(f"Error getting name suggestions: {e}")
        # Fall back to basic names
        return signature.file_name(), signature.function_name()


def confirm_names(
        signature: ConversionSignature,
        suggested_file: Optional[str] = None,
        suggested_func: Optional[str] = None
) -> Tuple[str, str]:
    """Ask user to confirm or modify suggested names
    
    Args:
        signature: The conversion signature
        suggested_file: Optional suggested file name
        suggested_func: Optional suggested function name
        
    Returns:
        Tuple of (confirmed_file_name, confirmed_function_name)
    """
    if suggested_file is None or suggested_func is None:
        suggested_file, suggested_func = suggest_names(signature)

    print_status("\nSuggested names:")
    print_status(f"  File name: {suggested_file}.py")
    print_status(f"  Function name: {suggested_func}")

    while True:
        response = input("\nAccept these names? [Y/n]: ").lower()
        if response in ('', 'y', 'yes'):
            return suggested_file, suggested_func
        elif response in ('n', 'no'):
            file_name = input("Enter new file name (without .py): ").strip()
            func_name = input("Enter new function name: ").strip()
            if file_name and func_name:
                return file_name, func_name
            print_warning("Names cannot be empty, using suggestions")
            return suggested_file, suggested_func
