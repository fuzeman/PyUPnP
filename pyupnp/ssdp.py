from threading import Semaphore, Event
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from pyupnp.upnp import Device
from pyupnp.util import http_parse_raw, get_default_v6_address, get_default_v4_address, parse_usn, header_exists

__author__ = 'Dean Gardiner'

SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900


class SSDP_Device(DatagramProtocol):
    _search_devices = {}
    _search_lock = Semaphore(3)
    _search_lock_value = 0
    _search_deviceFoundCallback = None
    _search_finishedCallback = None

    def __init__(self):
        self.stopCall = None

        self.devices = {}

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
               address=SSDP_ADDR, port=SSDP_PORT, timeout=1):
        address_v4 = get_default_v4_address()
        address_v6 = get_default_v6_address()

        ssdp_any = SSDP_Device.createListener('', cls._search_deviceFound,
                                              cls._search_stopped)

        ssdp_v4 = None
        if address_v4:
            ssdp_v4 = SSDP_Device.createListener(
                address_v4,
                cls._search_deviceFound,
                cls._search_stopped
            )

        ssdp_v6 = None
        if address_v6:
            ssdp_v6 = SSDP_Device.createListener(
                address_v6,
                cls._search_deviceFound,
                cls._search_stopped
            )

        search_params = {
            'mx': mx,
            'target': target,
            'repeat': repeat,

            'address': address,
            'port': port,
        }

        # Acquire looks before sending any search
        cls._search_lock.acquire()
        cls._search_lock_value = 1

        if ssdp_v4:
            cls._search_lock.acquire()
            cls._search_lock_value += 1
        if ssdp_v6:
            cls._search_lock.acquire()
            cls._search_lock_value += 1

        cls._search_deviceFoundCallback = staticmethod(foundDeviceCallback)
        cls._search_finishedCallback = staticmethod(finishedCallback)

        # Send search requests
        ssdp_any.sendSearch(**search_params)
        ssdp_any.stopTimeout(True, timeout)

        if ssdp_v4:
            ssdp_v4.sendSearch(**search_params)
            ssdp_v4.stopTimeout(True, timeout)

        if ssdp_v6:
            ssdp_v6.sendSearch(**search_params)
            ssdp_v6.stopTimeout(True, timeout)

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

    def sendRequest(self, method, headers, repeat=0,
                    address=SSDP_ADDR, port=SSDP_PORT):
        headers['HOST'] = '%s:%d' % (address, port)

        msg = '%s * HTTP/1.1\r\n' % method
        for hk, hv in headers.items():
            msg += str(hk) + ': ' + str(hv) + '\r\n'
        msg += '\r\n\r\n'

        for x in xrange(repeat + 1):
            self.transport.write(msg, (address, port))

    def sendSearch(self, mx=5, target='ssdp:all', repeat=1,
                    address=SSDP_ADDR, port=SSDP_PORT):
        self.sendRequest('M-SEARCH', {
            'MAN': '"ssdp:discover"',
            'MX': mx,
            'ST': target,
        }, repeat, address, port)

    def listen(self, address=''):
        self.port = reactor.listenUDP(0, self, address)
        self.running = True

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

        if respCode == 200:
            valid = True
            valid = valid and header_exists(headers, 'usn')
            valid = valid and header_exists(headers, 'location')
            valid = valid and header_exists(headers, 'server')

            if not valid:
                return

            # Parse USN
            uuid, root, schema, name, device_type, version = (None, None, None,
                                                              None, None, None)
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
                uuid, root, schema, name, device_type, version = parsedUsn

            if not self.devices.has_key(uuid):
                self.devices[uuid] = Device(uuid, headers=headers, found=True)
                self.foundDeviceCallback(self.devices[uuid])

            if not root and name == 'service':
                self.devices[uuid].set_service(schema, device_type, version)
