from core.ipc import IPCService, IPCMessage


class VIService(IPCService):
    """
    NS2 Video Interface (VI) service.
    System modules talk to this to get a framebuffer.
    """

    def __init__(self, framebuffer):
        self.fb = framebuffer

    def handle(self, msg: IPCMessage):
        cmd = msg.command_id

        # command 0: get framebuffer info
        if cmd == 0:
            msg.response = {
                "width": self.fb.width,
                "height": self.fb.height,
                "format": "RGBA8888",
            }
            return msg

        # command 1: test clear (debug only)
        if cmd == 1:
            self.fb.clear(30, 30, 40)
            return msg

        raise RuntimeError(f"Unknown VI command {cmd}")
