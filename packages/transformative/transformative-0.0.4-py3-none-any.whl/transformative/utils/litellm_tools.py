import hashlib
import json
from pathlib import Path

import diskcache
import litellm

# Initialize cache in user's cache directory
cache_dir = Path.home() / ".cache" / "autoconvert" / "litellm"
cache = diskcache.Cache(str(cache_dir))


def load_prompt(prompt_path: Path) -> str:
    """Load a prompt template from a file"""
    with open(prompt_path) as f:
        return f.read()


def _make_cache_key(prompt: str, model: str) -> str:
    """Create a unique cache key from the prompt and model"""
    key_dict = {
        "prompt": prompt,
        "model": model
    }
    key_str = json.dumps(key_dict, sort_keys=True)
    return hashlib.sha256(key_str.encode()).hexdigest()


def get_completion(prompt: str, model: str = "gpt-4") -> str:
    """Get a completion from LiteLLM with caching"""
    # Check cache first
    cache_key = _make_cache_key(prompt, model)
    cached_result = cache.get(cache_key)
    short_prompt = prompt.replace("\n", " ")[:50]
    if cached_result is not None:
        # print(Panel.fit(f"Cache hit - returning cached result for {model}: {short_prompt}", style="green"))
        return cached_result

    # print(Panel.fit(f"Cache miss - sending prompt to {model}: {short_prompt}", style="yellow"))
    response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    result = response.choices[0].message.content

    # Cache the result before returning
    cache.set(cache_key, result)
    return result
