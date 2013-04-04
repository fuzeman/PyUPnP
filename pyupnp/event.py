import time
import requests
import xml.etree.ElementTree as et
from pyupnp.lict import Lict
from pyupnp.logr import Logr
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

        if self.value is None:
            self.value = self._default()

    def _default(self):
        if not self.initialized:
            raise Exception()

        if self.state_variable.dataType == 'string':
            return str()
        if self.state_variable.dataType == 'boolean':
            return False
        if self.state_variable.dataType == 'ui4':
            return 0

        Logr.warning(self.state_variable.dataType + "not implemented")
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
        elif self.state_variable.dataType == 'ui4':
            value = int(value)
        elif self.state_variable.dataType == 'boolean':
            value = bool(value)
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

        self.expired = False  # subscription has been flagged for deletion

    def _increment_notify_key(self):
        if self.next_notify_key >= 4294967295:
            self.next_notify_key = 0
        else:
            self.next_notify_key += 1

    def check_expiration(self):
        if self.expired is True:
            return True

        if time.time() > self.last_subscribe + self.timeout:
            self.expired = True
            return True

        return False

    def notify(self, props):
        """

        :type props: EventProperty or list of EventProperty
        """
        if type(props) is not list:
            props = [props]

        if self.expired:
            return

        if self.check_expiration():
            Logr.info("(%s) subscription expired", self.sid)
            return

        # noinspection PyTypeChecker
        Logr.debug("(%s) notify(), %d props: %s", self.sid, len(props), str(props))

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
            _property.append(make_element(prop.name, str(prop.value)))
            _propertyset.append(_property)

        data = '<?xml version="1.0"?>' + et.tostring(_propertyset)

        try:
            requests.request('NOTIFY', self.callback,
                             headers=headers, data=data)
        except requests.exceptions.ConnectionError:
            pass
        self._increment_notify_key()