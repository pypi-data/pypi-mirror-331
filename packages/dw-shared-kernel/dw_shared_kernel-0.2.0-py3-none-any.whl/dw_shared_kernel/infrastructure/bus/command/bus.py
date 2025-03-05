from collections.abc import Callable, Awaitable

from dw_shared_kernel.infrastructure.bus.command.handler import CommandHandler
from dw_shared_kernel.infrastructure.bus.command.command import Command
from dw_shared_kernel.infrastructure.bus.middleware.base import BusMiddleware


__all__ = ("CommandBus",)


class CommandBus:
    def __init__(
        self,
        middlewares: list[BusMiddleware] | None = None,
    ):
        self._handlers: dict[type[Command], CommandHandler] = {}
        self._middlewares = middlewares or []
        self._middleware_chain: Callable[[Command], Awaitable[None]] = self._build_middleware_chain()

    def register(
        self,
        command: type[Command],
        handler: CommandHandler,
    ) -> None:
        self._handlers[command] = handler

    async def handle(
        self,
        command: Command,
    ) -> None:
        await self._middleware_chain(command)

    def add_middlewares(
        self,
        middlewares: list[BusMiddleware],
    ) -> None:
        self._middlewares = middlewares + self._middlewares
        self._middleware_chain = self._build_middleware_chain()

    def _build_middleware_chain(self) -> Callable[[Command], Awaitable[None]]:
        async def command_executor(command: Command) -> None:
            command_handler = self._handlers.get(command.__class__)

            if not command_handler:
                raise ValueError(f"Command handler doesn't exist for the '{command.__class__}' command")

            await command_handler(command=command)

        def wrapped_middleware(
            middleware: BusMiddleware,
            next_handler: Callable[[Command], Awaitable[None]],
        ) -> Callable[[Command], Awaitable[None]]:
            async def wrapped_handler(command: Command) -> None:
                return await middleware(
                    message=command,
                    next_=next_handler,
                )

            return wrapped_handler

        for mdl in self._middlewares[::-1]:
            command_executor = wrapped_middleware(  # type: ignore
                middleware=mdl,
                next_handler=command_executor,
            )

        return command_executor
