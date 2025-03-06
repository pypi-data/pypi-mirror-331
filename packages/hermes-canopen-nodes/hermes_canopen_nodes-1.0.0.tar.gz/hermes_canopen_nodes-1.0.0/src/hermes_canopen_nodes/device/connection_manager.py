import logging
import time
from enum import Enum

from node_hermes_core.objs.signal import Signal


class DeviceConnectionManager:
    class State(Enum):
        DISCONNECTED = 0
        CONNECTED = 1

    last_heartbeat: float = 0
    state = State.DISCONNECTED
    on_connect: Signal
    on_disconnect: Signal
    TIMEOUT = 2

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.on_connect = Signal()
        self.on_disconnect = Signal()

    def heartbeat_received(self):
        self.last_heartbeat = time.time()

    def set_state(self, state: State):
        if self.state == state:
            return

        if state == self.State.CONNECTED:
            self.log.info("Device connected")
            self.on_connect.emit()

        elif state == self.State.DISCONNECTED:
            self.log.info("Device disconnected")
            self.on_disconnect.emit()

        self.state = state

    @property
    def is_connected(self):
        return self.state == self.State.CONNECTED

    @property
    def heartbeat_age(self):
        return time.time() - self.last_heartbeat

    def update(self):
        if self.heartbeat_age > self.TIMEOUT and self.is_connected:
            self.log.warning("No heartbeat received")
            self.set_state(self.State.DISCONNECTED)

        elif self.heartbeat_age < self.TIMEOUT and not self.is_connected:
            self.log.info("Heartbeat received")
            self.set_state(self.State.CONNECTED)
