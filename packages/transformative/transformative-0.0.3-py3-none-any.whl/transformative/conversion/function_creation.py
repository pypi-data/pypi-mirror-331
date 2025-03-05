"""Functions for generating conversion code using aider"""
import subprocess
from datetime import datetime
from pathlib import Path

from .types import ConversionSignature
from ..utils.code_wrangling import _get_actual_module_file, get_module_path
from ..utils.print_utils import print_status, print_error

TEST_INSTRUCTIONS = f"""
# Test Requirements:
# 1. Test basic conversion functionality
# 2. Include edge cases and error handling
# 3. Use pytest.mark.parametrize where appropriate
# 4. Include docstrings explaining each test
# 5. Follow pytest best practices
# 6. Illustrate the expected behavior
# 7. Improve the readability of the codebase through explanatory testing
# 8. All imports should be at the top of the file
# 9. Do NOT expect that the function checks the type of the input data
    """.strip()

TODO_BLOCK = f"""
# TODO: Write test cases that verify:
# 1. Basic conversion functionality
# 2. Edge cases and error handling
# 3. The conversion requirements described above
#
# Note: The function currently raises NotImplementedError.
# Write tests that describe the expected behavior, they will fail initially.
# Do not write the actual conversion function yet.
# Once you write the tests, stop and I will review them.
""".strip()

CONVERSION_INSTRUCTIONS = f"""
# TODO Your own imports go here. Do not use local imports.

# TODO: Fill out this function, follow this advice
# 1. All imports should be at the top of the file
# 2. Add type hints to the function signature, and in general use type annotations to make the code readable
# 3. Do NOT check the type of the input data, as this can cause problems
""".strip()


def get_conversion_path(signature: ConversionSignature, generated_dir: Path) -> Path:
    """Get the path where the conversion function should be stored"""
    # Create a file name based on the signature

    # Add a short hash to avoid collisions
    # base_name = f"{signature.from_type.__name__.lower()}_to_{signature.to_type.__name__.lower()}"
    # file_name = f"{base_name}_{hash(signature) & 0xFFFF:04x}.py"
    file_name = f"{signature.file_name()}.py"

    return generated_dir / file_name


def get_test_path(signature: ConversionSignature, generated_dir: Path) -> Path:
    """Get the path where the test file should be stored"""
    # Create a test file name based on the signature

    # Add a short hash to avoid collisions
    # base_name = f"test_{signature.from_type.__name__.lower()}_to_{signature.to_type.__name__.lower()}"
    # file_name = f"{base_name}_{hash(signature) & 0xFFFF:04x}.py"
    file_name = f"test_{signature.file_name()}.py"

    return generated_dir / file_name


def write_test_todo(test_path: Path, generated_dir: Path, signature: ConversionSignature) -> None:
    """Write initial TODO comments to the test file"""
    test_path.parent.mkdir(parents=True, exist_ok=True)

    # Get actual module files
    from_file, from_module = _get_actual_module_file(signature.from_type)
    to_file, to_module = _get_actual_module_file(signature.to_type)

    # Get the conversion file name (without .py)
    conv_base = get_conversion_path(signature, test_path.parent).stem

    # Get proper module path for the generated code directory
    module_path = get_module_path(generated_dir)

    todo_content = f"""\"\"\"
Tests for converting {signature.from_type.__name__} to {signature.to_type.__name__}

This test file is designed to test the stub function in {conv_base}.py.
The stub currently raises NotImplementedError - your task is to write tests
that describe how the function should behave once implemented.

The conversion should: {signature.description if signature.description else f'Convert {signature.from_type.__name__} to {signature.to_type.__name__}'}
\"\"\"

from {from_module} import {signature.from_type.__name__}
from {to_module} import {signature.to_type.__name__}
from {module_path}.{conv_base} import {signature.function_name()}

# TODO Your own imports go here. Do not use local imports.

{TODO_BLOCK}

{TEST_INSTRUCTIONS}

def test_basic_conversion():
    \"\"\"Test basic conversion functionality\"\"\"
    pass

def test_edge_cases():
    \"\"\"Test edge cases and error handling\"\"\"
    pass
"""
    test_path.write_text(todo_content)


def create_aider_test_message(signature: ConversionSignature) -> str:
    """Create the message to send to aider for generating tests"""
    return "Implement the tests following the requirements in the TODO and comments"


def generate_empty_conversion_file(
        signature: ConversionSignature,
        conv_path: Path,
        test_path: Path,
        debug_level: int = 0
) -> None:
    """Create an empty conversion file with a stub function
    
    Returns:
        Tuple of (success, error_message)
    """
    # Get actual module files for imports
    from_file, from_module = _get_actual_module_file(signature.from_type)
    to_file, to_module = _get_actual_module_file(signature.to_type)

    # Create stub content
    stub_content = f"""\"\"\"
Module for converting {signature.from_type.__name__} to {signature.to_type.__name__}
\"\"\"

from {from_module} import {signature.from_type.__name__}
from {to_module} import {signature.to_type.__name__}

def {signature.function_name()}(
    data: {signature.from_type.__name__}
) -> {signature.to_type.__name__}:
    \"\"\"Convert {signature.from_type.__name__} to {signature.to_type.__name__}
    
    Args:
        data: The input {signature.from_type.__name__}
        
    Returns:
        The converted {signature.to_type.__name__}
    \"\"\"
    raise NotImplementedError("Conversion not yet implemented")
"""
    # Create the directory if needed
    conv_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the file
    conv_path.write_text(stub_content)

    if debug_level >= 2:
        print_status(f"Created conversion stub at: {conv_path}")


