import asyncio

from etcd_client import Client as EtcdClient
from etcd_client import ConnectOptions, EtcdLockOption

from padlock.backends.base import LockBackend


class EtcdLockBackend(LockBackend):
    kind = "etcd"

    def __init__(
        self,
        endpoints: list[str],
        prefix: str | None = None,
        connect_timeout: float | None = None,
        keep_alive_interval: int | None = None,
        keep_alive_timeout: float | None = None,
        keep_alive_while_idle: bool | None = None,
        tcp_keepalive: float | None = None,
        timeout: float | None = None,
        user: tuple[str, str] | None = None,
    ) -> None:
        self._client = EtcdClient(
            endpoints=endpoints,
            connect_options=self._build_connect_options(
                connect_timeout=connect_timeout,
                keep_alive_interval=keep_alive_interval,
                keep_alive_timeout=keep_alive_timeout,
                keep_alive_while_idle=keep_alive_while_idle,
                tcp_keepalive=tcp_keepalive,
                timeout=timeout,
                user=user,
            ),
        )
        self._prefix = prefix
        self._locks: dict[str, EtcdClient] = {}

    def _build_connect_options(
        self,
        connect_timeout: float | None = None,
        keep_alive_interval: int | None = None,
        keep_alive_timeout: float | None = None,
        keep_alive_while_idle: bool | None = None,
        tcp_keepalive: float | None = None,
        timeout: float | None = None,
        user: tuple[str, str] | None = None,
    ) -> ConnectOptions | None:
        if not any(
            (
                connect_timeout,
                keep_alive_interval,
                keep_alive_timeout,
                keep_alive_while_idle,
                tcp_keepalive,
                timeout,
                user,
            )
        ):
            return None

        connect_options = ConnectOptions()

        if connect_timeout:
            connect_options = connect_options.with_connect_timeout(connect_timeout)
        if keep_alive_interval and keep_alive_timeout:
            connect_options = connect_options.with_keep_alive(
                keep_alive_interval, keep_alive_timeout
            )
        if keep_alive_while_idle:
            connect_options = connect_options.with_keep_alive_while_idle(
                keep_alive_while_idle
            )
        if tcp_keepalive:
            connect_options = connect_options.with_tcp_keepalive(tcp_keepalive)
        if timeout:
            connect_options = connect_options.with_timeout(timeout)
        if user:
            connect_options = connect_options.with_user(*user)

        return connect_options

    def _build_key(self, key: str) -> bytes:
        return f"{self._prefix}/{key}".encode() if self._prefix else key.encode()

    async def acquire(
        self,
        key: str,
        timeout: float | None = None,
        ttl: float | None = None
    ) -> bool:
        lock = self._client.with_lock(
            EtcdLockOption(
                lock_name=self._build_key(key),
                timeout=timeout,
                ttl=int(ttl) if ttl else None
            )
        )

        try:
            await asyncio.wait_for(lock.__aenter__(), timeout)
            self._locks[key] = lock
            return True
        except Exception as e:
            try:
                await lock.__aexit__(None, None, None)
            except Exception:
                pass

            raise e

        return False

    async def release(self, key: str) -> None:
        if (lock := self._locks.pop(key, None)):
            await lock.__aexit__(None, None, None)
