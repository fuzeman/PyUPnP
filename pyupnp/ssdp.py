import pprint
import socket
from threading import Semaphore
import time
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from pyupnp.data import DeviceDescription
from pyupnp.util import http_parse_raw, get_default_v4_address, parse_usn, header_exists

__author__ = 'Dean Gardiner'

SSDP_ADDR_V4 = "239.255.255.250"
SSDP_ADDR_V6 = "[FF05::C]"
SSDP_PORT = 1900


class SSDP_Device(DatagramProtocol):
    _search_devices = {}
    _search_lock = Semaphore(2)
    _search_lock_value = 0
    _search_deviceFoundCallback = None
    _search_finishedCallback = None

    def __init__(self, description=None):
        self.description = description

        self.stopCall = None

        self.devices = {}

        self.multicastListener = SSDP_MulticastListener(self)

        # Notify
        self.bootID = None

        # Callbacks
        self.foundDeviceCallback = None
        self.stoppedCallback = None

    #
    # Class Methods
    #

    @classmethod
    def createListener(cls, address='', foundDeviceCallback=None, stoppedCallback=None):
        ssdp = SSDP_Device()
        ssdp.foundDeviceCallback = foundDeviceCallback
        ssdp.stoppedCallback = stoppedCallback
        ssdp.listen(address)
        return ssdp

    @classmethod
    def search(cls, mx=1, target='ssdp:all', repeat=1,
               foundDeviceCallback=None, finishedCallback=None,
               timeout=1):
        """Search for SSDP devices/services


        """
        address_v4 = get_default_v4_address()

        ssdp_v4_any = SSDP_Device.createListener('', cls._search_deviceFound,
                                                 cls._search_stopped)

        ssdp_v4 = None
        if address_v4:
            ssdp_v4 = SSDP_Device.createListener(
                address_v4,
                cls._search_deviceFound,
                cls._search_stopped
            )

        search_params = {
            'mx': mx,
            'target': target,
            'repeat': repeat,

            'port': SSDP_PORT,
        }

        # Acquire looks before sending any search
        cls._search_lock.acquire()  # v4_any
        cls._search_lock_value = 1

        if ssdp_v4:
            cls._search_lock.acquire()
            cls._search_lock_value += 1

        cls._search_deviceFoundCallback = staticmethod(foundDeviceCallback)
        cls._search_finishedCallback = staticmethod(finishedCallback)

        # Send search requests
        ssdp_v4_any.sendSearch(address=SSDP_ADDR_V4, **search_params)
        ssdp_v4_any.stopTimeout(True, timeout)

        # Address-bound search requests
        if ssdp_v4:
            ssdp_v4.sendSearch(address=SSDP_ADDR_V4, **search_params)
            ssdp_v4.stopTimeout(True, timeout)

    @classmethod
    def _search_stopped(cls, devices):
        cls._search_lock_value -= 1

        if cls._search_lock_value == 0:
            devices = cls._search_devices
            callback = cls._search_finishedCallback

            cls._search_devices = {}
            cls._search_deviceFoundCallback = None
            cls._search_finishedCallback = None
            cls._search_lock_value = 0

            callback(devices)

        cls._search_lock.release()  # Release the ssdp search lock

    @classmethod
    def _search_deviceFound(cls, device):
        if device.uuid not in cls._search_devices:
            cls._search_devices[device.uuid] = device
            cls._search_deviceFoundCallback(device)

    #
    # Instance Methods
    #

    @staticmethod
    def _joinHeaders(headers):
        msg = ""
        for hk, hv in headers.items():
            msg += str(hk) + ': ' + str(hv) + '\r\n'
        return msg

    def sendRequest(self, method, headers, repeat=0,
                    address=SSDP_ADDR_V4, port=SSDP_PORT):
        headers['HOST'] = '%s:%d' % (address, port)

        msg = '%s * HTTP/1.1\r\n' % method
        msg += self._joinHeaders(headers)
        msg += '\r\n\r\n'

        for x in xrange(repeat + 1):
            self.transport.write(msg, (address, port))

    def sendResponse(self, headers, address, port, transport=None):
        if transport is None:
            transport = self.transport

        msg = 'HTTP/1.1 200 OK\r\n'
        msg += self._joinHeaders(headers)
        msg += '\r\n\r\n'

        try:
            self.transport.write(msg, (address, port))
        except socket.error, e:
            print e.message

    def sendSearch(self, mx=5, target='ssdp:all', repeat=1,
                   address=SSDP_ADDR_V4, port=SSDP_PORT):
        self.sendRequest('M-SEARCH', {
            'MAN': '"ssdp:discover"',
            'MX': mx,
            'ST': target,
        }, repeat, address, port)

    def sendSearchResponse(self, st, usn, address, port, description=None,
                           expire=1800, transport=None):
        """

        :type description: DeviceDescription
        """
        print "sendSearchResponse", st, usn, address, port

        if description is None:
            if self.description is None:
                raise ValueError()
            else:
                description = self.description

        if self.bootID is None:
            self.bootID = int(time.time())

        headers = {
            'CACHE-CONTROL': 'max-age = %s' % expire,
            'EXT': '',
            'LOCATION': description.location,
            'SERVER': description.server,
            'ST': st,
            'USN': usn,
            'BOOTID.UPNP.ORG': self.bootID,
            'CONFIGID.UPNP.ORG': description.configID
        }

        if self.port.socket.getsockname()[1] != 1900:
            headers['SEARCHPORT.UPNP.ORG'] = self.port.socket.getsockname()[1]

        self.sendResponse(headers, address, port, transport)

    def sendNotify(self, nt, usn, description=None, nts='ssdp:alive', repeat=1,
                   expire=1800, address=SSDP_ADDR_V4, port=SSDP_PORT):
        """

        :type description: DeviceDescription
        """
        if description is None:
            if self.description is None:
                raise ValueError()
            else:
                description = self.description

        if self.bootID is None:
            self.bootID = int(time.time())

        headers = {
            'CACHE-CONTROL': 'max-age = %d' % expire,
            'LOCATION': description.location,
            'NT': nt,
            'NTS': nts,
            'SERVER': description.server,
            'USN': usn,
            'BOOTID.UPNP.ORG': self.bootID,
            'CONFIGID.UPNP.ORG': description.configID
        }

        if self.port.socket.getsockname()[1] != 1900:
            headers['SEARCHPORT.UPNP.ORG'] = self.port.socket.getsockname()[1]

        #pprint.pprint(headers)

        self.sendRequest('NOTIFY', headers, repeat, address, port)

    def listen(self, address=''):
        self.port = reactor.listenUDP(0, self, address)
        self.running = True
        print "SSDP listening on", self.port.socket.getsockname()
        self.multicastListener.listen(address)

    def stop(self):
        if not self.running:
            return

        self.port.stopListening()
        self.running = False

        if self.stoppedCallback:
            self.stoppedCallback(self.devices)

    def stopTimeout(self, construct=False, timeout=10):
        if self.stopCall or construct:
            if self.stopCall:
                self.stopCall.cancel()
            self.stopCall = reactor.callLater(timeout, self.stop)

    def datagramReceived(self, data, (address, port)):
        self.stopTimeout()  # Reset stop timeout

        version, respCode, respText, headers = http_parse_raw(data)

        print address

        if respCode == 200:
            valid = True
            valid = valid and header_exists(headers, 'usn')
            valid = valid and header_exists(headers, 'location')
            valid = valid and header_exists(headers, 'server')

            if not valid:
                return

            # Parse USN
            uuid, root, schema, name, service_type, service_version = (
                None, None, None, None, None, None
            )
            parsedUsn = parse_usn(headers['usn'])
            if not parsedUsn:
                return
            if len(parsedUsn) == 1:
                if parsedUsn[0]:
                    uuid = parsedUsn[0]
                    root = True
                else:
                    return
            elif parsedUsn[1]:
                uuid, root = parsedUsn
            else:
                uuid, root, schema, name, service_type, service_version = parsedUsn

            if not self.devices.has_key(uuid):
                self.devices[uuid] = DeviceDescription(uuid, headers=headers, found=True)
                self.foundDeviceCallback(self.devices[uuid])

            if not root and name == 'service':
                self.devices[uuid].set_service(schema, service_type, service_version)
        else:
            print version, respCode, respText


