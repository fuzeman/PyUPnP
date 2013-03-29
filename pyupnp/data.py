import urllib
import urlparse
import xml.etree.ElementTree as et
from pyupnp.util import absolute_url

__author__ = 'Dean Gardiner'


class ServiceDescription():
    def __init__(self, schema, type, version, xml_tree=None, baseUrl=None):
        self.schema = schema
        self.type = type
        self.version = version
        self.described = False

        self.serviceType = None
        self.serviceId = None
        self.controlURL = None
        self.eventSubURL = None
        self.SCPDURL = None

        self.update(xml_tree, baseUrl)

    def update(self, xml_tree, baseUrl):
        if xml_tree is not None and baseUrl is not None:
            self.serviceType = xml_tree.findtext('{urn:schemas-upnp-org:device-1-0}serviceType')
            self.serviceId = xml_tree.findtext('{urn:schemas-upnp-org:device-1-0}serviceId')

            self.controlURL = absolute_url(baseUrl, xml_tree.findtext('{urn:schemas-upnp-org:device-1-0}controlURL'))
            self.eventSubURL = absolute_url(baseUrl, xml_tree.findtext('{urn:schemas-upnp-org:device-1-0}eventSubURL'))
            self.SCPDURL = absolute_url(baseUrl, xml_tree.findtext('{urn:schemas-upnp-org:device-1-0}SCPDURL'))

            self.described = True


class DeviceDescription():
    def __init__(self, uuid, headers=None, found=False):
        self.uuid = uuid

        self.location = None
        self.server = None
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

        self.configID = 0

        self.services = {}  # { schema: { serviceType: { version: <Service> } } }

    def set_service(self, schema, type, version, xml_tree=None):
        schema = schema.replace('-', '.')
        if not schema in self.services:
            self.services[schema] = {}

        if not type in self.services[schema]:
            self.services[schema][type] = {}

        if not version in self.services[schema][type]:
            self.services[schema][type][version] = ServiceDescription(schema, type, version, xml_tree, baseUrl=self.getBaseUrl())
        else:
            self.services[schema][type][version].update(xml_tree, baseUrl=self.getBaseUrl())

    def get_service(self, path):
        path = path.replace('/', '\\')

        pathParts = path.split('\\')
        if len(pathParts) != 3:
            return None
        schema, type, version = pathParts

        if not schema in self.services:
            return None
        if not type in self.services[schema]:
            return None
        if not version in self.services[schema][type]:
            return None

        return self.services[schema][type][version]

    def getBaseUrl(self):
        if self.location:
            u = urlparse.urlparse(self.location)
            return u.scheme + '://' + u.netloc

    def load(self, callback=None, force=False):
        if self.described and not force:  # Already Described?
            return

        conn = urllib.urlopen(self.location)
        data = conn.read()
        conn.close()

        xml = None
        try:
            xml = et.fromstring(data)
        except et.ParseError:
            print "parse error"
            return

        xDevice = xml.find('{urn:schemas-upnp-org:device-1-0}device')

        if xDevice.findtext('{urn:schemas-upnp-org:device-1-0}UDN') != 'uuid:' + self.uuid:
            print "ERROR: UUID mismatch"
            return

        self.friendlyName = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}friendlyName')

        self.manufacturer = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}manufacturer')
        self.manufacturerURL = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}manufacturerURL')

        self.modelName = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}modelName')
        self.modelNumber = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}modelNumber')
        self.modelURL = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}modelURL')

        self.serialNumber = xDevice.findtext('{urn:schemas-upnp-org:device-1-0}serialNumber')

        self.described = True

        xServices = xDevice.find('{urn:schemas-upnp-org:device-1-0}serviceList')
        for service in xServices.iterfind('{urn:schemas-upnp-org:device-1-0}service'):
            serviceTypeUri = service.findtext('{urn:schemas-upnp-org:device-1-0}serviceType')

            _tmp = serviceTypeUri.index('urn:') + 4
            serviceSchema = serviceTypeUri[_tmp:serviceTypeUri.index(':', _tmp)].replace('-', '.')

            _tmp = serviceTypeUri.index('service:') + 8
            serviceType = serviceTypeUri[_tmp:serviceTypeUri.index(':', _tmp)]

            serviceVersion = serviceTypeUri[serviceTypeUri.index(':', _tmp) + 1:]

            self.set_service(serviceSchema, serviceType, serviceVersion, xml_tree=service)
            self.services[serviceSchema][serviceType][serviceVersion].described = True

    def __str__(self):
        return "(%s) [%s] [%s]" % (self.uuid, self.location, self.server)