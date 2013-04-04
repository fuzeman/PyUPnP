# PyUPnP - Simple Python UPnP device library built in Twisted
# Copyright (C) 2013  fuzeman <gardiner91@gmail.com>

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
