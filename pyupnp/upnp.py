from SOAPpy import parseSOAPRPC, buildSOAP
import time
from twisted.internet import reactor
from twisted.web.error import UnsupportedMethod
from twisted.web.resource import Resource
from twisted.web.server import Site
from pyupnp.logr import Logr
from pyupnp.util import twisted_absolute_path

__author__ = 'Dean Gardiner'


def getHeader(request, name, required=True, default=None):
    result = request.requestHeaders.getRawHeaders(name)
    if len(result) != 1:
        if required:
            raise KeyError()
        else:
            return default
    return result[0]


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

        Logr.debug("listen()")
        self.site = Site(self)
        self.site_port = reactor.listenTCP(0, self.site, interface=interface)
        self.listen_address = self.site_port.socket.getsockname()[0]
        self.listen_port = self.site_port.socket.getsockname()[1]
        self.running = True

        self.device.location = "http://%s:" + str(self.listen_port)

        Logr.debug("listening on %s:%s", self.listen_address, self.listen_port)

    def stop(self):
        if not self.running:
            return

        Logr.debug("stop()")
        self.site_port.stopListening()
        self.running = False

    def getChild(self, path, request):
        # Hack to fix twisted not accepting absolute URIs
        path, request = twisted_absolute_path(path, request)

        if path == '':
            return ServeResource(self.device.dumps(), 'application/xml')

        for service in self.device.services:
            if path == service.serviceId:
                return ServiceResource(service)

        Logr.debug("unhandled request %s", path)
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

        if path == 'control':
            return ServiceControlResource(self.service)

        Logr.debug("(%s) unhandled request %s", self.service.serviceType, path)
        return Resource()


class ServiceControlResource(Resource):
    def __init__(self, service):
        Resource.__init__(self)
        self.service = service

    def render(self, request):
        try:
            return Resource.render(self, request)
        except UnsupportedMethod, e:
            Logr.debug("(%s) unhandled method %s",
                       self.service.serviceType, request.method)
            raise e

    def render_POST(self, request):
        data = request.content.getvalue()
        (r, header, body, attrs) = parseSOAPRPC(data, header=1, body=1, attrs=1)

        name = r._name
        kwargs = r._asdict()

        Logr.debug("(%s) %s", self.service.serviceType, name)

        if name not in self.service.actions or name not in self.service.actionFunctions:
            raise NotImplementedError()

        action = self.service.actions[name]
        func = self.service.actionFunctions[name]

        for argument in action:
            if argument.direction == 'in':
                if argument.name in kwargs:
                    value = kwargs[argument.name]
                    del kwargs[argument.name]
                    kwargs[argument.parameterName] = value
                else:
                    raise TypeError()

        result = func(**kwargs)

        return buildSOAP(kw={
            '%sResponse' % name: result
        })


class ServiceEventResource(Resource):
    def __init__(self, service):
        Resource.__init__(self)
        self.service = service

    def _parse_nt(self, value):
        if value != 'upnp:event':
            raise ValueError()
        return value

    def _parse_callback(self, value):
        # TODO: Support multiple callbacks as per UPnP 1.1
        if '<' not in value or '>' not in value:
            raise ValueError()
        return value[value.index('<') + 1:value.index('>')]

    def _parse_timeout(self, value):
        if not value.startswith('Second-'):
            raise ValueError()
        return int(value[7:])

    def render(self, request):
        try:
            return Resource.render(self, request)
        except UnsupportedMethod, e:
            Logr.debug("(%s) %s", self.service.serviceType, request.method)
            raise e

    def render_SUBSCRIBE(self, request):
        Logr.debug("(%s) SUBSCRIBE", self.service.serviceType)

        if request.requestHeaders.hasHeader('sid'):
            # Renew
            sid = getHeader(request, 'sid')
            if sid in self.service.subscriptions:
                self.service.subscriptions[sid].last_subscribe = time.time()
                self.service.subscriptions[sid].expired = False
                Logr.debug("(%s) Successfully renewed subscription",
                           self.service.serviceType)
            else:
                Logr.debug("(%s) Received invalid subscription renewal",
                           self.service.serviceType)
        else:
            # New Subscription
            nt = self._parse_nt(getHeader(request, 'nt'))
            callback = self._parse_callback(getHeader(request, 'callback'))
            timeout = self._parse_timeout(getHeader(request, 'timeout', False))

            Logr.debug("(%s) %s %s", self.service.serviceType, callback, timeout)

            responseHeaders = self.service.subscribe(callback, timeout)
            if responseHeaders is not None and type(responseHeaders) is dict:
                for name, value in responseHeaders.items():
                    request.setHeader(name, value)
                return ''
            else:
                Logr.debug("(%s) SUBSCRIBE FAILED", self.service.serviceType)

    def render_UNSUBSCRIBE(self, request):
        Logr.debug("(%s) UNSUBSCRIBE", self.service.serviceType)

        if request.requestHeaders.hasHeader('sid'):
            # Cancel
            sid = getHeader(request, 'sid')
            if sid in self.service.subscriptions:
                self.service.subscriptions[sid].expired = True
                Logr.debug("(%s) Successfully unsubscribed", self.service.serviceType)
            else:
                Logr.debug("(%s) Received invalid UNSUBSCRIBE request", self.service.serviceType)
        else:
            Logr.debug("(%s) Received invalid UNSUBSCRIBE request", self.service.serviceType)


class ServeResource(Resource):
    def __init__(self, data, mimetype):
        Resource.__init__(self)
        self.data = data
        self.mimetype = mimetype

    def render(self, request):
        request.setHeader('Content-Type', self.mimetype)
        return self.data
