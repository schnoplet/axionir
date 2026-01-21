from core.ir import IRBlock, IRInstr, IROp
from core.optimizer import IROptimizer

def test_constant_folding():
    b = IRBlock()
    b.emit(IRInstr(IROp.MOV, dst=0, imm=2))
    b.emit(IRInstr(IROp.MOV, dst=1, imm=3))
    b.emit(IRInstr(IROp.ADD, dst=2, src1=0, src2=1))

    opt = IROptimizer()
    out = opt.optimize(b)
    assert out.instructions[-1].imm == 5\n