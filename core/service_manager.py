from core.ipc import IPCMessage
from core.services.unknown_service import UnknownService


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
            svc = UnknownService(name)
            self.services[name] = svc

        return svc.handle(msg)

    def list_services(self):
        return list(self.services.keys())
