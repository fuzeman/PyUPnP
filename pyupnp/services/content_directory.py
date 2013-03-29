from pyupnp.services import Service
from pyupnp.upnp import UPnP_Service, UPnP_Action, UPnP_Argument, UPnP_StateVariable


class ContentDirectoryService(Service):
    def __init__(self):
        Service.__init__(self)
        self.actions = {
            'Browse': UPnP_Action('Browse', {
                'ObjectID':                     UPnP_Argument('ObjectID',           'in',   'A_ARG_TYPE_ObjectID'),
                'BrowseFlag':                   UPnP_Argument('BrowseFlag',         'in',   'A_ARG_TYPE_BrowseFlag'),
                'Filter':                       UPnP_Argument('Filter',             'in',   'A_ARG_TYPE_Filter'),
                'StartingIndex':                UPnP_Argument('StartingIndex',      'in',   'A_ARG_TYPE_Index'),
                'RequestedCount':               UPnP_Argument('RequestedCount',     'in',   'A_ARG_TYPE_Count'),
                'SortCriteria':                 UPnP_Argument('SortCriteria',       'in',   'A_ARG_TYPE_SortCriteria'),

                'Result':                       UPnP_Argument('Result',             'out',  'A_ARG_TYPE_Result'),
                'NumberReturned':               UPnP_Argument('NumberReturned',     'out',  'A_ARG_TYPE_Count'),
                'TotalMatches':                 UPnP_Argument('TotalMatches',       'out',  'A_ARG_TYPE_Count'),
                'UpdateID':                     UPnP_Argument('UpdateID',           'out',  'A_ARG_TYPE_UpdateID'),
                }),
            'GetSearchCapabilities': UPnP_Action('GetSearchCapabilities', {
                'SearchCaps':                   UPnP_Argument('SearchCaps',         'out',  'SearchCapabilities'),
                }),
            'GetSortCapabilities': UPnP_Action('GetSortCapabilities', {
                'SortCaps':                     UPnP_Argument('SortCaps',           'out',  'SortCapabilities'),
                }),
            'GetSystemUpdateID': UPnP_Action('GetSystemUpdateID', {
                'Id':                           UPnP_Argument('Id', 'out', 'SystemUpdateID'),
                }),
            'Search': UPnP_Action('Search', {
                'ContainerID':                  UPnP_Argument('ContainerID',        'in',   'A_ARG_TYPE_ObjectID'),
                'SearchCriteria':               UPnP_Argument('SearchCriteria',     'in',   'A_ARG_TYPE_SearchCriteria'),
                'Filter':                       UPnP_Argument('Filter',             'in',   'A_ARG_TYPE_Filter'),
                'StartingIndex':                UPnP_Argument('StartingIndex',      'in',   'A_ARG_TYPE_Index'),
                'RequestedCount':               UPnP_Argument('RequestedCount',     'in',   'A_ARG_TYPE_Count'),
                'SortCriteria':                 UPnP_Argument('SortCriteria',       'in',   'A_ARG_TYPE_SortCriteria'),

                'Result':                       UPnP_Argument('Result',             'out',  'A_ARG_TYPE_Result'),
                'NumberReturned':               UPnP_Argument('NumberReturned',     'out',  'A_ARG_TYPE_Count'),
                'TotalMatches':                 UPnP_Argument('TotalMatches',       'out',  'A_ARG_TYPE_Count'),
                'UpdateID':                     UPnP_Argument('UpdateID',           'out',  'A_ARG_TYPE_UpdateID'),
                }),
            'UpdateObject': UPnP_Action('UpdateObject', {
                'ObjectID':                     UPnP_Argument('ObjectID',           'in',   'A_ARG_TYPE_ObjectID'),
                'CurrentTagValue':              UPnP_Argument('CurrentTagValue',    'in',   'A_ARG_TYPE_TagValueList'),
                'NewTagValue':                  UPnP_Argument('NewTagValue',        'in',   'A_ARG_TYPE_TagValueList'),
                }),
            'X_GetRemoteSharingStatus': UPnP_Action('X_GetRemoteSharingStatus', {
                'Status':                       UPnP_Argument('Status',             'out',  'X_RemoteSharingEnabled'),
                }),
            }
        self.stateVariables = {
            'A_ARG_TYPE_ObjectID':              UPnP_StateVariable('A_ARG_TYPE_ObjectID',           'string'),
            'A_ARG_TYPE_Result':                UPnP_StateVariable('A_ARG_TYPE_Result',             'string'),
            'A_ARG_TYPE_SearchCriteria':        UPnP_StateVariable('A_ARG_TYPE_SearchCriteria',     'string'),
            'A_ARG_TYPE_BrowseFlag':            UPnP_StateVariable('A_ARG_TYPE_BrowseFlag',         'string', [
                'BrowseMetadata', 'BrowseDirectChildren'
            ]),
            'A_ARG_TYPE_Filter':                UPnP_StateVariable('A_ARG_TYPE_Filter',             'string'),
            'A_ARG_TYPE_SortCriteria':          UPnP_StateVariable('A_ARG_TYPE_SortCriteria',       'string'),
            'A_ARG_TYPE_Index':                 UPnP_StateVariable('A_ARG_TYPE_Index',              'ui4'),
            'A_ARG_TYPE_Count':                 UPnP_StateVariable('A_ARG_TYPE_Count',              'ui4'),
            'A_ARG_TYPE_UpdateID':              UPnP_StateVariable('A_ARG_TYPE_UpdateID',           'ui4'),
            'A_ARG_TYPE_TagValueList':          UPnP_StateVariable('A_ARG_TYPE_TagValueList',       'string'),
            'SearchCapabilities':               UPnP_StateVariable('SearchCapabilities',            'string'),
            'SortCapabilities':                 UPnP_StateVariable('SortCapabilities',              'string'),
            'SystemUpdateID':                   UPnP_StateVariable('SystemUpdateID',                'ui4',
                                                                   sendEvents=True),
            'ContainerUpdateIDs':               UPnP_StateVariable('ContainerUpdateIDs',            'string',
                                                                   sendEvents=True),
            'X_RemoteSharingEnabled':           UPnP_StateVariable('X_RemoteSharingEnabled',        'boolean',
                                                                   sendEvents=True),
            }
