from api_limiter.models.limiter import LimiterModel

from .protocol import SyncStorageProtocol


class StorageInMemory[T](SyncStorageProtocol[T]):
    def __init__(self) -> None:
        self._storage: dict[str, LimiterModel[T]] = {}

    def get(self, key: str) -> LimiterModel[T] | None:
        return self._storage.get(key)

    def set(self, key: str, value: LimiterModel[T]) -> None:
        self._storage[key] = value
