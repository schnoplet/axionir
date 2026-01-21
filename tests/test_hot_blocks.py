from core.ir import IRBlock, IRInstr, IROp
from core.cache import HotBlockProfiler

def test_hot_block_detection():
    profiler = HotBlockProfiler(hot_threshold=3)
    b = IRBlock()
    b.emit(IRInstr(IROp.NOP))

    assert not profiler.record(b)
    assert not profiler.record(b)
    assert profiler.record(b)\n