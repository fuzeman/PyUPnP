from pyupnp.device import Device, DeviceIcon
from pyupnp.services import register_action
from pyupnp.services.connection_manager import ConnectionManagerService
from pyupnp.services.content_directory import ContentDirectoryService


class MediaServerDevice(Device):
    deviceType = 'urn:schemas-upnp-org:device:MediaServer:1'

    def __init__(self):
        Device.__init__(self)

        self.uuid = '2fac1234-31f8-11b4-a222-08002b34c003'

        self.connectionManager = MSConnectionManager()
        self.contentDirectory = MSContentDirectory()

        self.services = [
            self.connectionManager,
            self.contentDirectory
        ]

        self.icons = [
            DeviceIcon('image/png', 32, 32, 24,
                       'http://172.25.3.103:52323/MediaRenderer_32x32.png')
        ]


class MSConnectionManager(ConnectionManagerService):
    def __init__(self):
        ConnectionManagerService.__init__(self)


class MSContentDirectory(ContentDirectoryService):
    def __init__(self):
        ContentDirectoryService.__init__(self)

if __name__ == '__main__':
    device = MediaServerDevice()