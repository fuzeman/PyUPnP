import pprint
from random import Random
import socket
from threading import Semaphore
import time
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from pyupnp.data import DeviceDescription
from pyupnp.util import http_parse_raw, get_default_v4_address, parse_usn, header_exists, headers_join

__author__ = 'Dean Gardiner'

SSDP_ADDR_V4 = "239.255.255.250"
SSDP_ADDR_V6 = "[FF05::C]"
SSDP_PORT = 1900


class SSDP:
    def __init__(self, device):
        """SSDP Client/Listener

        :type device: Device
        """
        self.device = device

        if self.device.uuid is None:
            raise ValueError()

        self.targets = [
            'ssdp:all',
            'upnp:rootdevice',
            'uuid:' + self.device.uuid,
            self.device.deviceType
        ]
        for service in self.device.services:
            self.targets.append(service.serviceType)

        self.interfaces = [
            '',
            get_default_v4_address()
        ]

        _clients = []
        for interface in self.interfaces:
            _clients.append(SSDP_Client(self, interface))
        self.clients = SSDP_ClientsInterface(_clients)

        self.listener = SSDP_Listener(self, self.interfaces)

    def listen(self):
        print "[SSDP] listen()"
        self.clients.listen()
        self.listener.listen()

    def stop(self):
        print "[SSDP] stop()"
        self.clients.stop()
        self.listener.stop()


class SSDP_ClientsInterface:
    def __init__(self, clients):
        """Interface to control multiple `SSDP_Client` instances

        :type clients: list of SSDP_Client
        """
        self.clients = clients

    def listen(self):
        print "[SSDP_ClientsInterface] listen()"
        for client in self.clients:
            client.listen()

    def stop(self):
        print "[SSDP_ClientsInterface] stop()"
        for client in self.clients:
            client.stop()

    def respond(self, headers, (address, port)):
        for client in self.clients:
            client.respond(headers, (address, port))


class SSDP_Client(DatagramProtocol):
    def __init__(self, ssdp, interface):
        self.ssdp = ssdp
        self.interface = interface

        self.running = False

    def listen(self):
        if self.running:
            raise Exception()

        print "[SSDP_Client] listen()"
        self.listen_port = reactor.listenUDP(0, self, self.interface)
        self.running = True
        print "[SSDP_Client] listening on", self.listen_port.socket.getsockname()

    def stop(self):
        print "[SSDP_Client] stop()"
        if not self.running:
            return

        self.listen_port.stopListening()

    def respond(self, headers, (address, port)):
        print "[SSDP_Client] respond", address, port
        msg = 'HTTP/1.1 200 OK\r\n'
        msg += headers_join(headers)
        msg += '\r\n\r\n'

        try:
            self.transport.write(msg, (address, port))
        except socket.error, e:
            print "[SSDP_Client] socket.error:", e


class SSDP_Listener(DatagramProtocol):
    def __init__(self, ssdp, interfaces, responseExpire=900):
        self.ssdp = ssdp
        self.interfaces = interfaces
        self.responseExpire = responseExpire

        self.running = False
        self.rand = Random()

    def listen(self):
        if self.running:
            raise Exception()

        print "[SSDP_Listener] listen()"
        self.listen_port = reactor.listenMulticast(SSDP_PORT, self, listenMultiple=True)
        self.running = True

    def startProtocol(self):
        self.transport.setTTL(2)

        for interface in self.interfaces:
            self.transport.joinGroup(SSDP_ADDR_V4, interface)
            if interface == '':
                print "[SSDP_Listener] joined on ANY"
            else:
                print "[SSDP_Listener] joined on", interface

    def stop(self):
        print "[SSDP_Listener] stop()"

        if not self.running:
            return

        self.listen_port.stopListening()

    def datagramReceived(self, data, (address, port)):
        #print "[SSDP_Listener] datagramReceived", address, port

        method, path, version, headers = http_parse_raw(data)

        if method == 'M-SEARCH':
            self.received_MSEARCH(headers, (address, port))
        elif method == 'NOTIFY':
            self.received_NOTIFY(headers, (address, port))
        else:
            print "[SSDP_Listener] Unhandled Method '" + str(method) + "'"

    def received_MSEARCH(self, headers, (address, port)):
        print "[SSDP_Listener] received_MSEARCH"
        try:
            host = headers['host']
            man = str(headers['man']).strip('"')
            mx = int(headers['mx'])
            st = headers['st']
        except KeyError:
            print "[SSDP_Listener] ERROR: received message with missing headers"
            return
        except ValueError:
            print "[SSDP_Listener] ERROR: received message with invalid values"
            return

        if man != 'ssdp:discover':
            print "[SSDP_Listener] ERROR: received message where MAN != 'ssdp:discover'"
            return

        if st == 'ssdp:all':
            for target in self.ssdp.targets:
                reactor.callLater(self.rand.randint(1, mx),
                                  self.respond_MSEARCH, target, (address, port))
        elif st in self.ssdp.targets:
            reactor.callLater(self.rand.randint(1, mx),
                              self.respond_MSEARCH, st, (address, port))
        else:
            print "[SSDP_Listener] ignoring '" + str(st) + "'"

    def respond(self, headers, (address, port)):
        print "[SSDP_Listener] respond", address, port
        msg = 'HTTP/1.1 200 OK\r\n'
        msg += headers_join(headers)
        msg += '\r\n\r\n'

        try:
            self.transport.write(msg, (address, port))
        except socket.error, e:
            print "[SSDP_Listener] socket.error:", e

    def respond_MSEARCH(self, st, (address, port)):
        print "[SSDP_Listener] respond_MSEARCH"

        if self.ssdp.device.bootID is None:
            self.ssdp.device.bootID = int(time.time())

        if address == '127.0.0.1':
            location = self.ssdp.device.getLocation('127.0.0.1')
        else:
            location = self.ssdp.device.getLocation(get_default_v4_address())

        headers = {
            'CACHE-CONTROL': 'max-age = %d' % self.responseExpire,
            'EXT': '',
            'LOCATION': location,
            'SERVER': self.ssdp.device.server,
            'ST': st,
            'USN': 'uuid:' + self.ssdp.device.uuid + '::' + st,
            'BOOTID.UPNP.ORG': self.ssdp.device.bootID ,
            'CONFIGID.UPNP.ORG': self.ssdp.device.configID,
        }

        self.respond(headers, (address, port))

    def received_NOTIFY(self, headers, (address, port)):
        print "[SSDP_Listener] received_NOTIFY"

    # def sendNotify(self, nt, usn, description=None, nts='ssdp:alive', repeat=1,
    #                expire=1800, address=SSDP_ADDR_V4, port=SSDP_PORT):
    #     """
    #
    #     :type description: DeviceDescription
    #     """
    #     if description is None:
    #         if self.description is None:
    #             raise ValueError()
    #         else:
    #             description = self.description
    #
    #     if self.bootID is None:
    #         self.bootID = int(time.time())
    #
    #     headers = {
    #         'CACHE-CONTROL': 'max-age = %d' % expire,
    #         'LOCATION': description.location,
    #         'NT': nt,
    #         'NTS': nts,
    #         'SERVER': description.server,
    #         'USN': usn,
    #         'BOOTID.UPNP.ORG': self.bootID,
    #         'CONFIGID.UPNP.ORG': description.configID
    #     }
    #
    #     if self.port.socket.getsockname()[1] != 1900:
    #         headers['SEARCHPORT.UPNP.ORG'] = self.port.socket.getsockname()[1]
    #
    #     #pprint.pprint(headers)
    #
    #     self.sendRequest('NOTIFY', headers, repeat, address, port)
