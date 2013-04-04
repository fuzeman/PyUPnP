# PyUPnP - Simple Python UPnP device library built in Twisted
# Copyright (C) 2013  Dean Gardiner <gardiner91@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from threading import Thread
import time
from twisted.internet import reactor
from pyupnp.device import Device, DeviceIcon
from pyupnp.logr import Logr
from pyupnp.services import register_action
from pyupnp.services.connection_manager import ConnectionManagerService
from pyupnp.services.content_directory import ContentDirectoryService
from pyupnp.services.microsoft.media_receiver_registrar import MediaReceiverRegistrarService
from pyupnp.ssdp import SSDP
from pyupnp.upnp import UPnP


class MediaServerDevice(Device):
    deviceType = 'urn:schemas-upnp-org:device:MediaServer:1'

    friendlyName = "PyUPnP-MediaServer"

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

        self.source_protocol_info = 'http-get:*:*:*'
        self.current_connection_ids = '0'


class MSContentDirectory(ContentDirectoryService):
    def __init__(self):
        ContentDirectoryService.__init__(self)
        self.system_update_id = 0

    @register_action('X_GetRemoteSharingStatus')
    def getRemoteSharingStatus(self):
        return {
            'Status': 1
        }


class MSMediaReceiverRegistrar(MediaReceiverRegistrarService):
    def __init__(self):
        MediaReceiverRegistrarService.__init__(self)

    @register_action('IsAuthorized')
    def isAuthorized(self, device_id):
        return {
            'Result': 1
        }

    @register_action('RegisterDevice')
    def registerDevice(self, request):
        Logr.warning("RegisterDevice not implemented")
        return {
            'RegistrationRespMsg': None
        }

    @register_action('IsValidated')
    def isValidated(self, device_id):
        return {
            'Result': None
        }


class CommandThread(Thread):
    def __init__(self, device, upnp, ssdp):
        """

        :type device: Device
        :type upnp: UPnP
        :type ssdp: SSDP
        """
        Thread.__init__(self)
        self.device = device
        self.upnp = upnp
        self.ssdp = ssdp

        self.running = True

    def run(self):
        while self.running:
            try:
                command = 'command_' + raw_input('')

                if hasattr(self, command):
                    getattr(self, command)()
            except EOFError:
                self.command_stop()

    def command_stop(self):
        # Send 'byebye' NOTIFY
        self.ssdp.clients.sendall_NOTIFY(None, 'ssdp:byebye', True)

        # Stop everything
        self.upnp.stop()
        self.ssdp.stop()
        reactor.stop()
        self.running = False

if __name__ == '__main__':
    Logr.configure(logging.DEBUG)

    device = MediaServerDevice()

    upnp = UPnP(device)
    ssdp = SSDP(device)

    upnp.listen()
    ssdp.listen()

    def event_test():
        device.contentDirectory.system_update_id = time.time()
        reactor.callLater(5, event_test)

    event_test()

    r = CommandThread(device, upnp, ssdp)
    r.start()

    reactor.run()
