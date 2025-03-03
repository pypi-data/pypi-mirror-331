from collections.abc import Iterable

from dw_shared_kernel.infrastructure.di.container import Container
from dw_shared_kernel.infrastructure.di.layer import Layer


def get_di_container(
    layers: Iterable[Layer],
) -> Container:
    container = Container()

    for layer in layers:
        layer.setup(
            container=container,
        )

    return container
