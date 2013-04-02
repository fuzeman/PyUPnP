DEFAULT_SEARCH = ['key', 'name']


class Lict():
    def __init__(self, seq=None, priority=list, searchNames=None, searchOptimize=True):
        """Hybrid list-dict collection

        :type seq: object or list or dict
        :type priority: list or dict
        """
        if searchNames is None:
            searchNames = DEFAULT_SEARCH
        elif type(searchNames) is str:
            searchNames = [searchNames]

        if searchNames is tuple:
            searchNames = list(searchNames)

        self._searchNames = searchNames
        self._searchOptimize = searchOptimize

        self._priority = priority
        if self._priority is not list and self._priority is not dict:
            raise ValueError()

        #: :type: list
        self._col_list = None

        #: :type: dict
        self._col_dict = None

        if seq is None:
            seq = []
        self.extend(seq)

    def _get_object_key(self, p_object):
        """Get key from object"""
        matched_key = None
        matched_index = None

        if hasattr(p_object, self._searchNames[0]):
            return getattr(p_object, self._searchNames[0])

        for x in xrange(len(self._searchNames)):
            key = self._searchNames[x]
            if hasattr(p_object, key):
                matched_key = key
                matched_index = x

        if matched_key is None:
            raise KeyError()

        if matched_index != 0 and self._searchOptimize:
            self._searchNames.insert(0, self._searchNames.pop(matched_index))

        return getattr(p_object, matched_key)

    def _sync_list_to_dict(self, items=None):
        if self._col_dict is None:
            self._col_dict = {}

        for item in items:
            key = self._get_object_key(item)

            if key in self._col_dict:
                raise KeyError()

            self._col_dict[key] = item

    def __getitem__(self, y):
        if self._priority is list:
            if type(y) is int and y < len(self._col_list):
                return self._col_list[y]

            if y in self._col_dict:
                return self._col_dict[y]

            raise KeyError()
        elif self._priority is dict:
            if y in self._col_dict:
                return self._col_dict[y]

            if type(y) is int and y < len(self._col_list):
                return self._col_list[y]

            raise KeyError()

        raise NotImplementedError()

    def _set_index(self, index, value):
        del self._col_dict[self._get_object_key(self._col_list[index])]
        self._col_list[index] = value
        self._sync_list_to_dict([value])

    def _set_key(self, key, value):
        if key != self._get_object_key(value):
            raise ValueError()

        if key in self._col_dict:
            x = self._col_list.index(self._col_dict[key])
            self._col_dict[key] = value
            self._col_list[x] = value
        else:
            self.append(value)

    def __setitem__(self, y, value):
        if self._priority is list:
            if type(y) is int and y < len(self._col_list):
                self._set_index(y, value)
            elif y in self._col_dict:
                self._set_key(y, value)
            else:
                raise KeyError()
        elif self._priority is dict:
            if y in self._col_dict:
                self._set_key(y, value)
            elif type(y) is int and y < len(self._col_list):
                self._set_index(y, value)
            else:
                raise KeyError()
        else:
            raise NotImplementedError()

    def __delitem__(self, y):
        if self._priority is list:
            if type(y) is int and y < len(self._col_list):
                self.pop(y)
            elif y in self._col_dict:
                self.popvalue(y)
            else:
                raise KeyError()
        elif self._priority is dict:
            if y in self._col_dict:
                self.popvalue(y)
            elif type(y) is int and y < len(self._col_list):
                self.pop(y)
            else:
                raise KeyError()
        else:
            raise NotImplementedError()

    def __repr__(self):
        if self._priority is dict:
            return repr(self._col_dict)
        elif self._priority is list:
            return repr(self._col_list)
        raise NotImplementedError()

    def __str__(self):
        if self._priority is dict:
            return str(self._col_dict)
        elif self._priority is list:
            return str(self._col_list)
        raise NotImplementedError()

    #
    # list
    #

    def append(self, p_object):
        """ L.append(object) -- append object to end """
        self.insert(len(self._col_list), p_object)

    def count(self, value):
        """ L.count(value) -> integer -- return number of occurrences of value """
        return self._col_list.count(value)

    def extend(self, collection):
        """ L.extend(iterable) -- extend list by appending elements from the iterable """
        if type(collection) is list:
            if self._col_dict is None and self._col_list is None:
                self._col_list = collection
            else:
                self._col_list += collection
            self._sync_list_to_dict(collection)
        elif type(collection) is dict:
            if self._col_dict is None and self._col_list is None:
                self._col_dict = collection
                self._col_list = collection.values()
            else:
                for key, value in collection.items():
                    self._set_key(key, value)
        else:
            raise NotImplementedError()

    def index(self, value, start=None, stop=None):
        """
        L.index(value, [start, [stop]]) -> integer -- return first index of value.
        Raises ValueError if the value is not present.
        """
        return self._col_list.index(value, start, stop)

    def insert(self, index, p_object):
        """ L.insert(index, object) -- insert object before index """
        key = self._get_object_key(p_object)
        if key in self._col_dict:
            raise KeyError()
        self._col_list.insert(index, p_object)
        self._col_dict[key] = p_object

    def pop(self, index=None):
        """
        L.pop([index]) -> item -- remove and return item at index (default last).
        Raises IndexError if list is empty or index is out of range.
        """
        if index is None:
            index = len(self._col_list) - 1

        key = self._get_object_key(self._col_list[index])
        del self._col_dict[key]

        return self._col_list.pop(index)

    def remove(self, value):
        """
        L.remove(value) -- remove first occurrence of value.
        Raises ValueError if the value is not present.
        """
        self._col_list.remove(value)
        self._col_dict.pop(self._get_object_key(value))

    def reverse(self):
        """ L.reverse() -- reverse *IN PLACE* """
        self._col_list.reverse()

    def sort(self, cmp=None, key=None, reverse=False):
        """
        L.sort(cmp=None, key=None, reverse=False) -- stable sort *IN PLACE*;
        cmp(x, y) -> -1, 0, 1
        """
        self._col_list.sort()

    def __iter__(self):
        return iter(self._col_list)

    def __len__(self):
        return len(self._col_list)

    #
    # dict
    #

    def clear(self):
        """ D.clear() -> None.  Remove all items from D. """
        self._col_dict.clear()
        self._col_list = []

    def copy(self):
        """ D.copy() -> a shallow copy of D """
        return self._col_dict.copy()

    def get(self, k, d=None):
        """ D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None. """
        return self._col_dict.get(k, d)

    def has_key(self, k):
        """ D.has_key(k) -> True if D has a key k, else False """
        return k in self._col_dict

    def items(self):
        """ D.items() -> list of D's (key, value) pairs, as 2-tuples """
        return self._col_dict.items()

    def iteritems(self):
        """ D.iteritems() -> an iterator over the (key, value) items of D """
        return self._col_dict.iteritems()

    def iterkeys(self):
        """ D.iterkeys() -> an iterator over the keys of D """
        return self._col_dict.iterkeys()

    def itervalues(self):
        """ D.itervalues() -> an iterator over the values of D """
        return self._col_dict.itervalues()

    def keys(self):
        """ D.keys() -> list of D's keys """
        return self._col_dict.keys()

    def popvalue(self, k, d=None):
        """
        D.popvalue(k[,d]) -> v, remove specified key and return the corresponding value.
        If key is not found, d is returned if given, otherwise KeyError is raised
        """
        if k not in self._col_dict:
            return d
        value = self._col_dict.pop(k)
        self._col_list.remove(value)
        return value

    def popitem(self):
        """
        D.popitem() -> (k, v), remove and return some (key, value) pair as a
        2-tuple; but raise KeyError if D is empty.
        """
        key, value = self._col_dict.popitem()
        if value is not None:
            self._col_list.remove(value)
        return key, value

    def setdefault(self, k, d=None):
        """ D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D """
        if k not in self._col_dict:
            self._set_key(k, d)
        return self._col_dict.get(k)

    def update(self, E=None, **F):
        """
        D.update([E, ]**F) -> None.  Update D from dict/iterable E and F.
        If E present and has a .keys() method, does:     for k in E: D[k] = E[k]
        If E present and lacks .keys() method, does:     for (k, v) in E: D[k] = v
        In either case, this is followed by: for k in F: D[k] = F[k]
        """
        if hasattr(E, 'keys'):
            self.extend(E)
        else:
            for key, value in E:
                self._set_key(key, value)
        self.extend(F)

    def values(self):
        """ D.values() -> list of D's values """
        return self._col_dict.values()

    def viewitems(self):
        """ D.viewitems() -> a set-like object providing a view on D's items """
        return self._col_dict.viewitems()

    def viewkeys(self):
        """ D.viewkeys() -> a set-like object providing a view on D's keys """
        return self._col_dict.viewkeys()

    def viewvalues(self):
        """ D.viewvalues() -> an object providing a view on D's values """
        return self._col_dict.viewvalues()


