"""
twat-mp - Parallel processing utilities for twat using pathos and aiomultiprocess.
"""

from twat_mp.mp import (
    MultiPool,
    ProcessPool,
    ThreadPool,
    amap,
    imap,
    mmap,
    pmap,
    set_debug_mode,
)
from twat_mp.async_mp import AsyncMultiPool, apmap

try:
    from twat_mp.__version__ import __version__
except ImportError:
    __version__ = "0.0.0"


__all__ = [
    "AsyncMultiPool",
    "MultiPool",
    "ProcessPool",
    "ThreadPool",
    "__version__",
    "amap",
    "apmap",
    "imap",
    "mmap",
    "pmap",
    "set_debug_mode",
]
