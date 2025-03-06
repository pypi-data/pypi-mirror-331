from abc import ABC, abstractmethod


class LockBackend(ABC):
    kind: str

    async def connect(self) -> None:  # noqa: B027
        ...

    async def close(self) -> None:  # noqa: B027
        ...

    @abstractmethod
    async def acquire(
        self,
        key: str,
        timeout: float | None = None,
        ttl: float | None = None
    ) -> bool:
        ...

    @abstractmethod
    async def release(self, key: str) -> None:
        ...