class LictTest():
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

if __name__ == '__main__':
    import timeit

    number = 10000
    repeat = 10
    print_digits = 4

    def print_result(result):
        print str(round(result, print_digits)) + u"\u00B5s"

    # ----------------------------------
    #  append
    # ----------------------------------

    print '----- append -----'

    lict_append_result = (sum(timeit.repeat("""
col.append(LictTest(name=str(uuid.uuid4())))
""", """
import uuid
from lict import Lict, LictTest
col = Lict()
    """, repeat=repeat, number=number)) / repeat / number) * 1000 * 1000
    print 'lict',
    print_result(lict_append_result)

    list_append_result = (sum(timeit.repeat("""
col.append(LictTest(name=str(uuid.uuid4())))
""", """
import uuid
from lict import LictTest
col = []
    """, repeat=repeat, number=number)) / repeat / number) * 1000 * 1000
    print 'list',
    print_result(list_append_result)

    print '====', str(round(lict_append_result - list_append_result, print_digits)) + u"\u00B5s",\
        '(' + str(round(((lict_append_result / list_append_result) - 1) * 100, 2)) + '%)',\
        'slower than list'

    # ----------------------------------
    #  remove
    # ----------------------------------

    print '------- pop ------'

    lict_append_result = (sum(timeit.repeat("""
col.pop()
""", """
import uuid
from lict import Lict, LictTest
col = Lict()
for x in range(""" + str(number) + """):
    col.append(LictTest(name=str(uuid.uuid4())))
    """, repeat=repeat, number=number)) / repeat / number) * 1000 * 1000
    print 'lict',
    print_result(lict_append_result)

    list_append_result = (sum(timeit.repeat("""
col.pop()
""", """
import uuid
from lict import LictTest
col = []
for x in range(""" + str(number) + """):
    col.append(LictTest(name=str(uuid.uuid4())))
    """, repeat=repeat, number=number)) / repeat / number) * 1000 * 1000
    print 'list',
    print_result(list_append_result)

    print '====', str(round(lict_append_result - list_append_result, print_digits)) + u"\u00B5s", \
        '(' + str(round(((lict_append_result / list_append_result) - 1) * 100, 2)) + '%)', \
        'slower than list'
