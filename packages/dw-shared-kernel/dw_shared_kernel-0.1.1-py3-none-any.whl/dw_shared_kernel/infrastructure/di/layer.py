from abc import ABC, abstractmethod

from dw_shared_kernel.infrastructure.di.container import Container


class Layer(ABC):
    @abstractmethod
    def setup(self, container: Container) -> None: ...
