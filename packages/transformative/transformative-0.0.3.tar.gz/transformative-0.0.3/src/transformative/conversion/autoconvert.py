import importlib
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union, TypeVar, Dict, Callable, Type

from . import searcher, function_creation, test_runner
from .function_creation import generate_conversion_file
from .namer import confirm_names
from .types import ConversionSignature
from ..utils.code_wrangling import get_module_path, _get_actual_module_file
from ..utils.print_utils import pause_for_user_review, get_user_confirmation
from ..utils.print_utils import print_status, print_warning, print_error, print_generation_header, print_results, print_panel

# Type variables for generic type hints
X = TypeVar("X")
Y = TypeVar("Y")
T = TypeVar("T")
R = TypeVar("R")


# Global state container
@dataclass
class AutoConvertState:
    initialized: bool = False
    generated_code_dir: Optional[Path] = None
    # Maps ConversionSignature to the actual conversion function
    known_functions: Dict[ConversionSignature, Callable] = field(default_factory=dict)

    def add_function(self, signature: ConversionSignature, func: Callable) -> None:
        """Add a conversion function to the known functions catalog"""
        self.known_functions[signature] = func

    def get_function(self, signature: ConversionSignature) -> Optional[Callable]:
        """Get a conversion function by signature if it exists"""
        return self.known_functions.get(signature)

    def has_function(self, signature: ConversionSignature) -> bool:
        """Check if a conversion function exists for the given signature"""
        return signature in self.known_functions

    def remove_function(self, signature: ConversionSignature) -> None:
        """Remove a conversion function from the catalog if it exists"""
        if signature in self.known_functions:
            del self.known_functions[signature]


# Single global state instance
_state = AutoConvertState()


def convert(
        data: X,
        to_type: Type[Y],
        description: Optional[str] = None,
        debug_level: int = 0,
        clobber_existing_files: bool = False,
) -> Y:
    """Execute a conversion from one type to another
    
    Args:
        data: The data to convert
        to_type: The type to convert to
        description: Optional description of the conversion
        debug_level: Level of debug output (0-4)
        
    Returns:
        The converted data
    """
    if not _state.initialized:
        raise RuntimeError("autoconvert must be initialized first")

    # Get the actual types, handling __main__ module case
    from_type = type(data)

    # Get existing function or create new one
    func = create(from_type=from_type, to_type=to_type, description=description, debug_level=debug_level, clobber_existing_files=clobber_existing_files)

    # Execute the conversion
    try:
        result = func(data)
        # if not isinstance(result, to_type):  # Not checking this because of issues with the module sometimes being __main__
        #     raise TypeError(f"Conversion returned {type(result)}, expected {to_type}")
        return result
    except Exception as e:
        print_error(f"Error during conversion: {str(e)}")
        raise


