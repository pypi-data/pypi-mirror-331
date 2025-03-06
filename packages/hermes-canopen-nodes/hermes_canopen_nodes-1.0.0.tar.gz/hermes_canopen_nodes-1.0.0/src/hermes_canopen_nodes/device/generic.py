from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel

from .canopen_entries import CanopenArray, CanopenInvalid, CanopenVariable
from ..network.generic_node import GenericCanopenNetworkNode


class GenericCanopenDeviceNode(ABC):
    pass


class CanopenDevice:
    @abstractmethod
    def __init__(self, network_node: GenericCanopenNetworkNode, eds_path: str, id: int): ...

    @abstractmethod
    def reset(self): ...

    @abstractmethod
    def get_heartbeat_interval(self) -> int: ...

    @abstractmethod
    def set_hearbeat_interval(self, ms: int): ...

    @abstractmethod
    def read_sdo(
        self, index: int | str, subindex: int | str | None = None
    ) -> CanopenVariable | CanopenArray | CanopenInvalid: ...

    @abstractmethod
    def write_sdo(
        self,
        value: int | float | bool,
        index: int | str,
        subindex: int | str | None = None,
    ) -> bool: ...

    @abstractmethod
    def attach_tpdo(self, tpdo_name: str, tpdo_id: int, model: "Type[TPDOModel]", callback): ...

    @abstractmethod
    def close(self): ...


class TPDOModel(BaseModel):
    """Abstract class for TPDO models used to interpret TPDO data from CANopen devices"""

    @classmethod
    def from_tpdo(cls, tpdo):
        return cls.from_dict({v.name: v.raw for v in tpdo})

    @classmethod
    def from_dict(cls, d: dict) -> "TPDOModel": ...


class PDOPacket(ABC):
    @abstractmethod
    def to_class(self) -> "Type[TPDOModel]": ...
