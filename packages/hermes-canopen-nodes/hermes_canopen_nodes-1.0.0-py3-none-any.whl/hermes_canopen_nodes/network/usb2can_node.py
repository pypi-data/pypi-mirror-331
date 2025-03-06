from typing import Literal

import canopen.network
from pydantic import Field
from .generic_node import GenericCanopenNetworkNode


class Usb2CanCanopenNetworkNode(GenericCanopenNetworkNode):
    class Config(GenericCanopenNetworkNode.Config):
        type: Literal["usb2can_canopen"]
        serial: str = Field(default="A1B2C3D4", title="Serial number of the device")
        usb2can_dll: str = Field(default="usb2can.dll", title="Path to the usb2can.dll")

        @classmethod
        def default(cls):
            return cls(type="usb2can_canopen", serial="A1B2C3D4", usb2can_dll="usb2can.dll")

    config: Config

    def __init__(self, config: Config):
        super().__init__(config)

    def init(self):
        super().init()
        self.interface = canopen.network.Network()
        self.interface.connect(
            bustype="usb2can",
            dll=self.config.usb2can_dll,
            channel=self.config.serial,
            bitrate=self.config.bitrate.value,
        )
