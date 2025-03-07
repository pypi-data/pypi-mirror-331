from dataclasses import dataclass
from datetime import timedelta
from typing import Annotated, Callable


@dataclass
class Config[T]:
    key: Annotated[Callable[[T], str], "Handler function"]
    uses: Annotated[int, "Number of uses allowed in the cooldown period"]
    cooldown: Annotated[timedelta, "Cooldown period"]
