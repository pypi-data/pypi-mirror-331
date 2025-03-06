import canopen
import time

import canopen.network


def scan():
    network = canopen.network.Network()
    network.connect(bustype="kvaser", channel=0, bitrate=1000000)

    network.scanner.search()
    time.sleep(0.1)
    print("Discovered nodes: ")
    for node_id in network.scanner.nodes:
        print(f"ID = {node_id}")
