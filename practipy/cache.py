import sys
from pathlib import Path

from diskcache import Cache

if sys.platform in ["win32", "cygwin"]:
    _cache = Cache(Path.home() / "AppData" / "Local" / "Temp" / "practipy_cache")
else:
    _cache = Cache("/tmp/practipy_cache")


def cache_disk(*args, **kwargs):
    """Like functools.cache, but caches the results to disk instead of RAM.

    Useful for debugging and development of code containing a few very lenghty function
    calls.
    """
    if len(args) == 1 and callable(args[0]):
        return _cache.memoize()(args[0])

    def wrapped(func):
        return _cache.memoize(*args, **kwargs)(func)

    return wrapped
