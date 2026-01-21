from dataclasses import dataclass
from typing import List

from .ir import IRBlock, IRInstr, IROp


# -----------------------------
# Minimal ARM64 instruction model
# -----------------------------

@dataclass
class ARM64Instr:
    op: str
    rd: int
    rn: int | None = None
    imm: int | None = None


class ARM64Decoder:
    """
    Minimal ARM64 -> IR decoder.
    This is NOT a full decoder.
    It exists to prove the frontend pipeline.
    """

    def decode_block(self, instrs: List[ARM64Instr]) -> IRBlock:
        block = IRBlock("arm64_block")

        for ins in instrs:
            if ins.op == "MOVZ":
                block.emit(
                    IRInstr(
                        IROp.MOV,
                        dst=ins.rd,
                        imm=ins.imm,
                    )
                )

            elif ins.op == "ADD":
                block.emit(
                    IRInstr(
                        IROp.ADD,
                        dst=ins.rd,
                        src1=ins.rn,
                        src2=ins.imm,  # imm treated as register index later
                    )
                )

            elif ins.op == "SUB":
                block.emit(
                    IRInstr(
                        IROp.SUB,
                        dst=ins.rd,
                        src1=ins.rn,
                        src2=ins.imm,
                    )
                )

            else:
                raise NotImplementedError(f"Unsupported ARM64 op: {ins.op}")

        return block
