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
        ServiceStateVariable('SourceProtocolInfo',              'string',
                             sendEvents=True),
        ServiceStateVariable('SinkProtocolInfo',                'string',
                             sendEvents=True),
        ServiceStateVariable('CurrentConnectionIDs',            'string',
                             sendEvents=True),
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
    ]

    @register_action('GetProtocolInfo')
    def getProtocolInfo(self):
        return {
            'Source': None,
            'Sink': None
        }

    @register_action('GetCurrentConnectionIDs')
    def getCurrentConnectionIDs(self):
        return {
            'ConnectionIDs': None
        }

    @register_action('GetCurrentConnectionInfo')
    def getCurrentConnectionInfo(self, connectionID):
        return {
            'RcsID': None,
            'AVTransportID': None,
            'ProtocolInfo': None,
            'PeerConnectionManager': None,
            'PeerConnectionID': None,
            'Direction': None,
            'Status': None
        }
