from abc import ABC, abstractmethod

from api_limiter.models.limiter import LimiterModel


class SyncStorageProtocol[T](ABC):
    @abstractmethod
    def get(self, key: str) -> LimiterModel[T] | None: ...

    @abstractmethod
    def set(self, key: str, value: LimiterModel[T]) -> None: ...


class AsyncStorageProtocol[T](ABC):
    @abstractmethod
    async def get(self, key: str) -> LimiterModel[T] | None: ...

    @abstractmethod
    async def set(self, key: str, value: LimiterModel[T]) -> None: ...
