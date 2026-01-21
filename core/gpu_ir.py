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
