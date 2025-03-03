import time
from typing import Literal

import psutil
from node_hermes_core.data import PhysicalDatapacket
from node_hermes_core.nodes.source_node import SourceNode


class CpuNode(SourceNode):
    class Config(SourceNode.Config):
        type: Literal["cpu_info"] = "cpu_info"

        @classmethod
        def default(cls):
            return cls()

    config: Config

    def __init__(self, config: Config | None = None):
        if config is None:
            config = self.Config.default()
        self.process = psutil.Process()

        super().__init__(config)

    def init(self):  # type: ignore
        super().init()

    def get_data(self) -> PhysicalDatapacket:
        # Define metadata points for different units
        point_percent = PhysicalDatapacket.PointDefinition(unit="%", precision=1)
        point_bytes = PhysicalDatapacket.PointDefinition(unit="B", precision=0)
        point_count = PhysicalDatapacket.PointDefinition(unit="count", precision=0)
        point_seconds = PhysicalDatapacket.PointDefinition(unit="s", precision=1)

        data = {}
        metadata = {}

        # CPU per core usage
        cpu_load_per_cpu = psutil.cpu_percent(interval=None, percpu=True)
        for i, value in enumerate(cpu_load_per_cpu):
            key = f"system.cpu.core_{i}"
            data[key] = value
            metadata[key] = point_percent

        # Memory usage
        memory = psutil.virtual_memory()
        data["system.memory.total"] = memory.total
        metadata["system.memory.total"] = point_bytes

        data["system.memory.available"] = memory.available
        metadata["system.memory.available"] = point_bytes

        data["system.memory.percent"] = memory.percent
        metadata["system.memory.percent"] = point_percent

        # PROCESS INFO
        mem_info = self.process.memory_info()
        data["process.memory.rss"] = mem_info.rss
        metadata["process.memory.rss"] = point_bytes

        data["process.memory.vms"] = mem_info.vms
        metadata["process.memory.vms"] = point_bytes

        data["process.memory.percent"] = self.process.memory_percent()
        metadata["process.memory.percent"] = point_percent

        cpu_times = self.process.cpu_times()
        data["process.cpu.user_time"] = cpu_times.user
        metadata["process.cpu.user_time"] = point_seconds

        data["process.cpu.system_time"] = cpu_times.system
        metadata["process.cpu.system_time"] = point_seconds

        data["process.cpu.usage"] = self.process.cpu_percent(interval=None)
        metadata["process.cpu.usage"] = point_percent

        # Thread count
        data["process.thread_count"] = self.process.num_threads()
        metadata["process.thread_count"] = point_count

        # System uptime (seconds since boot)
        uptime = time.time() - psutil.boot_time()
        data["system.uptime"] = uptime
        metadata["system.uptime"] = point_seconds

        return PhysicalDatapacket(
            self.name,
            timestamp=time.time(),
            data=data,
            metadata=metadata,
        )

    def deinit(self):
        super().deinit()
