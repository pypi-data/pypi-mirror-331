import logging
import os
from typing import Callable, List

from ..openapi.api_config import APIConfig
from .events import Events

logger = logging.getLogger(__name__)


class Base:
    socketio_namespace = None

    def __init__(self, events: Events):
        self._on_connect_callbacks: List[Callable] = []
        self._on_connect_error_callbacks: List[Callable] = []
        self._on_disconnect_callbacks: List[Callable] = []

        try:
            self._api_config = APIConfig(base_path=os.environ["BLISSAPI_URL"])
        except KeyError:
            raise RuntimeError("`BLISSAPI_URL` not defined in environemnt")

        self._events = events

    def _on(self, event: str, callback: callable):
        """Convience wrapper to register socketio event callback"""
        return self._events.socketio.on(
            event=event, handler=callback, namespace=self.socketio_namespace
        )

    def socket_connected(self):
        self._on("connect", self._on_connect)
        self._on("connect_error", self._on_connect_error)
        self._on("disconnect", self._on_disconnect)

        self._socket_connected()

    def _on_connect(self):
        logger.info(f"blissclient: Connected to namespace: {self.socketio_namespace}")
        for callback in self._on_connect_callbacks:
            callback()

    def _on_connect_error(self, err):
        logger.info(
            f"blissclient: SocketIO could not connect to `{self.socketio_namespace}`: {str(err)}"
        )
        for callback in self._on_connect_error_callbacks:
            callback(err)

    def _on_disconnect(self):
        logger.info(
            f"blissclient: SocketIO disconnected from `{self.socketio_namespace}`"
        )
        for callback in self._on_disconnect_callbacks:
            callback()
