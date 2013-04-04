import uuid
import xml.etree.ElementTree as et
from twisted.internet import reactor
from pyupnp.event import EventSubscription
from pyupnp.lict import Lict
from pyupnp.logr import Logr
from pyupnp.util import make_element


class Service(object):
    version = (1, 0)
    serviceType = None
    serviceId = None

    actions = {}
    stateVariables = {}

    event_properties = None
    subscription_timeout_range = (1800, None)

    _description = None

    def __init__(self):
        self.__class__.stateVariables = Lict(self.__class__.stateVariables)

        for name, arguments in self.__class__.actions.items():
            self.__class__.actions[name] = Lict(arguments)

        # Build action function map
        self.actionFunctions = {}
        for attr in dir(self):
            obj = getattr(self, attr)
            if callable(obj) and hasattr(obj, 'actionName'):
                setattr(self, attr, ServiceActionWrapper(self, obj))
                self.actionFunctions[getattr(obj, 'actionName')] = obj

        self.subscriptions = Lict(searchNames='sid')
        if self.event_properties is None:
            self.event_properties = Lict(searchNames='name')

    def _generate_subscription_sid(self):
        result = None
        retries = 0
        while result is None and retries < 10:
            generated_uuid = str(uuid.uuid4())
            if generated_uuid not in self.subscriptions:
                result = generated_uuid
            else:
                retries += 1
        if result is None:
            raise Exception()
        return result

    def subscribe(self, callback, timeout):
        sid = 'uuid:' + self._generate_subscription_sid()

        if (self.subscription_timeout_range[0] is not None and
                timeout < self.subscription_timeout_range[0]):
            timeout = self.subscription_timeout_range[0]

        if (self.subscription_timeout_range[1] is not None and
                timeout > self.subscription_timeout_range[1]):
            timeout = self.subscription_timeout_range[1]

        subscription = EventSubscription(sid, callback, timeout)

        # Send initial event property notifications
        # TODO: calling this is 1 second isn't really a great way to do this
        reactor.callLater(1, subscription.notify, self.event_properties.values())

        self.subscriptions.append(subscription)

        return {
            'SID': sid,
            'TIMEOUT': 'Second-' + str(timeout)
        }

    def notify(self, prop):
        for sid in self.subscriptions.keys():
            subscription = self.subscriptions[sid]
            if subscription.expired:
                self.subscriptions.popvalue(sid)
            else:
                subscription.notify(prop)

    def dump(self):
        Logr.debug("xml tree dumped")
        scpd = et.Element('scpd', attrib={
            'xmlns': 'urn:schemas-upnp-org:service-1-0',
        })

        # specVersion
        specVersion = et.Element('specVersion')
        specVersion.append(make_element('major', str(self.version[0])))
        specVersion.append(make_element('minor', str(self.version[1])))
        scpd.append(specVersion)

        # actionList
        actionList = et.Element('actionList')
        for action_name, action_args in self.actions.items():
            action = et.Element('action')
            action.append(make_element('name', action_name))

            argumentList = et.Element('argumentList')
            for arg in action_args:
                argumentList.append(arg.dump())
            action.append(argumentList)

            actionList.append(action)
        scpd.append(actionList)

        # serviceStateTable
        serviceStateTable = et.Element('serviceStateTable')
        for stateVariable in self.stateVariables.values():
            serviceStateTable.append(stateVariable.dump())
        scpd.append(serviceStateTable)

        return scpd

    def dumps(self, force=False):
        if self.__class__._description is None or force:
            self.__class__._description = '<?xml version="1.0" encoding="utf-8"?>' + \
                                          et.tostring(self.dump())
        return self.__class__._description


def register_action(actionName):
    def decorate(func):
        func.actionName = actionName
        return func
    return decorate


class ServiceActionWrapper:
    def __init__(self, service, func):
        self.func = func
        self.name = self.func.actionName

        self.service = service

        # Get the action arguments from the service
        self.parameters = {}
        self.outputParameters = {}
        if self.name in self.service.actions:
            arguments = self.service.actions[self.name]

            # Set arguments 'parameterName' attribute from function spec
            self.func_params = self.func.func_code.co_varnames
            for x in xrange(1, len(self.func_params)):
                j = x - 1

                param = self.func_params[x]
                if j >= len(arguments):
                    raise TypeError()

                if arguments[j].direction != 'in':
                    raise TypeError()  # Invalid parameter in function

                if arguments[j].stateVariable not in self.service.stateVariables:
                    raise TypeError()  # Non-Existent state variable used

                arguments[j].parameterName = param
                self.parameters[arguments[j].name] = arguments[j]

            # Build output parameters dict
            for arg in arguments:
                if arg.direction == 'out':
                    self.outputParameters[arg.name] = arg
        else:
            raise NotImplementedError()

    def translate_kwargs(self, kwargs):
        translated_kwargs = {}

        for key, value in kwargs.items():
            if key in self.parameters:
                translated_kwargs[self.parameters[key].parameterName] = value
            elif key in self.func_params:
                translated_kwargs[key] = value
            else:
                raise NotImplementedError()

        return translated_kwargs

    def __call__(self, *args, **kwargs):
        result = self.func(*args, **self.translate_kwargs(kwargs))

        for key in self.outputParameters:
            if key not in result:
                raise TypeError()

        return result


class ServiceActionArgument:
    def __init__(self, name, direction, stateVariable):
        self.name = name
        self.direction = direction
        self.stateVariable = stateVariable
        self.parameterName = None

    def dump(self):
        argument = et.Element('argument')
        argument.append(make_element('name', self.name))
        argument.append(make_element('direction', self.direction))
        argument.append(make_element('relatedStateVariable', self.stateVariable))
        return argument


class ServiceStateVariable:
    def __init__(self, name, dataType, allowedValues=None, sendEvents=False):
        self.name = name
        self.dataType = dataType
        self.allowedValues = allowedValues
        self.sendEvents = sendEvents

    def dump(self):
        sendEventsStr = "no"
        if self.sendEvents:
            sendEventsStr = "yes"

        stateVariable = et.Element('stateVariable', sendEvents=sendEventsStr)

        stateVariable.append(make_element('name', self.name))
        stateVariable.append(make_element('dataType', self.dataType))

        if self.allowedValues:
            allowedValues = et.Element('allowedValueList')
            for value in self.allowedValues:
                allowedValues.append(make_element('allowedValue', value))
            stateVariable.append(allowedValues)

        return stateVariable