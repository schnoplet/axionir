# AxionIR IR definitions
# Apache-2.0

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
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
    SVC = auto()   # <-- THIS WAS MISSING


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
            h.update(f"{i.op.name}:{i.dst}:{i.src1}:{i.src2}:{i.imm}".encode())
        return h.hexdigest()
