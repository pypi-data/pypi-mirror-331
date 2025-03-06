import time
from typing import Literal, List

from node_hermes_core.data.datatypes import SinglePointDataPacket
from node_hermes_core.depencency.node_dependency import NodeDependency
from node_hermes_core.nodes.source_node import SourceNode
from pydantic import BaseModel, Field, PrivateAttr

from ..network import (
    GenericCanopenNetworkNode,
    KvaeserCanopenNetworkNode,
    LinuxCanopenNetworkNode,
    Usb2CanCanopenNetworkNode,
)
from .device import CanopenDevice
from .mock_device import CanopenMockDevice


class PDOConfigModel(BaseModel):
    format: str
    _name: str = PrivateAttr()
    pdo_id: int


class GroupProbeVariable(BaseModel):
    group: str
    variable: str


class CanopenDeviceNode(SourceNode):
    class Config(SourceNode.Config):
        type: Literal["canopen_device"]
        device_id: int = Field(description="The device ID for the node")

        eds_path: str = Field(title="EDS Path", description="Path to the EDS file for the node")

        mock: bool = False
        canopen_interface: (
            KvaeserCanopenNetworkNode.Config
            | LinuxCanopenNetworkNode.Config
            | Usb2CanCanopenNetworkNode.Config
            | str
            | None
        ) = Field(description="The canopen interface to use for the node, either a string or a config object")
        probed_variables: "List[GroupProbeVariable]" = Field(
            default_factory=list, title="Probed Variables", description="Variables to probe from the device"
        )

    config: Config
    canopen_interface: GenericCanopenNetworkNode | None = None
    device: CanopenDevice | CanopenMockDevice | None = None

    def __init__(self, config: Config) -> None:
        super().__init__(config)

        self.base_dependency = NodeDependency(
            name="interface",
            config=config.canopen_interface,
            reference=GenericCanopenNetworkNode,
        )
        self.dependency_manager.add(self.base_dependency)

    def init(self, canopen_interface: GenericCanopenNetworkNode) -> None:  # type: ignore
        self.canopen_interface = canopen_interface

        assert (
            self.canopen_interface.interface is not None
        ), "Canopen interface must be initialized before initializing the device"

        # Initialize the device interface
        if not self.config.mock:
            self.device = CanopenDevice(self.canopen_interface, self.config.eds_path, self.config.device_id)
        else:
            self.device = CanopenMockDevice(self.canopen_interface, self.config.eds_path, self.config.device_id)

    def deinit(self):
        if self.device is not None:
            self.device.close()
            self.device = None
        return super().deinit()

    def watch_state(self):
        assert self.device is not None, "Device interface must be initialized before watching state"
        self.device.connection_manager.update()

    def work(self) -> None:
        self.send_data(self.get_data())

    def get_data(self) -> SinglePointDataPacket:
        # Update state watchdog
        assert self.device is not None, "Canopen device was not initialized"
        self.watch_state()
        data = {}

        for probe in self.config.probed_variables:
            try:
                data[f"{probe.group}.{probe.variable}"] = self.device.read_sdo(probe.group, probe.variable).value  # type: ignore
            except Exception as e:
                print(e)
                pass
                # self.fail_frequency_counter.update(1)
                # variabe = f"{device_name}/{probe.group}/{probe.variable}"
                # self.log.warning(
                #     f"failed to read data, {self.fail_frequency_counter.frequency:.2f},variable {variabe},  error count = {self.fail_frequency_counter.count}"
                # )

                # if self.fail_frequency_counter.frequency > 50:
                #     raise

        return SinglePointDataPacket(
            source=self.config._device_name,
            timestamp=time.time(),
            data=data,
        )


# This should be present in the base canopen interface
# Check if sync has stopped, and restart it if it has
# if self.enable_sync and self.network.sync._task._task.stopped:  # type: ignore
#     self.network.sync.start(1 / self.sync_rate)

# self.network.check()
