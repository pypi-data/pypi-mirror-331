from dw_shared_kernel.infrastructure.bus.command.bus import CommandBus
from dw_shared_kernel.infrastructure.bus.query.bus import QueryBus
from dw_shared_kernel.infrastructure.di.container import Container
from dw_shared_kernel.infrastructure.di.layer import Layer


class InfrastructureLayer(Layer):
    def setup(
        self,
        container: Container,
    ) -> None:
        container[QueryBus] = QueryBus()
        container[CommandBus] = CommandBus()
