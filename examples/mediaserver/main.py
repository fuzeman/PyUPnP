from pyupnp.device import Device
from pyupnp.services import register_action
# from pyupnp.services.connection_manager import ConnectionManagerService
from pyupnp.services.content_directory import ContentDirectoryService


class MediaServerDevice(Device):
    def __init__(self):
        Device.__init__(self)

        # self.connectionManager = MSConnectionManager()
        self.contentDirectory = MSContentDirectory()

        self.services = [
            # self.connectionManager,
            self.contentDirectory
        ]


# class MSConnectionManager(ConnectionManagerService):
#     def __init__(self):
#         ConnectionManagerService.__init__(self)


class MSContentDirectory(ContentDirectoryService):
    def __init__(self):
        ContentDirectoryService.__init__(self)

if __name__ == '__main__':
    device = MediaServerDevice()
