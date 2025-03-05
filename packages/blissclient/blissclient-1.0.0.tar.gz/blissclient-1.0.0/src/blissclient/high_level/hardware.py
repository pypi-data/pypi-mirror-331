import logging
import time
from typing import Any, Callable, Dict, List, Literal

from ..openapi.api_config import APIConfig
from .base import Base
from ..exceptions import BlissRESTError

from ..openapi.services.ObjectApi_service import (
    _HardwaresResourceV1_post_post,
    _HardwaresResourceV1_get_get,
    _HardwareResourceV1_get__string_name__get,
    _HardwareResourceV1_put__string_name__put,
)
from ..openapi.services.ObjectTypeApi_service import (
    _ObjectTypesResource_get_get,
    _ObjectTypeResource_get__string_id__get,
)
from ..openapi.models.RegisterHardwareSchema import RegisterHardwareSchema
from ..openapi.models.SetObjectProperty import SetObjectProperty
from ..openapi.models.ObjectSchema import ObjectSchema
from ..openapi.models.ObjectTypeSchema import ObjectTypeSchema

logger = logging.getLogger(__name__)


class HardwareObject:
    """A `HardwareObject`

    Properties are mapped to python properties:
        print(omega.position)
        omega.velocity = 2000

    Functions can be directly called:
        omega.move(10)

    """

    _update_interval = 0.2

    def __init__(
        self,
        address: str,
        session,
        api_config: APIConfig,
        object_types: List[ObjectTypeSchema],
        initial_state: ObjectSchema = None,
        evented: bool = False,
    ):
        self._last_status_time = 0
        self._state: ObjectSchema = initial_state
        self._api_config = api_config
        self._address = address
        self._session = session
        self._evented = evented

        self._property_changed_callbacks: List[Callable] = []
        self._online_changed_callbacks: List[Callable] = []
        self._locked_changed_callbacks: List[Callable] = []

        self._get_status()

        for object_type in object_types:
            if object_type.type == self._state.type:
                self._object_type = object_type
                break
        else:
            self._object_type = _ObjectTypeResource_get__string_id__get(
                self._state.type, api_config_override=self._api_config
            )

        for callable in self._object_type.callables:
            setattr(self, callable, self._make_callable(callable))

    def subscribe(
        self, event_type: Literal["property", "online", "locked"], callback: Callable
    ):
        """Subscribe to an event on this object

        This can subscribe to object
            - property changes (position, velocity, etc)
            - online status changes
            - lock changes
        """
        if event_type == "property":
            if callback not in self._property_changed_callbacks:
                self._property_changed_callbacks.append(callback)
        if event_type == "online":
            if callback not in self._online_changed_callbacks:
                self._online_changed_callbacks.append(callback)
        if event_type == "locked":
            if callback not in self._locked_changed_callbacks:
                self._locked_changed_callbacks.append(callback)

    def set_evented(self, evented: bool):
        self._evented = evented

    def __dir__(self):
        return super().__dir__() + list(self._state.properties.keys())

    def __str__(self):
        properties = "".join(
            [
                f"  {property}:\t{value}\n"
                for property, value in self._state.properties.items()
            ]
        )
        callables = ", ".join(self._object_type.callables)

        errors = ""
        if self.errors:
            errors = f"! Errors: \n  {self.errors}"

        locked = "None"
        if self._state.locked:
            locked = self._state.locked.reason

        return f"""Address: {self._address} ({self.type})
{errors}
Online: {self._state.online}
Lock State: {locked}

Properties:
{properties}

Callables:
  {callables}

"""

    @property
    def name(self):
        return self._address

    @property
    def type(self):
        return self._state.type

    @property
    def errors(self):
        return self._state.errors

    @property
    def properties(self):
        return self._state.properties

    def __getattr__(self, item):
        state = object.__getattribute__(self, "_state")
        if state:
            get_status = object.__getattribute__(self, "_get_status")
            get_status()
            state = object.__getattribute__(self, "_state")
            if item in state.properties:
                return state.properties[item]

        return super().__getattribute__(item)

    def __setattr__(self, item: str, value: Any):
        if hasattr(self, "_state"):
            if self._state:
                if item in self._state.properties:
                    self._set(item, value)

        return super().__setattr__(item, value)

    def _make_callable(self, function: str):
        def call_function(*args, **kwargs):
            return self._call(function, *args, **kwargs)

        return call_function

    def update_state(self, log: bool = True):
        """Request update of state"""
        if log:
            logger.info(f"Requesting state for {self.name}")
        self._state = _HardwareResourceV1_get__string_name__get(
            name=self._address, api_config_override=self._api_config
        )

    def _get_status(self):
        if self._evented:
            return

        now = time.time()
        if now - self._last_status_time > self._update_interval:
            self.update_state(log=False)
            self._last_status_time = now
        else:
            logger.debug(
                f"Requesting update for {self.name}, ignoring last update {now - self._last_status_time}s ago"
            )

    def _call(self, function: str, *args, **kwargs):
        return self._session.call(function, object_name=self.name, *args, **kwargs)

    def _set(self, property: str, value: Any):
        return _HardwareResourceV1_put__string_name__put(
            name=self._address,
            data=SetObjectProperty(property=property, value=value),
            api_config_override=self._api_config,
        )

    def _update_property(self, data: Dict[str, Any]):
        logger.debug(f"_update_property `{self.name}` `{data}`")
        for key, value in data.items():
            if key in self._state.properties.keys():
                self._state.properties[key] = value

        for callback in self._property_changed_callbacks:
            callback(data)

    def _update_online(self, online: bool):
        logger.debug(f"_update_online `{self.name}` {online}")
        self._state.online = online
        for callback in self._online_changed_callbacks:
            callback(online)

    def _update_locked(self, reason: dict):
        logger.debug(f"_update_locked {self.name} {reason}")
        self._state.locked = reason
        for callback in self._locked_changed_callbacks:
            callback(reason)


