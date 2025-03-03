from abc import ABC

from pydantic import BaseModel


class Command(BaseModel, ABC):
    pass
