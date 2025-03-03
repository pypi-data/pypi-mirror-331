from abc import ABC
from dataclasses import dataclass
from typing import Any


@dataclass(kw_only=True)
class Entity[ID](ABC):
    id: ID

    def __eq__(self, other: Any) -> bool:
        return other.id == self.id if isinstance(other, Entity) else False
