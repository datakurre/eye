import collections
import inspect


PRIMITIVES = set([int, bool, str, unicode, type(None)])


class Node(object):

    def __init__(self, context):
        self.context = context
    
    def _dict(self):
        d = None
        
        type_ = type(self.context)
        if type_ in PRIMITIVES:
            d = {}
        elif type_.__name__.endswith('BTree'):
            # ZODB BTrees
            d = dict((str(k), v) for k, v in self.context.iteritems())
        elif isinstance(self.context, collections.Mapping):
            d = self.context
        elif isinstance(self.context, collections.Iterable):
            d = dict((str(i), v) for i, v in enumerate(self.context))
        elif hasattr(self.context, '__Broken_state__'):
            # ZODB
            if isinstance(self.context.__Broken_state__, collections.Mapping):
                d = self.context.__Broken_state__
            else:
                d = None
        
        if d is None:
            d = dict(inspect.getmembers(self.context))
        
        return dict((k, Node(v)) for k,v in d.iteritems())

    def __getitem__(self, name):
        return self._dict()[name]

    def items(self):
        return sorted(self._dict().items())
