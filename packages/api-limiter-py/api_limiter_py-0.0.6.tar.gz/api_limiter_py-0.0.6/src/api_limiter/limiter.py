from models.config import Config
from models.limiter import LimiterModel
from storage.protocol import AsyncStorageProtocol, SyncStorageProtocol


class Limiter[T]:
    def __init__(
        self,
        storage: SyncStorageProtocol[T],
    ) -> None:
        self._storage = storage

    def use(self, key: str, config: Config[T]):
        model = self._storage.get(key)

        if not model:
            model = LimiterModel[T](key=key)
            self._storage.set(key=key, value=model)

        if model.in_cooldown(config=config):
            raise Exception("Rate limit exceeded")

        model.use()
        self._storage.set(key=key, value=model)

    def decrement(self, key: str, config: Config[T]):
        model = self._storage.get(key=key)

        if not model:
            return

        if model.need_reset(config=config):
            model.reset()
            self._storage.set(key=key, value=model)
            return

        model.uses -= 1
        self._storage.set(key=key, value=model)


class AsyncLimiter[T]:
    def __init__(
        self,
        storage: AsyncStorageProtocol[T],
    ) -> None:
        self._storage = storage

    async def use(self, key: str, config: Config[T]) -> None:
        model = await self._storage.get(key)

        if not model:
            model = LimiterModel[T](key=key)
            await self._storage.set(key=key, value=model)

        if model.in_cooldown(config):
            raise Exception("Rate limit exceeded")

        model.use()
        await self._storage.set(key=key, value=model)

    async def decrement(self, key: str, config: Config[T]) -> None:
        model = await self._storage.get(key)

        if not model:
            return

        if model.need_reset(config):
            model.reset()
            await self._storage.set(key=key, value=model)
            return

        if not model.uses:
            return

        model.uses -= 1
        await self._storage.set(key=key, value=model)
