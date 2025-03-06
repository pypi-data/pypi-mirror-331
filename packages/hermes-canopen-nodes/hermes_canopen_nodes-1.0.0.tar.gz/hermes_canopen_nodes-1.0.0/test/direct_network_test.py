import logging
import time

from hermes_canopen_nodes.network import KvaeserCanopenNetworkNode

logging.basicConfig(level=logging.INFO)


config = KvaeserCanopenNetworkNode.Config(
    type="kvaeser_canopen",
    channel=KvaeserCanopenNetworkNode.Config.Channels.CHANNEL_0,
    bitrate=KvaeserCanopenNetworkNode.Config.Bitrates.BITRATE_1000000,
)

node = KvaeserCanopenNetworkNode(config)

node.init()

time.sleep(1)
node.deinit()
