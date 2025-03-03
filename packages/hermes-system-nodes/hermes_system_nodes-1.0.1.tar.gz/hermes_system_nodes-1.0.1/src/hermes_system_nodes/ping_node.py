import time
from typing import Literal

from node_hermes_core.data import PhysicalDatapacket
from node_hermes_core.nodes.source_node import SourceNode
from pythonping import ping


class PingNode(SourceNode):
    class Config(SourceNode.Config):
        type: Literal["pingv2"] = "pingv2"
        target: str = "8.8.8.8"  # Default target host.
        count: int = 1  # Number of ping packets.
        timeout: int = 1  # Timeout (in seconds) for each ping.

        @classmethod
        def default(cls):
            return cls()

    config: Config

    def __init__(self, config: Config | None = None):
        if config is None:
            config = self.Config.default()
        super().__init__(config)

    def init(self):  # type: ignore
        super().init()

    def get_data(self) -> PhysicalDatapacket:
        avg_rtt: float = -1
        try:
            # Send ping requests to the target.
            response = ping(self.config.target, count=self.config.count, timeout=self.config.timeout)
            avg_rtt = float(response.rtt_avg_ms)
        except Exception:
            pass

        data = {
            "avg_rtt": avg_rtt,
        }
        metadata = {
            "avg_rtt": PhysicalDatapacket.PointDefinition(unit="ms", precision=1),
        }

        return PhysicalDatapacket(
            self.name,
            timestamp=time.time(),
            data=data,
            metadata=metadata,
        )

    def deinit(self):
        super().deinit()
