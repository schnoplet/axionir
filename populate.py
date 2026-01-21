import os

BASE = os.getcwd()

FILES = {
    "core/ir.py": """
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, List
import hashlib

class IROp(Enum):
    NOP = auto()
    MOV = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    LOAD = auto()
    STORE = auto()
    CMP = auto()
    JMP = auto()
    BRANCH = auto()

@dataclass(frozen=True)
class IRInstr:
    op: IROp
    dst: Optional[int] = None
    src1: Optional[int] = None
    src2: Optional[int] = None
    imm: Optional[int] = None

class IRBlock:
    def __init__(self, label: str = ""):
        self.label = label
        self.instructions: List[IRInstr] = []

    def emit(self, instr: IRInstr):
        self.instructions.append(instr)

    def __len__(self):
        return len(self.instructions)

    def hash(self) -> str:
        h = hashlib.sha256()
        for i in self.instructions:
            h.update(
                f"{i.op.name}:{i.dst}:{i.src1}:{i.src2}:{i.imm}".encode()
            )
        return h.hexdigest()
""",

    "core/cpu.py": """
from .ir import IROp, IRInstr, IRBlock

class CPUState:
    def __init__(self, reg_count: int = 32):
        self.regs = [0] * reg_count
        self.pc = 0
        self.flags = {"Z": False}

class MMU:
    def __init__(self, size: int = 1024 * 1024):
        self.mem = bytearray(size)

    def read64(self, addr: int) -> int:
        return int.from_bytes(self.mem[addr:addr+8], "little")

    def write64(self, addr: int, value: int):
        self.mem[addr:addr+8] = value.to_bytes(8, "little")

class IRInterpreter:
    def __init__(self, state: CPUState, mmu: MMU):
        self.s = state
        self.m = mmu

    def exec_block(self, block: IRBlock):
        for ins in block.instructions:
            self.exec(ins)

    def exec(self, ins: IRInstr):
        r = self.s.regs

        if ins.op == IROp.NOP:
            return
        if ins.op == IROp.MOV:
            r[ins.dst] = ins.imm if ins.imm is not None else r[ins.src1]
        elif ins.op == IROp.ADD:
            r[ins.dst] = r[ins.src1] + r[ins.src2]
        elif ins.op == IROp.SUB:
            r[ins.dst] = r[ins.src1] - r[ins.src2]
        elif ins.op == IROp.MUL:
            r[ins.dst] = r[ins.src1] * r[ins.src2]
        elif ins.op == IROp.LOAD:
            r[ins.dst] = self.m.read64(r[ins.src1])
        elif ins.op == IROp.STORE:
            self.m.write64(r[ins.dst], r[ins.src1])
        elif ins.op == IROp.CMP:
            self.s.flags["Z"] = (r[ins.src1] == r[ins.src2])
""",

    "core/optimizer.py": """
from typing import Dict
from .ir import IRBlock, IRInstr, IROp

class IROptimizer:
    def constant_folding(self, block: IRBlock) -> IRBlock:
        consts: Dict[int, int] = {}
        out = IRBlock(block.label)

        for ins in block.instructions:
            if ins.op == IROp.MOV and ins.imm is not None:
                consts[ins.dst] = ins.imm
                out.emit(ins)

            elif ins.op in (IROp.ADD, IROp.SUB, IROp.MUL):
                a = consts.get(ins.src1)
                b = consts.get(ins.src2)

                if a is not None and b is not None:
                    if ins.op == IROp.ADD:
                        v = a + b
                    elif ins.op == IROp.SUB:
                        v = a - b
                    else:
                        v = a * b

                    consts[ins.dst] = v
                    out.emit(IRInstr(IROp.MOV, dst=ins.dst, imm=v))
                else:
                    out.emit(ins)
            else:
                out.emit(ins)

        return out

    def optimize(self, block: IRBlock) -> IRBlock:
        return self.constant_folding(block)
""",

    "core/cache.py": """
from typing import Dict
from .ir import IRBlock

class HotBlockProfiler:
    def __init__(self, hot_threshold: int = 5):
        self.counts: Dict[str, int] = {}
        self.hot_threshold = hot_threshold

    def record(self, block: IRBlock) -> bool:
        h = block.hash()
        self.counts[h] = self.counts.get(h, 0) + 1
        return self.counts[h] >= self.hot_threshold

class BlockCache:
    def __init__(self):
        self.cache: Dict[str, IRBlock] = {}

    def get_or_add(self, block: IRBlock) -> IRBlock:
        h = block.hash()
        if h not in self.cache:
            self.cache[h] = block
        return self.cache[h]
""",

    "core/scheduler.py": """
class Scheduler:
    def __init__(self):
        self.cpu = 0
        self.gpu = 0

    def tick_cpu(self, n: int):
        self.cpu += n

    def tick_gpu(self, n: int):
        self.gpu += n

    def should_sync(self) -> bool:
        return abs(self.cpu - self.gpu) > 10_000
""",

    "core/gpu_ir.py": """
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List

class GPUCmd(Enum):
    CLEAR = auto()
    DRAW = auto()
    SET_PIPELINE = auto()

@dataclass
class GPUInstr:
    cmd: GPUCmd
    args: Dict

class GPUCommandBuffer:
    def __init__(self):
        self.cmds: List[GPUInstr] = []

    def emit(self, instr: GPUInstr):
        self.cmds.append(instr)
""",

    "core/system.py": """
from .cpu import CPUState, MMU, IRInterpreter
from .optimizer import IROptimizer
from .cache import BlockCache, HotBlockProfiler
from .scheduler import Scheduler
from .gpu_ir import GPUCommandBuffer

class Dispatcher:
    def __init__(self, interp, opt, cache, profiler):
        self.interp = interp
        self.opt = opt
        self.cache = cache
        self.profiler = profiler

    def run(self, block):
        is_hot = self.profiler.record(block)
        if is_hot:
            block = self.opt.optimize(block)
            block = self.cache.get_or_add(block)
        self.interp.exec_block(block)

class AxionIRSystem:
    def __init__(self):
        self.mmu = MMU()
        self.cpu_state = CPUState()
        self.interp = IRInterpreter(self.cpu_state, self.mmu)
        self.optimizer = IROptimizer()
        self.cache = BlockCache()
        self.profiler = HotBlockProfiler()
        self.dispatcher = Dispatcher(
            self.interp, self.optimizer, self.cache, self.profiler
        )
        self.scheduler = Scheduler()
        self.gpu = GPUCommandBuffer()

    def run_block(self, block):
        self.dispatcher.run(block)
        self.scheduler.tick_cpu(len(block))
""",
}

def main():
    print("Re-populating AxionIR source tree...\n")

    for rel, content in FILES.items():
        path = os.path.join(BASE, rel)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content.lstrip("\n"))
        print(f"[WRITE] {rel}")

    print("\nAxionIR population complete.")

if __name__ == "__main__":
    main()
