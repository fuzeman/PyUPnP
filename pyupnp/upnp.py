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
        return '\r\n'.join([
            '<?xml version="1.0"?>',
            '<root xmlns="urn:schemas-upnp-org:device-1-0" configId="%s">' % self.device.description.configID,
                '<specVersion>',
                    '<major>1</major>',
                    '<minor>0</minor>',
                '</specVersion>',
                '<device>',
                    '<deviceType>urn:schemas-upnp-org:device:MediaServer:1</deviceType>',
                    '<friendlyName>%s</friendlyName>' % self.device.description.friendlyName,

                    '<manufacturer>PyUPnP</manufacturer>',
                    '<manufacturerURL>http://github.com/fuzeman/PyUPnP</manufacturerURL>',

                    #'<modelDescription>PyUPnP</modelDescription>',
                    '<modelName>PyUPnP</modelName>',
                    #'<modelNumber>0.8a</modelNumber>',
                    #'<modelURL>http://github.com/fuzeman/PyUPnP</modelURL>',

                    #'<serialNumber></serialNumber>',
                    '<UDN>uuid:%s</UDN>' % self.device.description.uuid,
                    #'<UPC></UPC>',
                    '<iconList>',
                        '<icon>',
                            '<mimetype>image/png</mimetype>',
                            '<width>32</width>',
                            '<height>32</height>',
                            '<depth>24</depth>',
                            '<url>http://172.25.3.103:52323/MediaRenderer_32x32.png</url>',
                        '</icon>',
                    '</iconList>',
                    '<serviceList>',
                        '<service>'
                            '<serviceType>urn:schemas-upnp-org:service:ContentDirectory:1</serviceType>'
                            '<serviceId>urn:upnp-org:serviceId:ContentDirectory</serviceId>'
                            '<controlURL>/control</controlURL>'
                            '<eventSubURL>/event</eventSubURL>'
                            '<SCPDURL>/ContentDirectory.xml</SCPDURL>'
                        '</service>',
                        '<service>'
                            '<serviceType>urn:schemas-upnp-org:service:ConnectionManager:1</serviceType>'
                            '<serviceId>urn:upnp-org:serviceId:ConnectionManager</serviceId>'
                            '<controlURL>/control</controlURL>'
                            '<eventSubURL>/event</eventSubURL>'
                            '<SCPDURL>/ConnectionManager.xml</SCPDURL>'
                        '</service>'
                    '</serviceList>',
                '</device>',
            '</root>',
        ])


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


class UPnP_Argument:
    def __init__(self, name, direction, relatedStateVariable):
        self.name = name
        self.direction = direction
        self.relatedStateVariable = relatedStateVariable

    def dump(self):
        argument = et.Element('argument')
        argument.append(make_element('name', self.name))
        argument.append(make_element('direction', self.direction))
        argument.append(make_element('relatedStateVariable', self.relatedStateVariable))
        return argument


class UPnP_Action:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def dump(self):
        action = et.Element('action')
        action.append(make_element('name', self.name))

        argumentList = et.Element('argumentList')
        for argument in self.arguments.values():
            argumentList.append(argument.dump())
        action.append(argumentList)

        return action


class UPnP_StateVariable:
    def __init__(self, name, dataType, allowedValues=None, sendEvents=False):
        self.name = name
        self.dataType = dataType
        self.sendEvents = sendEvents
        self.allowedValues = allowedValues

    def dump(self):
        sendEventsStr = "no"
        if self.sendEvents:
            sendEventsStr = "yes"
        stateVariable = et.Element('stateVariable', sendEvents=sendEventsStr)

        stateVariable.append(make_element('name', self.name))
        stateVariable.append(make_element('dataType', self.dataType))

        if self.allowedValues:
            allowedValues = et.Element('allowedValues')
            for value in self.allowedValues:
                allowedValues.append(make_element('allowedValue', value))
            stateVariable.append(allowedValues)

        return stateVariable


class UPnP_Service:
    def __init__(self):
        self.majorVersion = 1
        self.minorVersion = 0
        self.actions = {}
        self.stateVariables = {}

    def dump(self):
        scpd = et.Element('scpd', attrib={
            'xmlns': 'urn:schemas-upnp-org:service-1-0',
        })

        specVersion = et.Element('specVersion')
        specVersion.append(make_element('major', str(self.majorVersion)))
        specVersion.append(make_element('minor', str(self.minorVersion)))
        scpd.append(specVersion)

        actionList = et.Element('actionList')
        for action in self.actions.values():
            actionList.append(action.dump())
        scpd.append(actionList)

        serviceStateTable = et.Element('serviceStateTable')
        for stateVariable in self.stateVariables.values():
            serviceStateTable.append(stateVariable.dump())
        scpd.append(serviceStateTable)

        return scpd

    def dumps(self):
        return '<?xml version="1.0" encoding="utf-8"?>' + et.tostring(self.dump())
