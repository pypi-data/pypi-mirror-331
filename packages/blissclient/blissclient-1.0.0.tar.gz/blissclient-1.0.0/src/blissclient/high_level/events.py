import logging
import os

import socketio

logger = logging.getLogger(__name__)


class Events:
    namespaces = ["/call", "/object"]

    def __init__(self, socket_connected: callable):
        self._socketio = None
        self._socket_connected = socket_connected

    @property
    def socketio(self):
        return self._socketio

    def create_connect(self, async_client: bool = False, wait: bool = True):
        """Create a socketio connect function with either a threaded or async client

        Kwargs:
            async_client: Use the asyncio client
            wait: Whether to block this task / thread
        """
        if async_client:
            try:
                import aiohttp  # noqa F401
            except ModuleNotFoundError:
                print(
                    "blissclient: aiohttp not installed, this is required for socketio"
                )
                exit()
            self._socketio = socketio.AsyncClient()

            async def connect():
                await self._socketio.connect(
                    os.environ["BLISSAPI_URL"], namespaces=self.namespaces
                )
                logger.info("blissclient: Connecting to SocketIO")
                self._socket_connected()
                if wait:
                    await self._socketio.wait()

            return connect
        else:
            self._socketio = socketio.Client()

            def connect():
                self._socketio.connect(
                    os.environ["BLISSAPI_URL"], namespaces=self.namespaces
                )
                logger.info("blissclient: Connecting to SocketIO")
                self._socket_connected()
                if wait:
                    self._socketio.wait()

            return connect
