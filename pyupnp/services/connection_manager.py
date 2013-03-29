from pyupnp.services import Service
from pyupnp.upnp import UPnP_Action, UPnP_StateVariable, UPnP_Argument, UPnP_Service


class ConnectionManagerService(Service):
    def __init__(self):
        Service.__init__(self)
        self.actions = {
            'GetProtocolInfo': UPnP_Action('GetProtocolInfo', {
                'Source':                       UPnP_Argument('Source',         'out', 'SourceProtocolInfo'),
                'Sink':                         UPnP_Argument('Sink',           'out', 'SinkProtocolInfo')
            }),
            'GetCurrentConnectionIDs': UPnP_Action('GetCurrentConnectionIDs', {
                'ConnectionIDs':                UPnP_Argument('ConnectionIDs',  'out', 'CurrentConnectionIDs')
            }),
            'GetCurrentConnectionInfo': UPnP_Action('GetCurrentConnectionInfo', {
                'ConnectionID':                 UPnP_Argument('ConnectionID',           'in',   'A_ARG_TYPE_ConnectionID'),
                'RcsID':                        UPnP_Argument('RcsID',                  'out',  'A_ARG_TYPE_RcsID'),
                'AVTransportID':                UPnP_Argument('AVTransportID',          'out',  'A_ARG_TYPE_AVTransportID'),
                'ProtocolInfo':                 UPnP_Argument('ProtocolInfo',           'out',  'A_ARG_TYPE_ProtocolInfo'),
                'PeerConnectionManager':        UPnP_Argument('PeerConnectionManager',  'out',  'A_ARG_TYPE_ConnectionManager'),
                'PeerConnectionID':             UPnP_Argument('PeerConnectionID',       'out',  'A_ARG_TYPE_ConnectionID'),
                'Direction':                    UPnP_Argument('Direction',              'out',  'A_ARG_TYPE_Direction'),
                'Status':                       UPnP_Argument('Status',                 'out',  'A_ARG_TYPE_ConnectionStatus'),
                }),
            }
        self.stateVariables = {
            'SourceProtocolInfo':               UPnP_StateVariable('SourceProtocolInfo',            'string',
                                                                   sendEvents=True),
            'SinkProtocolInfo':                 UPnP_StateVariable('SinkProtocolInfo',              'string',
                                                                   sendEvents=True),
            'CurrentConnectionIDs':             UPnP_StateVariable('CurrentConnectionIDs',          'string',
                                                                   sendEvents=True),
            'A_ARG_TYPE_ConnectionStatus':      UPnP_StateVariable('A_ARG_TYPE_ConnectionStatus',   'string', [
                'OK',
                'ContentFormatMismatch',
                'InsufficientBandwidth',
                'UnreliableChannel',
                'Unknown'
            ]),
            'A_ARG_TYPE_ConnectionManager':     UPnP_StateVariable('A_ARG_TYPE_ConnectionManager',  'string'),
            'A_ARG_TYPE_Direction':             UPnP_StateVariable('A_ARG_TYPE_Direction',          'string', [
                'Input', 'Output'
            ]),
            'A_ARG_TYPE_ProtocolInfo':          UPnP_StateVariable('A_ARG_TYPE_ProtocolInfo',       'string'),
            'A_ARG_TYPE_ConnectionID':          UPnP_StateVariable('A_ARG_TYPE_ConnectionID',       'i4'),
            'A_ARG_TYPE_AVTransportID':         UPnP_StateVariable('A_ARG_TYPE_AVTransportID',      'i4'),
            'A_ARG_TYPE_RcsID':                 UPnP_StateVariable('A_ARG_TYPE_RcsID',              'i4'),
            }
