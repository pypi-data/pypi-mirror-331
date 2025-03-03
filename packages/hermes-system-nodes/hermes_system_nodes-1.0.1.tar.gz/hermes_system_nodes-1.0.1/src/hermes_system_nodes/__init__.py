from .cpu_node import CpuNode
from .ping_node import PingNode

NODES = [CpuNode, PingNode]

__all__ = ["NODES"]
