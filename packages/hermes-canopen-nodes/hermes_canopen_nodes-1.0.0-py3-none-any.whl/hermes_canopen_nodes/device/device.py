import logging
import time
from typing import Type

import canopen
import canopen.network
import canopen.objectdictionary
import canopen.sdo
import canopen.sdo.base

from .canopen_entries import CanopenArray, CanopenInvalid, CanopenVariable
from ..network.generic_node import GenericCanopenNetworkNode
from .connection_manager import DeviceConnectionManager
from .generic import GenericCanopenDeviceNode, TPDOModel

import os


class CanopenDevice(GenericCanopenDeviceNode):
    HEARTHBEAT_INDEX = 0x1017

    def __init__(self, network_node: GenericCanopenNetworkNode, eds_path: str, id: int):
        self.network_node = network_node

        assert self.network_node.interface is not None, "Interface is not initialized"

        # Check if ids path is valid and exists
        assert os.path.exists(eds_path), f"EDS file {eds_path} does not exist"

        # Load node
        self.node = self.network_node.interface.add_node(id, eds_path)
        self.node.sdo.MAX_RETRIES = 2  # type: ignore
        self.node.sdo.RESPONSE_TIMEOUT = 0.1

        self.log = logging.getLogger(f"CanopenDevice_{id}")

        # Connection manager for device
        self.connection_manager = DeviceConnectionManager()

        # Subscribe to NMT heartbeat
        assert self.node.id is not None, "Node ID is None"
        self.network_node.interface.subscribe(0x700 + int(self.node.id), callback=self.connection_state_callback)

        self.connection_manager.on_connect.connect(self.on_connect)

    def connection_state_callback(self, id, data: bytearray, timestamp):
        """Callback for NMT heartbeat messages"""

        # boot message
        if data[0] == 0x00:
            class_name = self.__class__.__name__
            self.log.info(f"{class_name} {self.node.id} booting up")

            self.connection_manager.heartbeat_received()
            self.connection_manager.set_state(DeviceConnectionManager.State.DISCONNECTED)

        # Heartbeat
        elif data[0] == 0x05:
            self.connection_manager.heartbeat_received()

    def on_connect(self):
        time.sleep(0.3)

        try:
            # When connected read TPDOs
            with self.lock:
                self.node.tpdo.read()
            self.log.info("TPDOs read")

        except Exception as e:
            self.log.exception(f"Error in tpdo fetching: {e}")

    @property
    def lock(self):
        return self.network_node.lock

    def reset(self):
        """Reset the device"""
        with self.lock:
            self.node.nmt.state = "RESET"
        self.node.nmt.wait_for_bootup(1)

    def get_heartbeat_interval(self) -> int:
        """Get the heartbeat interval"""
        heatbeat = self.read_sdo(self.HEARTHBEAT_INDEX)
        if isinstance(heatbeat, CanopenVariable):
            assert isinstance(heatbeat.value, int), "Heartbeat value is not an integer"
            return heatbeat.value
        else:
            raise ValueError(f"Invalid heartbeat value {heatbeat}")

    def set_hearbeat_interval(self, ms: int):
        """Set the heartbeat interval"""
        self.write_sdo(ms, self.HEARTHBEAT_INDEX)

    def read_sdo(
        self, index: int | str, subindex: int | str | None = None
    ) -> CanopenVariable | CanopenArray | CanopenInvalid:
        if subindex is None:
            sdo = self.node.sdo[index]
        else:
            sdo = self.node.sdo[index][subindex]  # type: ignore
        return self.read(sdo)  # type: ignore

    def write_sdo(
        self,
        value: int | float | bool,
        index: int | str,
        subindex: int | str | None = None,
    ) -> bool:
        if subindex is None:
            sdo = self.node.sdo[index]
        else:
            sdo = self.node.sdo[index][subindex]  # type: ignore
        return self.write(sdo, value)  # type: ignore

    def read(
        self, obj: canopen.sdo.base.SdoArray | canopen.sdo.base.SdoVariable
    ) -> CanopenVariable | CanopenArray | CanopenInvalid:
        with self.lock:
            if isinstance(obj, canopen.sdo.base.SdoArray):
                try:
                    return CanopenArray(
                        is_writeable=False, value=[value.phys for value in obj.values()], index=obj.od.index
                    )

                except Exception:
                    return CanopenInvalid(is_writeable=False, index=obj.od.index)

            elif isinstance(obj, canopen.sdo.base.SdoVariable):
                if obj.od.data_type == canopen.objectdictionary.BOOLEAN:
                    return CanopenVariable(is_writeable=obj.od.writable, value=bool(obj.phys), index=obj.index)
                else:
                    return CanopenVariable(is_writeable=obj.od.writable, value=obj.phys, index=obj.index)  # type: ignore
            else:
                raise ValueError(f"Unknown object type {obj}")

    def write(self, obj: canopen.sdo.base.SdoVariable | canopen.sdo.base.SdoArray, value: int | float | bool) -> bool:
        with self.lock:
            if isinstance(obj, canopen.sdo.base.SdoArray):
                # Not implemented for arrays
                return False

            elif isinstance(obj, canopen.sdo.base.SdoVariable):
                try:
                    obj.phys = value
                    return True

                except Exception as e:
                    self.log.error(f"Error writing value {value} to {obj.name}: {e}")
                    return False
            else:
                return False

    def dump_dict(
        self, filter_readonly: bool = True, filer_application_only: bool = True, error_tolerant: bool = False
    ):
        error_counter = 0

        data_dict = {}
        for obj in self.node.sdo.values():
            try:
                if isinstance(obj, canopen.sdo.base.Record):
                    sub_objects = {}
                    for subobj in obj.values():
                        subobj: canopen.sdo.base.SdoVariable
                        if subobj.subindex == 0:
                            continue
                        sub_objects[subobj.name] = self.read(subobj)
                    data_dict[obj.od.name] = sub_objects

                elif isinstance(obj, canopen.sdo.base.SdoVariable):
                    data_dict[obj.od.name] = self.read(obj)

                elif isinstance(obj, canopen.sdo.base.SdoArray):
                    data_dict[obj.od.name] = self.read(obj)

            except Exception as e:
                if error_tolerant:
                    error_counter += 1
                    self.log.warning(f"Error reading {obj}: {e}")

                    if error_counter > 10:
                        raise e

                    continue
                else:
                    self.log.error(f"Error reading {obj}: {e}")
                    raise e

        return data_dict

    def attach_tpdo(self, tpdo_name: str, tpdo_id: int, model: Type[TPDOModel], callback):
        self.node.tpdo[tpdo_id].add_callback(
            lambda data: callback(tpdo_name, model.from_tpdo(data)),
        )

    def close(self):
        self.node.pdo.stop()
        self.node.rpdo.stop()
        self.node.remove_network()
        self.log.info("Device closed")
