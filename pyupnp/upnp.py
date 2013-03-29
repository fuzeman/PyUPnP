from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site
from pyupnp.data import DeviceDescription
from pyupnp.ssdp import SSDP_Device
from pyupnp.util import get_default_v4_address, make_element
import xml.etree.ElementTree as et

__author__ = 'Dean Gardiner'


class UPnP_Device:
    def __init__(self, uuid):
        self.description = DeviceDescription(uuid)

        self.ssdp_any = SSDP_Device(self.description)
        self.ssdp_v4 = SSDP_Device(self.description)

    def listen(self, address=''):
        address_v4 = get_default_v4_address()
        if not address_v4:
            raise NotImplementedError()

        self.http_root = UPnP_HTTP(self)
        self.http_factory = Site(self.http_root)
        self.http_port = reactor.listenTCP(0, self.http_factory, interface=address_v4)
        self.description.location = 'http://' + ':'.join([
            self.http_port.socket.getsockname()[0], str(self.http_port.socket.getsockname()[1])
        ]) + '/device.xml'
        print "UPnP listening on", self.http_port.socket.getsockname()

        self.ssdp_any.listen()
        self.ssdp_any.sendNotify(
            'upnp:rootdevice',
            'uuid:' + self.description.uuid + '::upnp:rootdevice'
        )

        self.ssdp_v4.listen(address_v4)
        self.ssdp_v4.sendNotify(
            'upnp:rootdevice',
            'uuid:' + self.description.uuid + '::upnp:rootdevice'
        )

        self.running = True

    def stop(self):
        if not self.running:
            return

        self.http_port.stopListening()
        self.running = False


class UPnP_HTTP(Resource):
    def __init__(self, device):
        Resource.__init__(self)
        self.device = device

    def getChild(self, path, request):
        print "unhandled request", path
        return Resource()


class UPnP_HTTP_DeviceDescription(Resource):
    def __init__(self, device):
        """

        :type device: UPnP_Device
        """
        Resource.__init__(self)
        self.device = device

    def render(self, request):
        request.setHeader('Content-Type', 'application/xml')
        print "rendering \"device.xml\""
        return None


class UPnP_HTTP_ServiceDescription(Resource):
    def __init__(self, device, service):
        """

        :type device: UPnP_Device
        """
        Resource.__init__(self)
        self.device = device

        self.service = service
        self.data = self.service.dumps()

    def render(self, request):
        request.setHeader('Content-Type', 'application/xml')
        print "rendering \"%s\"" % request.path[1:]
        return self.data
