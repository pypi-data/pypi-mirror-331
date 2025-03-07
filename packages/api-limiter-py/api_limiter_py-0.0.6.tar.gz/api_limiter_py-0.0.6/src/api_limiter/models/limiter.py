from dataclasses import dataclass, field
from datetime import datetime

from models.config import Config


@dataclass
class LimiterModel[T]:
    key: str
    uses: int = field(default=0)
    last_use: datetime = field(default_factory=datetime.now)

    def in_cooldown(self, config: Config[T]) -> bool:
        if self.uses >= config.uses:
            return True

        return datetime.now() < self.last_use + config.cooldown

    def reset(self) -> None:
        self.uses = 0
        self.last_use = datetime.now()

    def need_reset(self, config: Config[T]) -> bool:
        return datetime.now() > self.last_use + config.cooldown

    def use(self) -> None:
        self.uses += 1
        self.last_use = datetime.now()
