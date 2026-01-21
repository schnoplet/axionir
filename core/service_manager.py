from .ipc import IPCMessage


class ServiceManager:
    def __init__(self):
        self.services = {}

    def register(self, name: str, service):
        self.services[name] = service

    def get(self, name: str):
        return self.services.get(name)

    def dispatch(self, name: str, msg: IPCMessage):
        svc = self.services.get(name)
        if not svc:
            raise RuntimeError(f"Service not found: {name}")
        return svc.handle(msg)
