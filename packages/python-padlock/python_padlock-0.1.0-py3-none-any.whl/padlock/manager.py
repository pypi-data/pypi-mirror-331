from contextlib import asynccontextmanager
from typing import AsyncIterator, Self

from padlock.backends.base import LockBackend
from padlock.errors import LockAcquisitionError


class LockManager:
    """
    A high-level lock manager that provides a context manager
    to acquire and release locks.
    """
    def __init__(
        self,
        backend: LockBackend,
    ) -> None:
        self._backend = backend

    async def __aenter__(self) -> Self:
        await self._backend.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._backend.close()

    @asynccontextmanager
    async def lock(self, key: str, timeout: float | None = None) -> AsyncIterator[None]:
        if not await self._backend.acquire(key, timeout):
            raise LockAcquisitionError(f"Could not acquire lock for key: {key}")

        try:
            yield
        finally:
            await self._backend.release(key)
