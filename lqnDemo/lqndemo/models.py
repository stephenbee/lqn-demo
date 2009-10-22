from persistent.mapping import PersistentMapping
from interfaces import IlqnServer, IAccountContainer, ITransactionContainer, IAccount, ITransaction
from zope.interface import implements
from persistent.dict import PersistentDict
from repoze.bfg.security import Everyone, Allow, Deny, Authenticated
from security import users
from datetime import datetime


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

    def __init__(self):
        super(lqnServer,self).__init__()
        self.__acl__ = [
            (Allow, Authenticated, 'view'),
            (Deny, Everyone, 'view'),]





class Accounts(BaseContainer):

    def __init__ (self):
        super(Accounts,self).__init__()
        self.__parent__ = None
        self.__name__ = None
        self.counter=10001

    def addAccount(self,realname,password=''):
        id = str(self.counter)
        self.counter +=1
        account = Account(realname,password)
        self[id] = account
        return account

class Account(BaseContainer):

    def __init__ (self,realname,password=''):
        super(Account,self).__init__()
        self.__parent__ = None
        self.__name__ = None
        if not password:
            password='321'
        self.password=str(password)
        self.realname=realname
        self.__balance__ = 0;

    def balance(self):
        return self.__balance__

    def updateBalance(self):
        balance = 0
        for t in self.myTransactions():
            if t.source == self.__name__:
                balance -= t.amount
            else:
                balance += t.amount                    
        self.__balance__ = balance
        return self.balance()

    def _transactions(self):
        return self.__parent__.__parent__['transactions']

    def sort(self,transactions):
        tmp = [(t.date,t) for t in transactions]
        tmp.sort()
        return [t[1] for t in tmp]


    def myTransactions(self):
        out = []
        for t in self._transactions().values():
            if t.source == self.__name__ or t.target == self.__name__:
                out.append(t)     
        return self.sort(out)                

    def incoming(self):
        ts = []
        for t in self._transactions().values():
            if t.target == self.__name__:
                ts.append(t)
        return ts                
    
    def outgoing(self):
        ts = []
        for t in self._transactions().values():
            if t.source == self.__name__:
                ts.append(t)
        return ts                

    def transfer(self,target,amount):
        return self._transactions().addTransaction(self.__name__,target,amount)


class Transactions(BaseContainer):
    """ 
    Could test here or in Accounts
    >>> root = make_root()
    >>> accounts = root['accounts']
    >>> transactions = root['transactions']
    >>> jhb = accounts['10001']
    >>> stephen = accounts['10002']
    >>> fabio = accounts['10003']
    >>> t = transactions.addTransaction(jhb.__name__,stephen.__name__,1)
    >>> jhb.balance()
    -1
    >>> stephen.balance()
    1
    >>> t = jhb.transfer(fabio.__name__,23)
    >>> jhb.balance()
    -24
    >>> fabio.balance()
    23
    >>> ts = [t.amount for t in jhb.myTransactions()]
    >>> ts == [1,23]
    True
     
    
    """ 
    def __init__(self):
        super(Transactions,self).__init__()
        self.__parent__ = None
        self.__name__ = None
        self.counter=1001

    def addTransaction(self,source,target,amount):
        trans = Transaction(source,target,amount)
        id = str(self.counter)
        self.counter += 1
        self[id] = trans
        sac = self.__parent__['accounts'][source]
        tac = self.__parent__['accounts'][target]
        sac.updateBalance()
        tac.updateBalance()
        return trans

class Transaction(BaseContainer):

    def __init__ (self,source,target,amount):
        super(Transaction,self).__init__()
        self.__parent__ = None
        self.__name__ = None
        self.source = source
        self.target = target
        self.amount = amount
        self.date = datetime.now()


def make_root():
    """ 
    >>> root = make_root()
    >>> sorted(root['accounts'].keys())
    ['10001', '10002', '10003', '10004', '10005']
    >>> root['accounts']['10001'].password
    '123'
    """
    app_root = lqnServer()
    app_root['accounts'] = Accounts()
    for user,password in users:
        app_root['accounts'].addAccount(user,password)
    app_root['transactions'] = Transactions()
    return app_root


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        zodb_root['app_root'] = make_root()
        import transaction
        transaction.commit()
    return zodb_root['app_root']
