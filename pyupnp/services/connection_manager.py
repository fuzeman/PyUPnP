# PyUPnP - Simple Python UPnP device library built in Twisted
# Copyright (C) 2013  Dean Gardiner <gardiner91@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pyupnp.event import EventProperty
from pyupnp.services import Service, register_action,\
    ServiceActionArgument, ServiceStateVariable


class ConnectionManagerService(Service):
    version = (1, 0)
    serviceType = "urn:schemas-upnp-org:service:ConnectionManager:1"
    serviceId = "urn:upnp-org:serviceId:ConnectionManager"

    actions = {
        'GetProtocolInfo': [
            ServiceActionArgument('Source',                 'out',  'SourceProtocolInfo'),
            ServiceActionArgument('Sink',                   'out',  'SinkProtocolInfo'),
        ],
        'GetCurrentConnectionIDs': [
            ServiceActionArgument('ConnectionIDs',          'out',  'CurrentConnectionIDs'),
        ],
        'GetCurrentConnectionInfo': [
            ServiceActionArgument('ConnectionID',           'in',   'A_ARG_TYPE_ConnectionID'),

            ServiceActionArgument('RcsID',                  'out',  'A_ARG_TYPE_RcsID'),
            ServiceActionArgument('AVTransportID',          'out',  'A_ARG_TYPE_AVTransportID'),
            ServiceActionArgument('ProtocolInfo',           'out',  'A_ARG_TYPE_ProtocolInfo'),
            ServiceActionArgument('PeerConnectionManager',  'out',  'A_ARG_TYPE_ConnectionManager'),
            ServiceActionArgument('PeerConnectionID',       'out',  'A_ARG_TYPE_ConnectionID'),
            ServiceActionArgument('Direction',              'out',  'A_ARG_TYPE_Direction'),
            ServiceActionArgument('Status',                 'out',  'A_ARG_TYPE_ConnectionStatus'),
        ],
    }
    stateVariables = [
        # Arguments
        ServiceStateVariable('A_ARG_TYPE_ConnectionStatus',     'string', [
            'OK',
            'ContentFormatMismatch',
            'InsufficientBandwidth',
            'UnreliableChannel',
            'Unknown'
        ]),
        ServiceStateVariable('A_ARG_TYPE_ConnectionManager',    'string'),
        ServiceStateVariable('A_ARG_TYPE_Direction',            'string', [
            'Input', 'Output'
        ]),
        ServiceStateVariable('A_ARG_TYPE_ProtocolInfo',         'string'),
        ServiceStateVariable('A_ARG_TYPE_ConnectionID',         'i4'),
        ServiceStateVariable('A_ARG_TYPE_AVTransportID',        'i4'),
        ServiceStateVariable('A_ARG_TYPE_RcsID',                'i4'),

        # Variables
        ServiceStateVariable('SourceProtocolInfo',              'string',
                             sendEvents=True),
        ServiceStateVariable('SinkProtocolInfo',                'string',
                             sendEvents=True),
        ServiceStateVariable('CurrentConnectionIDs',            'string',
                             sendEvents=True),
    ]

    source_protocol_info = EventProperty('SourceProtocolInfo')
    sink_protocol_info = EventProperty('SinkProtocolInfo')
    current_connection_ids = EventProperty('CurrentConnectionIDs')

    @register_action('GetProtocolInfo')
    def getProtocolInfo(self):
        raise NotImplementedError()

    @register_action('GetCurrentConnectionIDs')
    def getCurrentConnectionIDs(self):
        raise NotImplementedError()

    @register_action('GetCurrentConnectionInfo')
    def getCurrentConnectionInfo(self, connectionID):
        raise NotImplementedError()
