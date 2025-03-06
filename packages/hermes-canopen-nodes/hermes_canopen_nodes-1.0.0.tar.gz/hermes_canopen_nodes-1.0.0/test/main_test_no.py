import asyncio
import logging
import sys

from asyncslot import AsyncSlotRunner
from hermes_canopen_nodes.network import KvaeserCanopenNetworkNode, CanopenNetworkNode

from qtpy import QtWidgets

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    config = CanopenNetworkNode.Config(
        type="canopen",
        selected_interface=CanopenNetworkNode.Config.SelectedInterface.KVAESER,
        kvaeser_config=KvaeserCanopenNetworkNode.Config(
            type="kvaeser_canopen",
            channel=KvaeserCanopenNetworkNode.Config.Channels.CHANNEL_0,
            bitrate=KvaeserCanopenNetworkNode.Config.Bitrates.BITRATE_1000000,
        ),
        sync_frequency=1.0,
    )

    node = CanopenNetworkNode(config)

    widget = node.widget(node)
    widget.show()

    widget.raise_()
    with AsyncSlotRunner(debug=True):
        loop = asyncio.get_event_loop()
        loop.slow_callback_duration = 0.02
        sys.exit(app.exec_())
