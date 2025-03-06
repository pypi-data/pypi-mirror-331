from typing import Type

from .connection_manager import DeviceConnectionManager

from ..network.generic_node import GenericCanopenNetworkNode
from .canopen_entries import CanopenArray, CanopenInvalid, CanopenVariable
from .generic import TPDOModel


class CanopenMockDevice(GenericCanopenNetworkNode):
    def __init__(self, network_node: GenericCanopenNetworkNode, eds_path: str, id: int):
        # Connection manager for device
        self.connection_manager = DeviceConnectionManager()

        pass

    def reset(self):
        pass

    def get_heartbeat_interval(self) -> int:
        return 1000

    def set_hearbeat_interval(self, ms: int):
        return True

    def read_sdo(
        self, index: int | str, subindex: int | str | None = None
    ) -> CanopenVariable | CanopenArray | CanopenInvalid:
        return CanopenVariable(index=0x1535, value=123, is_writeable=True)

    def write_sdo(
        self,
        value: int | float | bool,
        index: int | str,
        subindex: int | str | None = None,
    ) -> bool:
        return True

    def attach_tpdo(self, tpdo_name: str, tpdo_id: int, model: "Type[TPDOModel]", callback):
        pass

    def close(self):
        pass
