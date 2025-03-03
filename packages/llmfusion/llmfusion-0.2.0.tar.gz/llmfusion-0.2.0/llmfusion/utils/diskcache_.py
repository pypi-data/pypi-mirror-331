import datetime
import hashlib
import inspect
from functools import wraps
from pathlib import Path
import diskcache

CACHE_SIZES_GiB = {"small": 1, "medium": 5, "large": 10}
PACKAGE_PATH = Path(__file__).parent.parent.parent
GiB = 1024 ** 3

_SHARDS = 16
DISKCACHE_ROOT_PATH = PACKAGE_PATH / ".diskcache"
MAX_DISKCACHE_WORKERS = 12

CACHE_EXPIRATION_BY_TAG = {
    "get_completion": datetime.timedelta(weeks=52).total_seconds(),
    "get_embedding": datetime.timedelta(weeks=52).total_seconds()
}



class CacheManager:
    def __init__(self):
        self.caches = {}

    def get_cache(self, file_path: str, size_gib: int) -> diskcache.FanoutCache:
        """Get or create cache for a source file path"""
        key = (file_path, size_gib)

        if key not in self.caches:
            try:
                rel_path = Path(file_path).relative_to(PACKAGE_PATH)
            except ValueError:
                rel_path = Path(file_path)

            cache_path = DISKCACHE_ROOT_PATH / rel_path.with_suffix('')
            cache_path.mkdir(parents=True, exist_ok=True)

            self.caches[key] = diskcache.FanoutCache(
                directory=str(cache_path),
                shards=_SHARDS,
                timeout=10,
                size_limit=size_gib * GiB,
                eviction_policy='least-recently-used'
            )
        return self.caches[key]


cache_manager = CacheManager()

import inspect
from pathlib import Path


def diskcache_memoize(expire_tag: str, size_gib: str = "medium"):
    def decorator(func):
        # Get function's defining file path during decoration
        func_path = Path(inspect.getfile(func)).resolve()
        cache_size = CACHE_SIZES_GiB[size_gib]
        cache = cache_manager.get_cache(str(func_path), cache_size)

        @wraps(func)
        def wrapper(*args, **kwargs):
            use_cache = kwargs.pop('use_cache', True)
            if not use_cache:
                return func(*args, **kwargs)

            # Extract instance and config
            instance = args[0] if args and hasattr(args[0], 'config') else None
            expire = CACHE_EXPIRATION_BY_TAG.get(expire_tag, 0)

            if instance and hasattr(instance.config, 'cache_ttl'):
                expire = instance.config.cache_ttl

            # Create safe arguments for caching (skip instance)
            cache_args = args[1:] if instance else args
            cache_key = _create_cache_key(cache_args, kwargs)

            if use_cache and (cached := cache.get(cache_key)):
                return cached

            result = func(*args, **kwargs)
            cache.set(cache_key, result, expire)
            return result

        return wrapper

    return decorator


def _create_cache_key( args, kwargs) -> str:
    """Create stable hash key from arguments"""
    key_parts = [
        str(arg if isinstance(arg, (str, int, float, bool)) else repr(arg))
        for arg in args
    ]
    key_parts.extend([
        f"{k}={v}" if isinstance(v, (str, int, float, bool)) else f"{k}={repr(v)}"
        for k, v in kwargs.items()
    ])
    return hashlib.sha256("|".join(key_parts).encode()).hexdigest()