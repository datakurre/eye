import cgi
import collections
import inspect
import urlparse
from persistent.mapping import PersistentMapping


PRIMITIVES = set([int, bool, str, unicode, type(None)])


class Node(object):

    def __init__(self, context):
        self.context = context

    def _dict(self):
        d = None

        type_ = type(self.context)

        if type_ not in PRIMITIVES:
            for base in inspect.getmro(type_):
                if base.__module__.startswith("BTrees"):
                    type_ = base
                    break
                elif base.__module__.startswith("persistent"):
                    type_ = base
                    break

        if type_ in PRIMITIVES:
            d = {}
        elif (type_.__name__.endswith('BTree') or
              type_.__name__.endswith('TreeSet')):
            # ZODB BTrees
            d = self.context
            # d = {}
            # bucket = self.context._firstbucket
            # if bucket is None:
            #     return d
            # while True:
            #     d[bucket.minKey()] = bucket
            #     bucket = bucket._next
            #     if bucket is None:
            #         break
        elif type_.__name__.endswith('Bucket'):
            d = self.context
        elif (type_.__name__.startswith('BTrees.') and
              type_.__name__.endswith('Set')):
            d = dict(enumerate(self.context.keys()))
        elif (isinstance(self.context, collections.Mapping) or
              isinstance(self.context, PersistentMapping)):
            d = self.context
        elif isinstance(self.context, collections.Iterable):
            d = dict(enumerate(self.context))
        elif hasattr(self.context, '__Broken_state__'):
            # ZODB
            if isinstance(self.context.__Broken_state__, collections.Mapping):
                d = self.context.__Broken_state__
            else:
                d = None

        if d is None:
            d = {}
            # try:
            #     d = dict(inspect.getmembers(self.context))
            # except AttributeError:
            #     d = {}

        return _normalize(d)

    def __getitem__(self, name):
        d = self._dict()
        if name not in d:
            name = urlparse.unquote(name)
        if name not in d and isinstance(name, str):
            name = name.decode('utf-8')
        return d[name]

    def items(self):
        return sorted(self._dict().items())


def _normalize(d):
    d2 = {}

    # Wake up sleepy objects - a hack for ZODB objects in "ghost" state.
    wakeupcall = dir(d)
    del wakeupcall

    if hasattr(d, '__dict__'):
        for k, v in d.__dict__.iteritems():
            k = unicode(k).replace('/', '_')
            k = cgi.escape(k)
            if not (isinstance(d, PersistentMapping) and k == 'data'):
                d2[k] = Node(v)

    for k, v in d.iteritems():
        k = unicode(k).replace('/', '_')
        k = cgi.escape(k)
        d2[k] = Node(v)
    return d2
