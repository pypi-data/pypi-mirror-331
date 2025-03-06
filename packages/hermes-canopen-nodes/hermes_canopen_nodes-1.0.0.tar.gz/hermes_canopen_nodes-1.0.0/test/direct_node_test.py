import logging
import time

from hermes_canopen_nodes.network import KvaeserCanopenNetworkNode
from hermes_canopen_nodes.device.node import CanopenDeviceNode

logging.basicConfig(level=logging.INFO)

canopen = KvaeserCanopenNetworkNode(
    KvaeserCanopenNetworkNode.Config(
        type="kvaeser_canopen",
        channel=KvaeserCanopenNetworkNode.Config.Channels.CHANNEL_0,
        bitrate=KvaeserCanopenNetworkNode.Config.Bitrates.BITRATE_1000000,
    )
)
canopen.init()

node_config = CanopenDeviceNode.Config(
    type="canopen_device",
    device_id=0x01,
    eds_path=r"test\eds\project.eds",
    canopen_interface=None,
)

node = CanopenDeviceNode(node_config)
node.init(canopen)


time.sleep(1)
assert node.device is not None
node.device.read_sdo(0x1000)

time.sleep(1)

node.deinit()
canopen.deinit()
