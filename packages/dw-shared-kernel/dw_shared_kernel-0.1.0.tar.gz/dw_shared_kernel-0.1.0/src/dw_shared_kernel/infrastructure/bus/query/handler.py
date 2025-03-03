from abc import ABC, abstractmethod

from dw_shared_kernel.infrastructure.bus.query.message import Query


class QueryHandler[QUERY: Query, RESULT](ABC):
    @abstractmethod
    async def __call__(self, query: QUERY) -> RESULT: ...
