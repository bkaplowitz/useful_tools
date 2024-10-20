import gzip
import inspect
import os
import pickle
import time
from functools import wraps
from pathlib import Path
import shutil


def _diskcache(path, f, *args, **kwargs):
    path.parent.mkdir(exist_ok=True, parents=True)
    if not path.exists():
        path.write_bytes(
            gzip.compress(pickle.dumps(f(*args, **kwargs), protocol=4))
        )
    return pickle.loads(gzip.decompress(path.read_bytes()))


def _diskclear(path):
    if path.exists():
        path.unlink()


def _memcache(cache, path, f, *args, **kwargs):
    if path not in cache:
        cache[path] = f(*args, **kwargs)
    return cache[path]


def _memclear(cache, path):
    if path in cache:
        del cache[path]


def _timecache(duration, cache, path, f, *args, **kwargs):
    if path in cache:
        calltime, val = cache[path]
        if (time.time() - calltime) < duration:
            return val
    calltime, val = time.time(), f(*args, **kwargs)
    cache[path] = (calltime, val)
    return val


def autocache(
    filepattern=None, disk=True, memory=False, duration=None, root=".cache"
):
    """Uses the modulename, function name and arguments to cache the results of a
    function in a sensible location. For example, suppose you have a function called
    `transactions` in a module called `banks.starling`. It takes one argument, a date.
    Then by decorating it as
    ```
    @autocache('{date:%Y-%m-%d}')
    def transactions(date):
        ...
    ```
    when you call `transactions(pd.Timestamp('2018-11-22'))`, the result will be stored
    to `.cache/banks/starling/transactions/2018-11-22`. Next time you call it with the
    same argument, the result will be loaded from that cache file.
    If you leave the pattern empty, it'll default to a concatenation of the params. So
    you could have easily written
    ```
    @autocache()
    def transactions(date):
        ...
    ```
    What's more, you can also set `memory=True` and get an additional in-memory cache
    that wraps the disk cache. If a result is in memory, that'll be returned, else
    it'll go to the disk, and only if the result is missing there too will the
    function be called.
    """

    def decorator(f):
        # Default to `.cache/slashed/module/path`
        module = f.__module__

        cache = {}

        nonlocal filepattern
        if filepattern is None:
            params = inspect.signature(f).parameters
            filepattern = "-".join(f"{{{p}}}" for p in params)

        # If the function is parameterless, fall back to the base path
        root_parts = [root, *module.split("."), f.__name__]
        parts = [*root_parts, filepattern] if filepattern else root_parts
        pattern = os.path.join(*parts)

        def cachepath(*args, **kwargs):
            bind = inspect.signature(f).bind(*args, **kwargs)
            bind.apply_defaults()
            return Path(pattern.format(**bind.arguments))

        @wraps(f)
        def wrapped(*args, **kwargs):
            path = cachepath(*args, **kwargs)
            if duration:
                # TODO: Implement disk duration caching.
                assert not disk, "Can't specify a duration and use disk caching"
                return _timecache(duration, cache, path, f, *args, **kwargs)
            if memory and disk:
                return _memcache(
                    cache, path, _diskcache, path, f, *args, **kwargs
                )
            if disk:
                return _diskcache(path, f, *args, **kwargs)
            if memory:
                return _memcache(cache, path, f, *args, **kwargs)
            return f

        def clear(*args, **kwargs):
            path = cachepath(*args, **kwargs)
            if memory:
                _memclear(cache, path)
            if disk:
                _diskclear(path)

        def clear_all():
            global cache
            if disk:
                shutil.rmtree(os.path.join(*root_parts))
            if memory:
                cache = {}

        wrapped.clear = clear
        wrapped.clear_all = clear_all

        return wrapped

    return decorator


def memcache(*args, **kwargs):
    return autocache(*args, **kwargs, memory=True, disk=False)


def timecache(duration, *args, **kwargs):
    return autocache(*args, **kwargs, duration=duration, disk=False)
