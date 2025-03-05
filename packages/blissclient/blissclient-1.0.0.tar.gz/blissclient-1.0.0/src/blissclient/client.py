import os

from .high_level.info import Info
from .high_level.session import Session
from .high_level.hardware import Hardware
from .high_level.events import Events


class BlissClient:
    def __init__(self):
        self._events = Events(self._socket_connected)
        self._hardware = Hardware(self._events)
        self._info = Info(self._events)
        self._session = Session(
            self._events, session_name=self.info.session, hardware=self._hardware
        )
        self._hardware.set_session(self._session)

    def __str__(self):
        return f"BlissClient: {self.url}\n  Beamline: {self.beamline}\n  Session: {self.info.session}"

    def _socket_connected(self):
        self._hardware.socket_connected()
        self._session.socket_connected()

    def create_connect(self, async_client: bool = False, wait: bool = True):
        """Return a socketio creation function"""
        return self._events.create_connect(async_client=async_client, wait=wait)

    @property
    def url(self):
        return os.environ["BLISSAPI_URL"]

    @property
    def info(self):
        return self._info.info

    @property
    def beamline(self):
        return self.info.beamline

    @property
    def session(self):
        return self._session

    @property
    def hardware(self):
        return self._hardware
