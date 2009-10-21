from persistent.mapping import PersistentMapping
from interfaces import IlqnServer, IAccountContainer, ITransactionContainer, IAccount, ITransaction
from zope.interface import implements
from persistent.dict import PersistentDict
class MyModel(PersistentMapping):
    __parent__ = __name__ = None

class BaseContainer(PersistentMapping):
    """ Provides a basis for `container` objects
        >>> container = BaseContainer()
        >>> container[u'foo'] = u'bar'
        >>> container[u'foo']
        u'bar'
        >>> container.items()
        [(u'foo', u'bar')]
        >>> container.keys()
        [u'foo']
        >>> container.values()
        [u'bar']
        
    """
    def __init__(self):
        self.data = PersistentDict()
    
    def __getitem__(self, key):
        return self.data.__getitem__(key)
    
    def __setitem__(self, key, value):
        """ Acts as a proxy to the self.data PersistentDict. As it is a
            persistent object, it will also try and assign the __parent__
            attrubute to any object stored through this interface.
            
                >>> container = BaseContainer()
                >>> container.__setitem__('foo', 'bar')
                >>> 'foo' in container.data
                True
                >>> container['foo'].__parent__ # doctest: +ELLIPSIS
                Traceback (most recent call last):
                ...
                AttributeError: 'str' object has no attribute '__parent__'
                >>> class Child(object):
                ...     __parent__ = None
                ...
                >>> container.__setitem__('baz', Child())
                >>> 'baz' in container.data
                True
                >>> container['baz'].__parent__ == container
                True
        """
        ret = self.data.__setitem__(key, value)
        try: 
            self.data[key].__parent__ = self
            self.data[key].__name__ = key
        except: pass
        return ret
    
    def items(self):
        return self.data.items()
    
    def keys(self):
        return self.data.keys()
    
    def values(self):
        return self.data.values()
    
    def update(self, _data={}, **kwargs):
        """ BaseContainers can be updated much the same as any Python dictionary.
            
            By passing another mapping object:
            
                >>> container = BaseContainer()
                >>> container.update({'foo':'bar'})
            
            By passing a list of iterables with length 2:
            
                >>> container = BaseContainer()
                >>> container.update([('foo', 'bar'),])
            
            By passing a set of keyword arguments:
            
                >>> container = BaseContainer()
                >>> container.update(foo='bar')
            
        """
        if kwargs:
            for k,v in kwargs.items():
                self.__setitem__(k,v)
            return
        elif isinstance(_data, dict):
            for k,v in _data.items():
                self.__setitem__(k,v)
    
    def to_dict(self):
        data = {}
        for interface in providedBy(self):
            for key in getFields(interface).keys():
                data[key] = getattr(self, key)
        return data
    

class lqnServer(BaseContainer):    
    __parent__ = __name__ = None
    implements(IlqnServer)

class Accounts(BaseContainer):

    def __init__ (self):
        self.__parent__ = None
        self.__name__ = None

class Transactions(BaseContainer):
    
    def __init__(self):
        self.__parent__ = None
        self.__name__ = None

def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = lqnServer()
        app_root['accounts'] = Accounts()
        app_root['transactions'] = Transactions()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']
