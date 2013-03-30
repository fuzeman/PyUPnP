import sys
from twisted.internet import reactor
from pyupnp.ssdp import SSDP_Device
from pyupnp.util import get_default_v4_address

__author__ = 'Dean Gardiner'

PRINT_SERVICES = False

def search():
    devices = {}

    def foundDevice(device):
        print "foundDevice", device

    def gotDescription(device):
        print "gotDescription", device

    def finished(devices):
        print "finishedSearching"
        print

        for dk, dv in devices.items():
            print dv
            dv.load()  # Get Device Description
            print '\tLocation:', dv.location
            print '\tServer:', dv.server
            print
            print '\tDescribed:', dv.described
            if dv.described:
                print '\t\tFriendly Name:', dv.friendlyName
                print '\t\tManufacturer:', dv.manufacturer
                print '\t\tManufacturer URL:', dv.manufacturerURL
                print '\t\tmodelName:', dv.modelName
                print '\t\tmodelNumber:', dv.modelNumber
                print '\t\tmodelURL:', dv.modelURL
                print '\t\tserialNumber:', dv.serialNumber
            if PRINT_SERVICES:
                print
                for schema, types in dv.services.items():
                    print '\t', schema
                    for service_type, versions in types.items():
                        print '\t\t', service_type
                        for version, s in versions.items():
                            print '\t\t\t', version

                            print '\t\t\t\tDescribed:', s.described
                            if s.described:
                                print '\t\t\t\t\tService Type:', s.serviceType
                                print '\t\t\t\t\tService ID:', s.serviceId
                                print '\t\t\t\t\tControlURL:', s.controlURL
                                print '\t\t\t\t\tEventSubURL:', s.eventSubURL
                                print '\t\t\t\t\tSCPDURL:', s.SCPDURL
            print

    SSDP_Device.search(
        foundDeviceCallback=foundDevice,
        finishedCallback=finished
    )


def upnp_device():
    device = UPnP_Device('2fac1234-31f8-11b4-a222-08002b34c003')
    device.description.friendlyName = "PyUPnP (DG-VAIO)"
    device.description.configID = 3
    device.description.server = "Microsoft-Windows/6.2 UPnP/1.0 PyUPnP/0.8a"
    device.listen()

    #address_v4 = get_default_v4_address()
    #ssdp = SSDP_Device.createListener(address_v4)
    #ssdp.description = DeviceDescription('2fac1234-31f8-11b4-a222-08002b34c003')
    #ssdp.sendNotify('upnp:rootdevice', 'uuid:' + ssdp.description.uuid + '::upnp:rootdevice')
    #ssdp.sendNotify('upnp:rootdevice', 'uuid:' + ssdp.description.uuid + '::upnp:rootdevice')

if __name__ == '__main__':
    mode = 'search'
    if len(sys.argv) > 1:
        mode = sys.argv[1]

    if mode == 'upnp':
        upnp_device()
    else:
        search()

    reactor.run()