class SSDP_MulticastListener(DatagramProtocol):
    def __init__(self, device):
        """

        :type device: SSDP_Device
        """
        self.device = device
        self.running = False

    def listen(self, address):
        self.address = address
        reactor.listenMulticast(SSDP_PORT, self, listenMultiple=True)
        self.running = True

    def startProtocol(self):
        self.transport.setTTL(5)

        if self.address == '':
            self.transport.joinGroup(SSDP_ADDR_V4)
        else:
            self.transport.joinGroup(SSDP_ADDR_V4, self.address)

        print "SSDP_MulticastListener listening on", self.address

    def datagramReceived(self, data, (address, port)):
        method, path, version, headers = http_parse_raw(data)

        print address, port, method, path, version

        if method == 'M-SEARCH':
            self.request_MSEARCH(headers, (address, port))
        elif method == 'NOTIFY':
            self.request_NOTIFY(headers, (address, port))

    def request_MSEARCH(self, headers, (address, port)):
        print headers['man'], headers['st'],
        if headers['st'] in ['upnp:rootdevice',
                             'urn:schemas-upnp-org:device:MediaServer:1',
                             'urn:schemas-upnp-org:service:ContentDirectory:1']:
            print "sent response"
            self.device.sendSearchResponse(
                headers['st'],
                'uuid:' + self.device.description.uuid + '::' + headers['st'],
                address, port, transport=self.transport
            )
        else:
            print "ignored"

    def request_NOTIFY(self, headers, (address, port)):
        pass