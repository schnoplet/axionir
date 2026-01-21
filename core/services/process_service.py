from core.ipc import IPCService, IPCMessage


class ProcessService(IPCService):
    """
    Minimal process info service.
    """

    def __init__(self, process):
        self.process = process

    def handle(self, msg: IPCMessage):
        # command 0: get pid
        if msg.command_id == 0:
            msg.response = {
                "pid": self.process.pid
            }
            return msg

        raise RuntimeError(f"Unknown ProcessService command {msg.command_id}")
