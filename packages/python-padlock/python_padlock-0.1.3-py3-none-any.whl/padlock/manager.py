from contextlib import asynccontextmanager
from typing import AsyncIterator, Self

from padlock.backends.base import LockBackend
from padlock.errors import LockAcquisitionError


class LockManager:
    """
    A high-level lock manager that provides a context manager
    to acquire and release locks with a given LockBackend.
    """
    def __init__(
        self,
        backend: LockBackend,
    ) -> None:
        self._backend = backend

    @property
    def kind(self) -> str:
        """
        Return the kind of the lock backend.

        :return: The kind of the lock backend.
        :rtype: str
        """
        return self._backend.kind

    async def __aenter__(self) -> Self:
        await self._backend.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._backend.close()

    @asynccontextmanager
    async def lock(
        self,
        key: str,
        timeout: float | None = None,
        ttl: float | None = None,
    ) -> AsyncIterator[None]:
        """
        Lock a key using the lock manager.

        :param key: The key to lock.
        :type key: str
        :param timeout: The maximum time to wait for the lock.
        :type timeout: float | None
        :param ttl: The time-to-live for the lock.
        :type ttl: float | None
        :raises LockAcquisitionError: If the lock could not be acquired.
        :return: A context manager to acquire and release the lock.
        :rtype: AsyncIterator[None]
        """
        if not await self._backend.acquire(key, timeout, ttl):
            raise LockAcquisitionError(f"Could not acquire lock for key: {key}")

        try:
            yield
        finally:
            await self._backend.release(key)
