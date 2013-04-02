import time
import requests
import xml.etree.ElementTree as et
from pyupnp.lict import Lict
from pyupnp.util import make_element


class EventProperty(object):
    def __init__(self, name, initial=None):
        self.name = name
        self.value = initial

        self.instance = None
        self.state_variable = None
        self.initialized = False

    def _instance_initialize(self, instance):
        if not hasattr(instance, 'stateVariables'):
            raise TypeError()

        if self.name not in instance.stateVariables:
            raise KeyError()

        if not instance.stateVariables[self.name].sendEvents:
            raise ValueError()

        self.instance = instance
        self.state_variable = instance.stateVariables[self.name]

        if self.instance.event_properties is None:
            self.instance.event_properties = Lict(searchNames='name')
        self.instance.event_properties.append(self)

        self.initialized = True

    def _default(self):
        if not self.initialized:
            raise Exception()

        if self.state_variable.dataType == 'string':
            return str()

        raise NotImplementedError()

    def __get__(self, instance, owner):
        if not self.initialized:
            self._instance_initialize(instance)

        if self.value is None:
            return self._default()
        return self.value

    def __set__(self, instance, value):
        if not self.initialized:
            self._instance_initialize(instance)

        if self.state_variable.dataType == 'string':
            value = str(value)
        else:
            raise NotImplementedError()

        self.value = value

        self.instance.notify(self)


class EventSubscription:
    def __init__(self, sid, callback, timeout):
        self.sid = sid
        self.callback = callback
        self.timeout = timeout

        self.last_subscribe = time.time()

        self.next_notify_key = 0

    def _increment_notify_key(self):
        if self.next_notify_key >= 4294967295:
            self.next_notify_key = 0
        else:
            self.next_notify_key += 1

    def notify(self, props):
        """

        :type prop: EventProperty
        """
        if type(props) is not list:
            props = [props]

        print "[EventSubscription] notify()", props



        headers = {
            'NT': 'upnp:event',
            'NTS': 'upnp:propchange',
            'SID': self.sid,
            'SEQ': self.next_notify_key
        }

        _propertyset = et.Element('e:propertyset', attrib={
            'xmlns:e': 'urn:schemas-upnp-org:event-1-0'
        })

        for prop in props:
            _property = et.Element('e:property')
            _property.append(make_element(prop.name, prop.value))
            _propertyset.append(_property)

        data = '<?xml version="1.0"?>' + et.tostring(_propertyset)

        requests.request('NOTIFY', self.callback,
                         headers=headers, data=data)
        self._increment_notify_key()