def generate_tests(
        signature: ConversionSignature,
        generated_dir: Path,
        debug_level: int = 0,
        capture_output: bool = False
) -> None:
    """Generate tests for a conversion function using aider"""
    if debug_level >= 1:
        print_status(f"Generating tests for {signature}")

    # Get the test file path
    test_path = get_test_path(signature, generated_dir)
    conv_path = get_conversion_path(signature, generated_dir)

    # Create the empty conversion file first
    generate_empty_conversion_file(signature, conv_path, test_path, debug_level)

    # Write initial to-do content
    write_test_todo(test_path, generated_dir, signature)

    if debug_level >= 2:
        print_status(f"Created test file with TODOs at: {test_path}")

    # Create the simple aider message
    message = create_aider_test_message(signature)

    if debug_level >= 2:
        print_status(f"Using aider message: {message}")

    # Run aider with simple message
    # Add --read flags for the input/output type files
    read_flags = []
    file_deduper = set()
    for type_obj in [signature.from_type, signature.to_type]:
        file_path, _ = _get_actual_module_file(type_obj)
        if file_path and file_path not in file_deduper:
            read_flags.extend(['--read', str(file_path)])
            file_deduper.add(file_path)
        else:
            print_error(f"Could not find module file for {type_obj}")
    read_flags.extend(['--read', str(conv_path)])

    cmd = ["aider", "--yes", "--no-auto-commits", "--message", f'"{message}"', str(test_path)] + read_flags

    print_status(f"Running command: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=capture_output,
        text=True,
        check=True
    )

    # Check if INSTRUCTIONS are in the test_path file, and delete them if so
    with open(test_path, 'r') as f:
        content = f.read()
        if TEST_INSTRUCTIONS.strip() in content:
            content = content.replace(TEST_INSTRUCTIONS.strip(), "")
        if TODO_BLOCK.strip() in content:
            content = content.replace(TODO_BLOCK.strip(), "")
        with open(test_path, 'w') as f:
            f.write(content.strip() + "\n")

    return None


def generate_conversion_file(
        signature: ConversionSignature,
        generated_dir: Path,
        debug_level: int = 0,
        capture_output: bool = False
) -> None:
    """Generate the conversion function implementation using aider
    
    Args:
        signature: The conversion signature
        generated_dir: Directory where generated code is stored
        debug_level: Level of debug output (0-4)
        capture_output: Whether to capture aider output
        
    Returns:
        Tuple of (success, error_message)
    """
    if debug_level >= 1:
        print_status(f"Generating conversion implementation for {signature}")

    # Get the file paths
    conv_path = get_conversion_path(signature, generated_dir)
    test_path = get_test_path(signature, generated_dir)

    # First, add the @autoconvert decorator and CONVERSION_INSTRUCTIONS to the file
    with open(conv_path, 'r') as f:
        content = f.read()

    # Add imports for decorator and datetime if they don't exist
    imports_to_add = []
    if "from src.conversion.decorator import autoconvert" not in content:
        imports_to_add.append("from src.conversion.decorator import autoconvert")
    if "from datetime import datetime" not in content:
        imports_to_add.append("from datetime import datetime")

    if imports_to_add:
        # Find the last import line
        import_lines = [i for i, line in enumerate(content.split('\n')) if line.startswith('from ') or line.startswith('import ')]
        if import_lines:
            last_import_line = import_lines[-1]
            content_lines = content.split('\n')
            for imp in imports_to_add:
                content_lines.insert(last_import_line + 1, imp)
            content = '\n'.join(content_lines)

    # Add the CONVERSION_INSTRUCTIONS
    if CONVERSION_INSTRUCTIONS.strip() not in content:
        # Add after the imports but before the function
        func_def_line = f"def {signature.function_name()}("
        if func_def_line in content:
            content = content.replace(func_def_line, f"\n{CONVERSION_INSTRUCTIONS}\n\n@autoconvert(\n    description=\"{signature.get_description()}\",\n    generated_date=\"{datetime.now().strftime('%Y-%m-%d')}\",\n    test_file=\"{test_path.name}\",\n    test_hash=None,\n)\n{func_def_line}")

    # Write the updated content back to the file
    with open(conv_path, 'w') as f:
        f.write(content)

    # Create the aider message
    message = f"Implement the conversion function that converts {signature.from_type.__name__} to {signature.to_type.__name__}. "
    if signature.description:
        message += f"The conversion should: {signature.description}"
    message += " Take a look at the tests to see more about the desired behavior."

    if debug_level >= 2:
        print_status(f"Using aider message: {message}")

    # Run aider with the message
    # Add --read flags for the input/output type files and test file
    read_flags = []
    file_deduper = set()
    for type_obj in [signature.from_type, signature.to_type]:
        file_path, _ = _get_actual_module_file(type_obj)
        if file_path and file_path not in file_deduper:
            read_flags.extend(['--read', str(file_path)])
            file_deduper.add(file_path)
        else:
            print_error(f"Could not find module file for {type_obj}")

    # Add test file to read flags
    read_flags.extend(['--read', str(test_path)])

    cmd = ["aider", "--yes", "--no-auto-commits", "--message", f'"{message}"', str(conv_path)] + read_flags

    if debug_level >= 2:
        print_status(f"Running command: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=capture_output,
        text=True,
        check=True
    )

    # Remove the INSTRUCTIONS from the conversion file
    with open(conv_path, 'r') as f:
        content = f.read()
        if CONVERSION_INSTRUCTIONS.strip() in content:
            content = content.replace(CONVERSION_INSTRUCTIONS.strip(), "")
        with open(conv_path, 'w') as f:
            f.write(content.strip() + "\n")
