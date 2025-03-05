import re

def extract_code_blocks(text: str) -> str:
    """Extract and combine code from markdown code blocks.
    
    Strips ```python or ``` fence markers and any text outside code blocks.
    Returns the combined code content from all code blocks.
    
    Args:
        text: String containing markdown code blocks
        
    Returns:
        String containing just the code content
    """
    # Match content between code fences, handling optional language identifier
    pattern = r"```(?:python)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    
    if not matches:
        # If no code blocks found, return original text
        return text.strip()
        
    # Combine all code blocks with newlines between them
    return "\n\n".join(block.strip() for block in matches) + "\n"


def commentize_description(description: str) -> str:
    description = description.strip()

    # Add comment markers to each line
    return "\n".join(f"# {line}" for line in description.splitlines())