class Hardware(Base):
    socketio_namespace = "/object"

    def __init__(self, events):
        self._session = None
        self._objects: dict[str, HardwareObject] = {}
        self._cached_initial_statuses: Dict[str, ObjectSchema] = {}

        self._evented = False
        super().__init__(events)

        self._object_types = _ObjectTypesResource_get_get(
            api_config_override=self._api_config
        )

    def set_session(self, session):
        self._session = session

    def _socket_connected(self):
        self._on("change", self._on_change_event)
        self._on("online", self._on_online_event)
        self._on("locked", self._on_locked_event)
        self._evented = True
        for obj in self._objects.values():
            obj.set_evented(True)

    def _on_change_event(self, event_data: Dict[str, Any] = None):
        object_id = event_data.get("id")
        data = event_data.get("data")
        if isinstance(data, dict):
            if object_id in self._objects:
                self._objects[object_id]._update_property(data)

    def _on_online_event(self, event_data: Dict[str, Any] = None):
        object_id = event_data.get("id")
        if object_id in self._objects:
            self._objects[object_id]._update_online(event_data.get("state"))

    def _on_locked_event(self, event_data: Dict[str, Any] = None):
        object_id = event_data.get("id")
        logger.debug(f"_on_locked_event {event_data}")
        if object_id in self._objects:
            self._objects[object_id]._update_locked(event_data.get("state"))

    def __str__(self):
        objects = "".join([f"  {address}\n" for address in self.available])
        return f"Hardware:\n{objects}"

    def _get_initial_status(self):
        response = _HardwaresResourceV1_get_get(api_config_override=self._api_config)
        self._cached_initial_statuses = {item.name: item for item in response.results}

    @property
    def available(self):
        """List the currently available `HardwareObjects`"""
        return list(self._cached_initial_statuses.keys())

    def register(self, *addresses: List[str]):
        """Register a `HardwareObject` with the bliss REST API"""
        response = _HardwaresResourceV1_post_post(
            data=RegisterHardwareSchema(names=addresses),
            api_config_override=self._api_config,
        )
        self._get_initial_status()
        return response

    def get(self, address: str):
        """Get a hardware object from its beacon `address`"""
        if address in self._objects:
            return self._objects[address]

        if address not in self.available:
            try:
                logger.info(
                    f"Object `{address}` not yet available, trying to register it..."
                )
                self.register(address)
            except BlissRESTError:
                raise KeyError(
                    f"Object `{address}` not available, are you are sure it exists in beacon?"
                )

        obj = HardwareObject(
            address=address,
            session=self._session,
            api_config=self._api_config,
            object_types=self._object_types.results,
            initial_state=self._cached_initial_statuses.get(address),
            evented=self._evented,
        )
        self._objects[address] = obj
        return obj
