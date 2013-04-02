from pyupnp.services import Service, ServiceActionArgument, ServiceStateVariable, register_action


class MediaReceiverRegistrarService(Service):
    version = (1, 0)
    serviceType = "urn:microsoft.com:serviceId:X_MS_MediaReceiverRegistrar:1"
    serviceId = "urn:microsoft.com:serviceId:X_MS_MediaReceiverRegistrar"

    actions = {
        'IsAuthorized': [
            ServiceActionArgument('DeviceID',               'in',   'A_ARG_TYPE_DeviceID'),
            ServiceActionArgument('Result',                 'out',  'A_ARG_TYPE_Result'),
        ],
        'RegisterDevice': [
            ServiceActionArgument('RegistrationReqMsg',     'in',   'A_ARG_TYPE_RegistrationReqMsg'),
            ServiceActionArgument('RegistrationRespMsg',    'out',  'A_ARG_TYPE_RegistrationRespMsg'),
        ],
        'IsValidated': [
            ServiceActionArgument('DeviceID',               'in',   'A_ARG_TYPE_DeviceID'),
            ServiceActionArgument('Result',                 'out',  'A_ARG_TYPE_Result'),
        ],
    }
    stateVariables = [
        # Arguments
        ServiceStateVariable('A_ARG_TYPE_DeviceID',                 'string'),
        ServiceStateVariable('A_ARG_TYPE_Result',                   'int'),
        ServiceStateVariable('A_ARG_TYPE_RegistrationReqMsg',       'bin.base64'),
        ServiceStateVariable('A_ARG_TYPE_RegistrationRespMsg',      'bin.base64'),

        # Variables
        ServiceStateVariable('AuthorizationGrantedUpdateID',        'ui4',
                             sendEvents=True),
        ServiceStateVariable('AuthorizationDeniedUpdateID',         'ui4',
                             sendEvents=True),
        ServiceStateVariable('ValidationSucceededUpdateID',         'ui4',
                             sendEvents=True),
        ServiceStateVariable('ValidationRevokedUpdateID',           'ui4',
                             sendEvents=True),
    ]

    @register_action('IsAuthorized')
    def isAuthorized(self, device_id):
        raise NotImplementedError()

    @register_action('RegisterDevice')
    def registerDevice(self, request):
        raise NotImplementedError()

    @register_action('IsValidated')
    def isValidated(self, device_id):
        raise NotImplementedError()
