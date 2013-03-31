from twisted.internet import reactor
from pyupnp.device import Device, DeviceIcon
from pyupnp.services import register_action
from pyupnp.services.connection_manager import ConnectionManagerService
from pyupnp.services.content_directory import ContentDirectoryService
from pyupnp.services.microsoft.media_receiver_registrar import MediaReceiverRegistrarService
from pyupnp.ssdp import SSDP
from pyupnp.upnp import UPnP


class MediaServerDevice(Device):
    deviceType = 'urn:schemas-upnp-org:device:MediaServer:1'

    def __init__(self):
        Device.__init__(self)

        self.uuid = '2fac1234-31f8-11b4-a222-08002b34c003'

        self.connectionManager = MSConnectionManager()
        self.contentDirectory = MSContentDirectory()
        self.mediaReceiverRegistrar = MSMediaReceiverRegistrar()

        self.services = [
            self.connectionManager,
            self.contentDirectory,
            self.mediaReceiverRegistrar
        ]

        self.icons = [
            DeviceIcon('image/png', 32, 32, 24,
                       'http://172.25.3.103:52323/MediaRenderer_32x32.png')
        ]

        self.namespaces['dlna'] = 'urn:schemas-dlna-org:device-1-0'
        self.extras['dlna:X_DLNADOC'] = 'DMS-1.50'


class MSConnectionManager(ConnectionManagerService):
    def __init__(self):
        ConnectionManagerService.__init__(self)


class MSContentDirectory(ContentDirectoryService):
    def __init__(self):
        ContentDirectoryService.__init__(self)


class MSMediaReceiverRegistrar(MediaReceiverRegistrarService):
    def __init__(self):
        MediaReceiverRegistrarService.__init__(self)

if __name__ == '__main__':
    device = MediaServerDevice()

    upnp = UPnP(device)
    ssdp = SSDP(device)

    upnp.listen()
    ssdp.listen()

    reactor.run()
