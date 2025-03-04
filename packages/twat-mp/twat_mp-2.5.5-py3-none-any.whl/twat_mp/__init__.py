"""
twat-mp - Parallel processing utilities for twat using pathos and aiomultiprocess.
"""

from twat_mp.mp import MultiPool, ProcessPool, ThreadPool, amap, imap, mmap, pmap

try:
    from twat_mp.__version__ import __version__
except ImportError:
    __version__ = "0.0.0"


__all__ = [
    "MultiPool",
    "ProcessPool",
    "ThreadPool",
    "__version__",
    "amap",
    "imap",
    "mmap",
    "pmap",
    "__version__",
]

try:
    from twat_mp.async_mp import AsyncMultiPool, apmap

    __all__ += ["AsyncMultiPool", "apmap"]
except ImportError:
    pass  # aiomultiprocess is not installed
