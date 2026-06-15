# utils/cache.py
import json
import os
import hashlib

CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)
    )),
    "cache"
)

os.makedirs(CACHE_DIR, exist_ok=True)


def make_key(prompt: str) -> str:
    """
    Create unique cache key from prompt.
    MD5 hash of prompt text.
    Same prompt = same key = same cached result.
    """
    return hashlib.md5(
        prompt.encode()
    ).hexdigest()


def get_cached(prompt: str) -> str:
    """
    Check if result exists in cache.
    Returns cached result or None.
    """
    key = make_key(prompt)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")

    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            data = json.load(f)
        print("[Cache] HIT ✅ — using cached response")
        return data.get("result")

    return None


def save_cache(prompt: str, result: str):
    """
    Save LLM result to cache file.
    Only cache non-empty results.
    """
    if not result:
        return

    key = make_key(prompt)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")

    with open(cache_file, "w") as f:
        json.dump({
            "key": key,
            "prompt_preview": prompt[:100],
            "result": result
        }, f, indent=2)

    print("[Cache] SAVED")


def clear_cache():
    """Clear all cached results."""
    import shutil
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
        os.makedirs(CACHE_DIR)
    print("[Cache] Cleared all cached results")