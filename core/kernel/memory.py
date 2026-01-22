class VirtualMemoryManager:
    def __init__(self, base=0x10000000, limit=0x80000000):
        self.base = base
        self.limit = limit
        self.next_addr = base
        self.allocations = {}

    def mmap(self, size: int) -> int:
        size = (size + 0xFFF) & ~0xFFF  # page align
        if self.next_addr + size > self.limit:
            raise MemoryError("Out of virtual memory")

        addr = self.next_addr
        self.allocations[addr] = size
        self.next_addr += size
        return addr

    def munmap(self, addr: int):
        if addr not in self.allocations:
            raise RuntimeError(f"Invalid munmap addr 0x{addr:x}")
        del self.allocations[addr]
