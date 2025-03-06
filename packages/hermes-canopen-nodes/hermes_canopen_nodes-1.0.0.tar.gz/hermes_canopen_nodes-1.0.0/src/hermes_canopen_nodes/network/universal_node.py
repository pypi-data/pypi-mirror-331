from enum import Enum
from typing import Literal

from node_hermes_core.nodes import GenericNode, SourceNode
from node_hermes_qt.nodes import GenericQtNode
from pydantic import Field

from .generic_node import GenericCanopenNetworkNode
from .kvaeser_node import KvaeserCanopenNetworkNode
from .linux_node import LinuxCanopenNetworkNode
from .usb2can_node import Usb2CanCanopenNetworkNode


class CanopenNetworkNode(GenericNode, GenericQtNode):
    class Config(SourceNode.Config, GenericQtNode.Config):
        class SelectedInterface(Enum):
            KVAESER = "kvaeser"
            LINUX = "linux"
            USB2CAN = "usb2can"

        type: Literal["canopen"]

        enable_sync: bool = Field(default=False, description="Enable the transmission of sync messages")
        sync_frequency: float = Field(default=1, description="Frequency of sync messages in Hz")

        selected_interface: SelectedInterface = Field(description="Interface to select")
        kvaeser_config: KvaeserCanopenNetworkNode.Config = Field(
            default_factory=KvaeserCanopenNetworkNode.Config.default, description="Kvaeser interface configuration"
        )
        linux_config: LinuxCanopenNetworkNode.Config = Field(
            default_factory=LinuxCanopenNetworkNode.Config.default, description="Linux interface configuration"
        )
        usb2can_config: Usb2CanCanopenNetworkNode.Config = Field(
            default_factory=Usb2CanCanopenNetworkNode.Config.default, description="USB2CAN interface configuration"
        )

    config: Config

    interface_component: GenericCanopenNetworkNode | None = None

    def __init__(self, config: Config):
        super().__init__(config)
        GenericQtNode.__init__(self)

    def init(self):
        if self.config.selected_interface == CanopenNetworkNode.Config.SelectedInterface.KVAESER:
            assert self.config.kvaeser_config is not None, "Kvaeser interface configuration is required"
            self.interface_component = KvaeserCanopenNetworkNode(self.config.kvaeser_config)
        elif self.config.selected_interface == CanopenNetworkNode.Config.SelectedInterface.LINUX:
            assert self.config.linux_config is not None, "Linux interface configuration is required"
            self.interface_component = LinuxCanopenNetworkNode(self.config.linux_config)
        elif self.config.selected_interface == CanopenNetworkNode.Config.SelectedInterface.USB2CAN:
            assert self.config.usb2can_config is not None, "USB2CAN interface configuration is required"
            self.interface_component = Usb2CanCanopenNetworkNode(self.config.usb2can_config)
        else:
            raise ValueError("Invalid interface selected")

        # Initialize the interface component
        self.interface_component.init()

        super().init()

    def deinit(self):
        if self.interface_component is not None:
            self.interface_component.deinit()

        self.interface_component = None

        super().deinit()

    @property
    def widget(self):
        """Get the widget class for this component"""
        from .universal_interface import CanopenConfigurationWidget

        return CanopenConfigurationWidget
