import xml.etree.ElementTree as et
import pyupnp
from pyupnp.logr import Logr
from pyupnp.util import make_element


class Device:
    version = (1, 0)

    # Description
    deviceType = None
    friendlyName = "PyUPnP Device"

    manufacturer = "PyUPnP"
    manufacturerURL = "http://github.com/fuzeman/PyUPnP"

    modelDescription = "PyUPnP"
    modelName = "PyUPnP"
    modelNumber = pyupnp.__version__
    modelURL = "http://github.com/fuzeman/PyUPnP"
    serialNumber = None
    UPC = None

    _description = None

    # SSDP
    server = "Microsoft-Windows/6.2 UPnP/1.0 PyUPnP/0.8a"

    def __init__(self):
        # Description
        self.configID = 0
        self.uuid = None

        # SSDP
        self.bootID = None
        self.location = None

        #: :type: list of UPnP_Service
        self.services = []

        #: :type: list of DeviceIcon
        self.icons = []

        self.namespaces = {
            '': 'urn:schemas-upnp-org:device-1-0'
        }

        self.extras = {}

    def getLocation(self, address):
        return self.location % address

    def get_UDN(self):
        if self.uuid is None:
            return None
        return 'uuid:%s' % self.uuid
    UDN = property(get_UDN)

    def dump(self):
        Logr.debug("xml tree dumped")
        root = et.Element('root', attrib={
            'configId': str(self.configID)
        })
        for prefix, namespace in self.namespaces.items():
            if prefix == '':
                prefix = 'xmlns'
            else:
                prefix = 'xmlns:' + prefix
            root.attrib[prefix] = namespace

        # specVersion
        specVersion = et.Element('specVersion')
        specVersion.append(make_element('major', str(self.version[0])))
        specVersion.append(make_element('minor', str(self.version[1])))
        root.append(specVersion)

        root.append(self.dump_device())
        return root

    def dump_device(self):
        device = et.Element('device')

        for attr_name in [
            'deviceType', 'friendlyName',
            'manufacturer', 'manufacturerURL',
            'modelDescription', 'modelName', 'modelNumber', 'modelURL', 'serialNumber',
            'UDN'
        ]:
            if hasattr(self, attr_name):
                val = getattr(self, attr_name)
                if val is not None:
                    device.append(make_element(attr_name, val))

        for name, val in self.extras.items():
            device.append(make_element(name, val))

        # iconList
        iconList = et.Element('iconList')
        for icon in self.icons:
            iconList.append(icon.dump())
        device.append(iconList)

        # serviceList
        serviceList = et.Element('serviceList')
        for service in self.services:
            _service = et.Element('service')
            _service.append(make_element('serviceType', service.serviceType))
            _service.append(make_element('serviceId', service.serviceId))
            _service.append(make_element('controlURL', '/' + service.serviceId + '/control'))
            _service.append(make_element('eventSubURL', '/' + service.serviceId + '/event'))
            _service.append(make_element('SCPDURL', '/' + service.serviceId))
            serviceList.append(_service)
        device.append(serviceList)

        return device

    def dumps(self, force=False):
        if self.__class__._description is None or force:
            self.__class__._description = '<?xml version="1.0"?>' + \
                                          et.tostring(self.dump())
        return self.__class__._description


class DeviceIcon:
    def __init__(self, mimetype, width, height, depth, url):
        self.mimetype = mimetype
        self.width = width
        self.height = height
        self.depth = depth
        self.url = url

    def dump(self):
        icon = et.Element('icon')
        icon.append(make_element('mimetype', self.mimetype))
        icon.append(make_element('width', str(self.width)))
        icon.append(make_element('height', str(self.height)))
        icon.append(make_element('depth', str(self.depth)))
        icon.append(make_element('url', self.url))
        return icon
