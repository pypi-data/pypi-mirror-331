import subprocess
from typing import Literal

import canopen.network
from pydantic import Field
from .generic_node import GenericCanopenNetworkNode


class LinuxCanopenNetworkNode(GenericCanopenNetworkNode):
    class Config(GenericCanopenNetworkNode.Config):
        type: Literal["linux_canopen"]
        channel: str = Field(default="can0", title="Channel to connect to")

        @classmethod
        def default(cls):
            return cls(type="linux_canopen", channel="can0")

    config: Config

    def __init__(self, config: Config):
        super().__init__(config)

    def init(self):
        super().init()
        # Start link
        subprocess.run(["sudo", "ip", "link", "set", "down", self.config.channel])
        subprocess.run(
            ["sudo", "ip", "link", "set", self.config.channel, "type", "can", "bitrate", str(self.config.bitrate)]
        )
        subprocess.run(["sudo", "ip", "link", "set", "up", self.config.channel])

        # Open interface
        self.interface = canopen.network.Network()
        self.interface.connect(
            bustype="socketcan", channel=self.config.channel, bitrate=self.config.bitrate, dll="usb2can.dll"
        )
