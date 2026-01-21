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
