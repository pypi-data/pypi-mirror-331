"""Functions for running tests and calculating test hashes"""
import hashlib
import subprocess
from pathlib import Path
from typing import Tuple, Optional

from src.utils.print_utils import print_status, print_error, print_warning, print_success


def calculate_test_hash(test_path: Path) -> str:
    """
    Calculate a hash of the test file content.
    
    Args:
        test_path: Path to the test file
        
    Returns:
        Hash of the test file content
    """
    content = test_path.read_text()
    return hashlib.md5(content.encode()).hexdigest()


def run_tests(test_path: Path, debug_level: int = 0) -> Tuple[bool, Optional[str]]:
    """
    Run the tests and check if they pass.
    
    Args:
        test_path: Path to the test file
        debug_level: Level of debug output (0-4)
        
    Returns:
        Tuple of (success, error_message)
    """
    if debug_level >= 1:
        print_status(f"Running tests at: {test_path}")
    
    try:
        # Run pytest on the test file
        result = subprocess.run(
            ["pytest", "-xvs", str(test_path)],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Check if tests passed
        if result.returncode == 0:
            if debug_level >= 1:
                print_success("Tests passed!")
            return True, None
        else:
            if debug_level >= 1:
                print_warning("Tests failed!")
                print_error(result.stdout)
                print_error(result.stderr)
            return False, result.stdout + "\n" + result.stderr
    except Exception as e:
        error_msg = f"Error running tests: {str(e)}"
        print_error(error_msg)
        return False, error_msg


def update_test_hash_in_file(conv_path: Path, test_hash: str, debug_level: int = 0) -> bool:
    """
    Update the test_hash parameter in the @autoconvert decorator.
    
    Args:
        conv_path: Path to the conversion file
        test_hash: Hash to set
        debug_level: Level of debug output (0-4)
        
    Returns:
        True if the hash was updated, False otherwise
    """
    if debug_level >= 2:
        print_status(f"Updating test hash in {conv_path} to {test_hash}")
    
    try:
        content = conv_path.read_text()
        
        # Replace test_hash=None with the actual hash
        if "test_hash=None" in content:
            content = content.replace('test_hash=None', f'test_hash="{test_hash}"')
            conv_path.write_text(content)
            return True
        else:
            # Try to find and replace an existing hash
            import re
            pattern = r'test_hash="[^"]*"'
            if re.search(pattern, content):
                content = re.sub(pattern, f'test_hash="{test_hash}"', content)
                conv_path.write_text(content)
                return True
            else:
                print_warning(f"Could not find test_hash parameter in {conv_path}")
                return False
    except Exception as e:
        print_error(f"Error updating test hash: {str(e)}")
        return False
