from typing import Dict, List
from .ir import IRBlock


class HotBlockProfiler:
    def __init__(self, hot_threshold: int = 5):
        self.counts: Dict[str, int] = {}
        self.hot_threshold = hot_threshold

    def record(self, block: IRBlock) -> bool:
        h = block.hash()
        self.counts[h] = self.counts.get(h, 0) + 1
        return self.counts[h] >= self.hot_threshold


class Trace:
    def __init__(self):
        self.blocks: List[IRBlock] = []

    def add(self, block: IRBlock):
        self.blocks.append(block)

    def __iter__(self):
        return iter(self.blocks)

    def __len__(self):
        return len(self.blocks)


class TraceCache:
    def __init__(self, max_trace_len: int = 8):
        self.traces: Dict[str, Trace] = {}
        self.max_trace_len = max_trace_len

    def has(self, key: str) -> bool:
        return key in self.traces

    def get(self, key: str) -> Trace:
        return self.traces[key]

    def start_or_extend(self, key: str, block: IRBlock):
        if key not in self.traces:
            self.traces[key] = Trace()

        trace = self.traces[key]
        if len(trace) < self.max_trace_len:
            trace.add(block)
