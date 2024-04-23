from uuid import uuid4

from .util import Answer
from .app import socket

disconnected = set([])


class User:
    def __init__(self):
        self.auth_key = str(uuid4())
        self._sid: str | None = None
        self._pending_messages = []

    @property
    def sid(self):
        return None if self._sid in disconnected else self._sid

    @sid.setter
    def sid(self, sid: str):
        self._sid = sid
        for message in self._pending_messages:
            self.emit(message)
            self._pending_messages.remove(message)

    def emit(self, message):
        if self.sid:
            socket.send(message, to=self.sid)
        else:
            self._pending_messages.append(message)


class Player(User):
    def __init__(self, name):
        super().__init__()
        self.name: str = name.strip().upper()
        self.money: float = 0


class Host(User):
    def __init__(self):
        super().__init__()
        self.auth_key = f"host-{self.auth_key}"
