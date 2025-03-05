import sys
from typing import Optional, Any

from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

# Configure rich console with unlimited width
console = Console(width=100)


def print_status(text: str) -> None:
    print(text)


def print_panel(text: str, title: Optional[str] = None, style: Optional[str] = None) -> None:
    """Print a message in a panel"""
    if style is None:
        style = "blue"
    console.print(Panel.fit(
        text,
        title=title,
        style=style
    ))


def print_generation_header(text: str) -> None:
    """Print a header for generation steps"""
    print_panel(text, style="blue", title="Creating new function")


def print_success(text: str) -> None:
    """Print a success message in a green panel"""
    print_panel(text, style="green")


def print_error(text: str) -> None:
    """Print an error message in a red panel"""
    print("[red]ERROR: " + text + "[/red]")


def print_warning(text: str) -> None:
    """Print a warning message in yellow text"""
    print("[yellow]WARNING: " + text + "[/yellow]")


def print_code(code: str, language: Optional[str] = "python", title: Optional[str] = None) -> None:
    """Print code with syntax highlighting"""
    print(Panel.fit(
        Syntax(code, language, theme="monokai", line_numbers=True),
        title=title,
        style="blue"
    ))


def print_results(results: list[str], title: str = "Results") -> None:
    """Print a list of results in a panel"""
    console.print(Panel.fit(
        "\n".join(results),
        title=title,
        style="blue"
    ))


def print_timing(elapsed: float, prefix: str = "Operation took") -> None:
    """Print timing information"""
    print_status(f"{prefix} {elapsed:.3f} seconds")


def get_user_input(prompt: str, default: Any = None, options: Optional[list] = None) -> Any:
    """
    Get user input with support for non-interactive mode.
    
    Args:
        prompt: The prompt to show the user
        default: The default value to return in non-interactive mode or when user enters nothing
        options: Optional list of valid options
        
    Returns:
        User input or default value
    """
    # In non-interactive mode, return the default
    if not sys.stdin.isatty():
        print_warning(f"Running in non-interactive mode. Using default: {default}")
        return default

    # Format prompt with options if provided
    if options:
        # Capitalize the default option if it exists
        option_str = "/".join(str(opt).upper() if opt == default else str(opt) for opt in options)
        full_prompt = f"{prompt} [{option_str}]: "
    elif default is not None:
        full_prompt = f"{prompt} (default: {default}): "
    else:
        full_prompt = f"{prompt}: "

    # Get user input
    response = input(full_prompt).strip()

    # Return default if user entered nothing
    if not response and default is not None:
        return default

    # Validate against options if provided
    if options and response not in [str(opt) for opt in options]:
        print_warning(f"Invalid input. Please choose from: {', '.join(str(opt) for opt in options)}")
        return get_user_input(prompt, default, options)

    return response


def is_interactive() -> bool:
    """
    Check if the program is running in an interactive terminal.
    
    Returns:
        True if running in an interactive terminal, False otherwise
    """
    return sys.stdin.isatty()


def pause_for_user_review(message: str = "Press Enter to continue or Ctrl+C to cancel...") -> None:
    """
    Pause execution for user review in interactive mode.
    In non-interactive mode, this function does nothing.
    
    Args:
        message: Message to display to the user
        
    Raises:
        RuntimeError: If the user cancels with Ctrl+C
    """
    if not is_interactive():
        print_warning("Running in non-interactive mode. Proceeding automatically.")
        return
        
    print_status(message)
    try:
        input()
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user.")
        raise RuntimeError("User cancelled operation")


def get_user_confirmation(prompt: str, default: bool = True) -> bool:
    """
    Ask the user for confirmation.

    Args:
        prompt: The prompt to show the user
        default: The default answer if the user just presses Enter

    Returns:
        True if the user confirmed, False otherwise
    """
    options = ['y', 'n']
    default_option = 'y' if default else 'n'

    response = get_user_input(prompt, default=default_option, options=options).lower()
    return response == 'y'
