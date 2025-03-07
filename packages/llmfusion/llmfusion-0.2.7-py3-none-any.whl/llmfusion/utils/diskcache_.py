import datetime
import hashlib
import inspect
from functools import wraps
from pathlib import Path
import diskcache

CACHE_SIZES_GiB = {"small": 1, "medium": 5, "large": 10}

CACHE_EXPIRATION_BY_TAG = {
    "get_completion": datetime.timedelta(weeks=52).total_seconds(),
    "get_embedding": datetime.timedelta(weeks=52).total_seconds()
}

class CacheManager:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or Path.home() / ".cache" / "llmfusion"
        self.caches = {}

    def get_cache(self, cache_name: str, size_gib: int) -> diskcache.FanoutCache:
        key = (cache_name, size_gib)
        if key not in self.caches:
            cache_path = self.base_dir / cache_name
            cache_path.mkdir(parents=True, exist_ok=True)
            self.caches[key] = diskcache.FanoutCache(
                directory=str(cache_path),
                shards=8,
                timeout=10,
                size_limit=size_gib * (1024 ** 3),
            )
        return self.caches[key]

cache_manager = CacheManager()

def _make_cache_key(args, kwargs):
    key_parts = [str(arg if isinstance(arg, (str, int, float, bool)) else repr(arg)) for arg in args]
    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
    key_str = "|".join(key_parts)
    return hashlib.sha256(key_str.encode()).hexdigest()

CACHE_EXPIRATION_BY_TAG = {
    "get_completion": datetime.timedelta(weeks=52).total_seconds(),
    "get_embedding": datetime.timedelta(weeks=52).total_seconds(),
}

def diskcache_memoize(expire_tag="get_completion", size_gib="large"):
    def decorator(func):
        func_path = Path(inspect.getfile(func)).resolve()
        cache_size = CACHE_SIZES_GiB[size_gib]

        @wraps(func)
        def wrapper(*args, **kwargs):
            instance = args[0] if args else None

            cache_dir = (
                Path(instance.config.resolved_cache_dir())
                if instance and hasattr(instance, "config")
                else Path.home() / ".cache" / "llmfusion"
            )

            expire = CACHE_EXPIRATION_BY_TAG.get(expire_tag, 0)
            if instance and hasattr(instance.config, "cache_ttl"):
                expire = instance.config.cache_ttl

            cache = cache_manager.get_cache(str(cache_dir / func_path.name), cache_size)

            cache_args = args[1:] if instance else args
            cache_key = _make_cache_key(cache_args, kwargs)

            if (cached := cache.get(cache_key)) is not None:
                return cached

            result = func(*args, **kwargs)
            cache.set(cache_key, result, expire=expire)
            return result

        return wrapper

    return decorator
