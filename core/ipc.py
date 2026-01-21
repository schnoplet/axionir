class IPCMessage:
    def __init__(self, command_id: int, data=None):
        self.command_id = command_id
        self.data = data or {}
        self.response = None


class IPCService:
    def handle(self, msg: IPCMessage):
        raise NotImplementedError