def create(
        from_type: Type[T],
        to_type: Type[R],
        description: Optional[str] = None,
        debug_level: int = 0,
        clobber_existing_files: bool = False,
) -> Callable[[T], R]:
    """Create or retrieve a conversion function
    
    Args:
        from_type: Type to convert from
        to_type: Type to convert to
        description: Optional description of the conversion
        debug_level: Level of debug output (0-4)
        clobber_existing_files: Overwrite existing files if True
        
    Returns:
        A function that converts from from_type to to_type
    """
    if not _state.initialized:
        raise RuntimeError("autoconvert must be initialized first")

    # Fix types
    if from_type.__module__ == '__main__':
        _, module_name = _get_actual_module_file(from_type)
        from_type = getattr(importlib.import_module(module_name), from_type.__name__)

    if to_type.__module__ == '__main__':
        _, module_name = _get_actual_module_file(to_type)
        to_type = getattr(importlib.import_module(module_name), to_type.__name__)

    # Create signature for this conversion
    signature = ConversionSignature(
        from_type=from_type,
        to_type=to_type,
        description=description
    )

    # Check if we already have this conversion
    if _state.has_function(signature):
        if debug_level >= 2:
            print_status(f"Found existing conversion function: {signature}")
        if clobber_existing_files:
            print_warning(f"WARNING! OVERWRITING FILE FOR: {signature}")
        else:
            return _state.get_function(signature)

    if debug_level >= 1:
        print_generation_header(f"{signature.file_name()} :: hash={signature.__hash__()} :: {signature}")

    # Get and confirm function/file names
    if debug_level >= 1:
        print_status("\nGetting name suggestions...")
    file_name, func_name = confirm_names(signature)

    # Create new signature with confirmed names
    signature = ConversionSignature(
        from_type=signature.from_type,
        to_type=signature.to_type,
        description=signature.description,
        file_name=file_name,
        function_name=func_name
    )

    # Generate tests first
    test_path = function_creation.get_test_path(signature, _state.generated_code_dir)
    function_creation.generate_tests(
        signature=signature,
        generated_dir=_state.generated_code_dir,
        debug_level=debug_level
    )

    # Ask the user to sign off on the tests
    print_panel(f"Test file generated at: {test_path}", title="Test Review Required")
    print_status("Please review the test file to ensure it correctly tests the conversion.")
    print_status("The conversion function will be generated based on these tests.")
    print_status("If the tests are incorrect, you can edit them manually before continuing.")

    # Pause for user review
    pause_for_user_review()

    generate_conversion_file(
        signature=signature,
        generated_dir=_state.generated_code_dir,
        debug_level=debug_level
    )

    # Run the tests and check if they pass
    tests_passed, error_message = test_runner.run_tests(test_path, debug_level)

    if not tests_passed:
        print_panel(f"Tests failed! Please fix the tests or the implementation.", title="Test Failure")
        if error_message:
            print_error(error_message)

        # Ask if the user wants to continue anyway
        if get_user_confirmation("Continue anyway?", default=False):
            print_warning("Continuing with failed tests!")
        else:
            raise RuntimeError("Tests failed and user chose not to continue")
    else:
        print_panel("Tests passed successfully!", title="Test Success")

        # Calculate the test hash and update it in the file
        test_hash = test_runner.calculate_test_hash(test_path)
        conv_path = function_creation.get_conversion_path(signature, _state.generated_code_dir)
        test_runner.update_test_hash_in_file(conv_path, test_hash, debug_level)

        if debug_level >= 2:
            print_status(f"Updated test hash to: {test_hash}")

    # Get the function out of the file
    conv_path = function_creation.get_conversion_path(signature, _state.generated_code_dir)
    module_path = f"{get_module_path(conv_path.parent)}.{conv_path.stem}"

    # Import and reload to ensure we get the new implementation
    module = importlib.import_module(module_path)
    module = importlib.reload(module)
    func = getattr(module, signature.function_name())

    # Add to known functions
    _state.add_function(signature, func)

    return func


def check_dependencies():
    """
    Check if required external dependencies are installed.
    Raises RuntimeError if dependencies are missing.
    """
    try:
        subprocess.run(["aider", "--version"], capture_output=True, check=False)
    except FileNotFoundError:
        raise RuntimeError("aider is required but not installed. Install with: `pip install aider-install`")


def init(
        generated_code_dir: Optional[Union[Path, str]] = None,
        other_code_dirs: Optional[Union[Path, str]] = None,  # TODO, also look for conversions in other directories
        debug_level: int = 0,
) -> None:
    """Initialize the autoconvert system

    Args:
        generated_code_dir: Directory where generated code will be stored
    """
    # Check if required dependencies are installed
    check_dependencies()
    global _state

    # if _state.initialized:
    #     print_warning("autoconvert is already initialized")
    #     return

    # Convert string path to Path object if needed
    if isinstance(generated_code_dir, str):
        generated_code_dir = Path(generated_code_dir)

    # Use default if not specified
    if generated_code_dir is None:
        generated_code_dir = Path.cwd() / "generated_code"

    # Create directory if it doesn't exist
    generated_code_dir.mkdir(parents=True, exist_ok=True)

    # Update state
    _state.generated_code_dir = generated_code_dir
    _state.initialized = True

    if debug_level >= 1:
        print_status(f"Initialized autoconvert with generated code directory: {generated_code_dir}")

    # Scan for existing conversion functions
    conversions = searcher.scan_directory_for_conversions(generated_code_dir, debug=debug_level >= 2)

    # Import and catalog found functions
    for func_name, metadata in conversions.items():
        try:
            # Split into module and function name
            module_name, func_name = func_name.split('.')

            # Import the module from generated_code directory
            module = importlib.import_module(f"generated_code.{module_name}")
            func = getattr(module, func_name)

            # Add to catalog
            _state.add_function(metadata.signature, func)
            if debug_level >= 4:
                print_status(f"Loaded function: {module_name}.{func_name}")
        except Exception as e:
            print_warning(f"Failed to import {func_name}: {str(e)}")

    if debug_level >= 2:
        known_funcs = [f"* {func.__name__} :: hash={sig.__hash__()} :: {sig}"
                       for sig, func in _state.known_functions.items()]
        if known_funcs:
            print_results(known_funcs, title="Known Functions")
        else:
            print_results(["No functions found"], title="Known Functions")
