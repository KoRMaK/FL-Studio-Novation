from script.exceptions import ConflictingCommandHandlerError
from util.plain_data import PlainData


class CommandDispatcher:
    def __init__(self):
        self._handlers = {}

    def register(self, handler, command_type):
        if not isinstance(command_type, PlainData):
            raise TypeError("Supplied command type is likely an object, not a class")

        command_name = command_type.wrapped_type.__name__
        callback_name = f"handle_{command_name}"
        callback = getattr(handler, callback_name)

        if command_name in self._handlers:
            raise ConflictingCommandHandlerError(
                f"Could not register {callback=} for {command_name=}. Handler for command already registered"
            )

        self._handlers[command_name] = callback

    def unregister(self, handler, command_type):
        if not isinstance(command_type, PlainData):
            raise TypeError("Supplied command type is likely an object, not a class")
        if callable(handler):
            raise TypeError("Callable provided where class was expected.")

        command_name = command_type.wrapped_type.__name__
        callback = self._handlers[command_name]
        if callback.__self__ is not handler:
            raise ValueError("Attempting to unregister for command registered with other handler.")
        self._handlers.pop(command_name)

    def dispatch(self, command):
        command_name = type(command).__name__
        if command_name not in self._handlers:
            raise KeyError(f"No handler found for {command_name=}")
        self._handlers[command_name](command)
