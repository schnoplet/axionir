from core.ipc import IPCService, IPCMessage


class UnknownService(IPCService):
    def __init__(self, name: str):
        self.name = name

    def handle(self, msg: IPCMessage):
        print(
            f"[AxionIR][WARN] Unknown service '{self.name}' "
            f"command={msg.command_id}"
        )
        msg.response = {
            "result": -1
        }
        return msg
