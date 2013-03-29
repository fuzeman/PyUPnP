from pyupnp.device import Device
from pyupnp.services.connection_manager import ConnectionManagerService
from pyupnp.services.content_directory import ContentDirectoryService


class MediaServerDevice(Device):
    def __init__(self):
        Device.__init__(self)

        self.services = [
            MSConnectionManagerService(),
            MSContentDirectory()
        ]


class MSConnectionManagerService(ConnectionManagerService):
    pass


class MSContentDirectory(ContentDirectoryService):
    pass

if __name__ == '__main__':
    pass