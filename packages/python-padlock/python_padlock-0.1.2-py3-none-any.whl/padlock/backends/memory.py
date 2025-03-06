import asyncio
from collections import defaultdict

from padlock.backends.base import LockBackend


class MemoryLockBackend(LockBackend):
    kind = "memory"

    def __init__(self) -> None:
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def acquire(
        self,
        key: str,
        timeout: float | None = None,
        ttl: float | None = None
    ) -> bool:
        try:
            await asyncio.wait_for(self._locks[key].acquire(), timeout)
            return True
        except Exception:
            pass

        return False

    async def release(self, key: str) -> None:
        self._locks[key].release()
