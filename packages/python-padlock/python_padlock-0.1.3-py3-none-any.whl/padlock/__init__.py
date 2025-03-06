from importlib.metadata import version

from padlock.backends.base import LockBackend
from padlock.backends.memory import MemoryLockBackend
from padlock.errors import (
    LockAcquisitionError,
    LockError,
)
from padlock.manager import LockManager


__version__ = version("python-padlock")
del version


__all__ = (
    "__version__",
    "LockBackend",
    "MemoryLockBackend",
    "LockManager",
    "LockError",
    "LockAcquisitionError",
)
