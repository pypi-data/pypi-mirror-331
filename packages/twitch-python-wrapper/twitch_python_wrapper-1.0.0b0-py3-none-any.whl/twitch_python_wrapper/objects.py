from dataclasses import dataclass
from enum import Enum

from twitch_python_wrapper.enums import NotificationTransportMethod


class Objects:
    def __repr__(self):
        attributes = ", ".join(
            f"{key}={value if isinstance(value, Enum) else repr(value)}"
            for key, value in self.__dict__.items()
        )
        return f"{self.__class__.__name__}({attributes})"

    def __iter__(self):
        return iter(self.__dict__.items())

@dataclass
class NotificationTransport(Objects):
    method: NotificationTransportMethod
    callback: str | None
    secret: str | None
    session_id: str | None
    conduit_id: str | None
    connected_at: int | None
    disconnected_at: int | None
