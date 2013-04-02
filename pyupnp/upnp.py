from twisted.internet import reactor
from twisted.web.error import UnsupportedMethod
from twisted.web.resource import Resource
from twisted.web.server import Site

__author__ = 'Dean Gardiner'


class UPnP(Resource):
    def __init__(self, device):
        """UPnP Control Server

        :type device: Device
        """
        Resource.__init__(self)

        self.device = device
        self.running = False

    def listen(self, interface=''):
        if self.running:
            raise Exception()

        print "[UPnP] listen()"
        self.site = Site(self)
        self.site_port = reactor.listenTCP(0, self.site, interface=interface)
        self.listen_address = self.site_port.socket.getsockname()[0]
        self.listen_port = self.site_port.socket.getsockname()[1]
        self.running = True

        self.device.location = "http://%s:" + str(self.listen_port)

        print "[UPnP] listening on", self.listen_address + ":" + str(self.listen_port)

    def stop(self):
        if not self.running:
            return

        print "[UPnP] stop()"
        self.site_port.stopListening()
        self.running = False

    def getChild(self, path, request):
        if path == '':
            return ServeResource(self.device.dumps(), 'application/xml')

        for service in self.device.services:
            if path == service.serviceId:
                return ServiceResource(service)

        print "[UPnP] unhandled request", path
        return Resource()


class ServiceResource(Resource):
    def __init__(self, service):
        Resource.__init__(self)
        self.service = service

    def render(self, request):
        request.setHeader('Content-Type', 'application/xml')
        return self.service.dumps()

    def getChild(self, path, request):
        if path == 'event':
            return ServiceEventResource(self.service)

        print "[UPnP][" + str(self.service.serviceType) + "] unhandled request", path
        return Resource()


class ServiceEventResource(Resource):
    def __init__(self, service):
        Resource.__init__(self)
        self.service = service

    def render(self, request):
        try:
            return Resource.render(self, request)
        except UnsupportedMethod, e:
            print "[UPnP][" + str(self.service.serviceType) + "] unhandled method",\
                request.method
            raise e

    def render_SUBSCRIBE(self, request):
        print "[UPnP][" + str(self.service.serviceType) + "][Event] SUBSCRIBE"
        print request.requestHeaders


class ServeResource(Resource):
    def __init__(self, data, mimetype):
        Resource.__init__(self)
        self.data = data
        self.mimetype = mimetype

    def render(self, request):
        request.setHeader('Content-Type', self.mimetype)
        return self.data
