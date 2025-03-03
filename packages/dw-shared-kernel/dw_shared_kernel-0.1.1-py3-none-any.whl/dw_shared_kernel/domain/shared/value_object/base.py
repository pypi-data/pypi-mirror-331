from abc import ABC
from dataclasses import dataclass


@dataclass(kw_only=True, slots=True)
class ValueObject(ABC):
    pass
