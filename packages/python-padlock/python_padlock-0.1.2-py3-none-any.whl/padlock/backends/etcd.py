import asyncio

from etcd_client import Client as EtcdClient
from etcd_client import EtcdLockOption

from padlock.backends.base import LockBackend


class EtcdLockBackend(LockBackend):
    kind = "etcd"

    def __init__(self, endpoints: list[str]) -> None:
        self._client = EtcdClient(endpoints)
        self._locks: dict[str, EtcdClient] = {}

    async def acquire(
        self,
        key: str,
        timeout: float | None = None,
        ttl: float | None = None
    ) -> bool:
        lock = self._client.with_lock(
            EtcdLockOption(key.encode(), timeout=timeout, ttl=int(ttl) if ttl else None)
        )

        try:
            await asyncio.wait_for(lock.__aenter__(), timeout)
            self._locks[key] = lock
            return True
        except Exception:
            pass

        return False

    async def release(self, key: str) -> None:
        if (lock := self._locks.pop(key, None)):
            await lock.__aexit__(None, None, None)
