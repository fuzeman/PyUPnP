import urllib
import xml.etree.ElementTree as et

__author__ = 'Dean Gardiner'


class Service():
    def __init__(self, schema, type, version, xml_tree=None):
        self.schema = schema
        self.type = type
        self.version = version
        self.described = False

        self._serviceType = None
        self._serviceId = None
        self._controlURL = None
        self._eventSubURL = None
        self._SCPDURL = None

        self.update(xml_tree)

    def update(self, xml_tree):
        if xml_tree is not None:
            self._serviceType = xml_tree.findtext('{urn:schemas-upnp-org:device-1-0}serviceType')
            self._serviceId = xml_tree.findtext('{urn:schemas-upnp-org:device-1-0}serviceId')
            self._controlURL = xml_tree.findtext('{urn:schemas-upnp-org:device-1-0}controlURL')
            self._eventSubURL = xml_tree.findtext('{urn:schemas-upnp-org:device-1-0}eventSubURL')
            self._SCPDURL = xml_tree.findtext('{urn:schemas-upnp-org:device-1-0}SCPDURL')
            self.described = True


class Device():
    def __init__(self, uuid, headers=None, found=False):
        self.uuid = uuid
        if headers:
            self.location = headers['location']
            self.server = headers['server']

        self.friendlyName = None

        self.manufacturer = None
        self.manufacturerURL = None

        self.modelName = None
        self.modelNumber = None
        self.modelURL = None

        self.serialNumber = None

        self.found = found
        self.described = False

        self.services = {}  # { schema: { serviceType: { version: <Service> } } }

    def set_service(self, schema, type, version, xml_tree=None):
        schema = schema.replace('-', '.')
        if not schema in self.services:
            self.services[schema] = {}

        if not type in self.services[schema]:
            self.services[schema][type] = {}

        if not version in self.services[schema][type]:
            self.services[schema][type][version] = Service(schema, type, version, xml_tree)
        else:
            self.services[schema][type][version].update(xml_tree)

    def __str__(self):
        return "(%s) [%s] [%s]" % (self.uuid, self.location, self.server)


class UPnP():
    def __init__(self):
        pass

    @staticmethod
    def deviceDescription(device, callback=None, force=False):
        if device.described and not force:  # Already Described?
            return

        conn = urllib.urlopen(device.location)
        data = conn.read()
        conn.close()

        xml = None
        try:
            xml = et.fromstring(data)
        except et.ParseError:
            print "parse error"
            return

        xDevice = xml.find('{urn:schemas-upnp-org:device-1-0}device')

        if xDevice.findtext('{urn:schemas-upnp-org:device-1-0}UDN') != 'uuid:' + device.uuid:
            print "ERROR: UUID mismatch"
            return

        device.friendlyName = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}friendlyName')

        device.manufacturer = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}manufacturer')
        device.manufacturerURL = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}manufacturerURL')

        device.modelName = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}modelName')
        device.modelNumber = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}modelNumber')
        device.modelURL = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}modelURL')

        device.serialNumber = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}serialNumber')

        device.described = True

        xServices = xDevice.find('{urn:schemas-upnp-org:device-1-0}serviceList')
        for service in xServices.iterfind('{urn:schemas-upnp-org:device-1-0}service'):
            serviceTypeUri = service.findtext('{urn:schemas-upnp-org:device-1-0}serviceType')

            _tmp = serviceTypeUri.index('urn:') + 4
            serviceSchema = serviceTypeUri[_tmp:serviceTypeUri.index(':', _tmp)].replace('-', '.')

            _tmp = serviceTypeUri.index('service:') + 8
            serviceType = serviceTypeUri[_tmp:serviceTypeUri.index(':', _tmp)]

            serviceVersion = serviceTypeUri[serviceTypeUri.index(':', _tmp) + 1:]

            device.set_service(serviceSchema, serviceType, serviceVersion, xml_tree=service)
            device.services[serviceSchema][serviceType][serviceVersion].described = True