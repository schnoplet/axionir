from dataclasses import dataclass


@dataclass
class VSyncFence:
    signaled: bool = False


class NS2Display:
    """
    NS2-style display + vsync model.
    Fixed refresh, present fences, frame pacing.
    """

    def __init__(self, refresh_hz: int = 60):
        self.refresh_hz = refresh_hz
        self.cycles_per_frame = int(1_000_000 / refresh_hz)
        self._cycle_counter = 0
        self._pending_fence: VSyncFence | None = None

    def present(self) -> VSyncFence:
        """
        Submit a frame for presentation.
        CPU/GPU must wait for vsync fence.
        """
        fence = VSyncFence()
        self._pending_fence = fence
        self._cycle_counter = 0
        return fence

    def tick(self, cycles: int):
        if not self._pending_fence:
            return

        self._cycle_counter += cycles
        if self._cycle_counter >= self.cycles_per_frame:
            self._pending_fence.signaled = True
            self._pending_fence = None
