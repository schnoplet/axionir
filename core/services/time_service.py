from core.ipc import IPCService, IPCMessage
import time


class TimeService(IPCService):
    """
    Kernel time service.
    Real system software expects this to exist.
    """

    def handle(self, msg: IPCMessage):
        # command 0: get time in nanoseconds
        if msg.command_id == 0:
            msg.response = {
                "time_ns": int(time.time() * 1_000_000_000)
            }
            return msg

        raise RuntimeError(f"Unknown TimeService command {msg.command_id}")
