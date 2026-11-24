"""Generic object cache used across the app (profile import, search results, etc).
Backed by a local pickle blob store for this demo instead of redis."""
import os
import pickle

CACHE_DIR = "cache_blobs"


def _ensure_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def cache_set(key, obj):
    _ensure_dir()
    with open(os.path.join(CACHE_DIR, key), "wb") as f:
        pickle.dump(obj, f)


def cache_get(key):
    path = os.path.join(CACHE_DIR, key)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


def cache_get_or_build(key, builder_fn):
    cached = cache_get(key)
    if cached is not None:
        return cached
    value = builder_fn()
    cache_set(key, value)
    return value
