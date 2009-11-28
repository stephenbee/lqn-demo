from persistent.mapping import PersistentMapping
from interfaces import IlqnServer, IAccountContainer, ITransactionContainer, IAccount, ITransaction,IVoucher
from zope.interface import implements
from persistent.dict import PersistentDict
from repoze.bfg.security import Everyone, Allow, Deny, Authenticated
from security import users
from datetime import datetime
import md5,random,urllib,urllib2
import logging

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
        ret = super(BaseContainer,self).__setitem__(key, value)
        try: 
            self.data[key].__parent__ = self
            self.data[key].__name__ = key
        except: pass
        return ret
    
   
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

    @property
    def root(self):
        location = self
        while location.__class__ != lqnServer:
            location = location.__parent__
        return location            

class lqnServer(BaseContainer):    
    __parent__ = __name__ = None
    implements(IlqnServer)

    def __init__(self):
	logging.info("Initializing lqnServer...")
        super(lqnServer,self).__init__()
        self.__acl__ = [
            (Allow, Authenticated, 'view'),
            (Deny, Everyone, 'view'),]
	logging.info("Done.")





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
	logging.debug("Added account %s",realname)
        return account

class Account(BaseContainer):

    __startbalance__ = 200

    def __init__ (self,realname,password=''):
        super(Account,self).__init__()
        self.__parent__ = None
        self.__name__ = None
        if not password:
            password='321'
        self.password=str(password)
        self.realname=realname
        self.__balance__ = self.__startbalance__

    def balance(self):
        return self.__balance__

    def updateBalance(self):
        balance = self.__startbalance__
        for t in self.myTransactions():
            if t.source == self.__name__:
                balance -= t.amount
            if t.target == self.__name__:
                balance += t.amount                    
        self.__balance__ = balance
	logging.debug("Balance updated for account %s",self.realname)
        return self.balance()

    def _transactions(self):
        return self.root['transactions']


    def _vouchers(self):
        return self.root['vouchers']


    def myVouchers(self):
        out = []
        for v in self._vouchers().values():
            if v.source == self.__name__:
                out.append(v)     
        return self.sortOnDate(out)                

    def sortOnDate(self, objs):
        tmp = [(t.date,t) for t in objs]
        tmp.sort()
        tmp.reverse()
        return [t[1] for t in tmp]

    def myTransactions(self):
        out = []
        for t in self._transactions().values():
            if t.source == self.__name__ or t.target == self.__name__:
                out.append(t)     
        return self.sortOnDate(out)                


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

class InvalidTransaction(Exception):
    pass

class Transactions(BaseContainer):
    """ 
    Could test here or in Accounts
    >>> startbalance = Account.__startbalance__
    >>> root = make_root()
    >>> accounts = root['accounts']
    >>> transactions = root['transactions']
    >>> jhb = accounts['10001']
    >>> stephen = accounts['10002']
    >>> fabio = accounts['10003']
    >>> t = transactions.addTransaction(jhb.__name__,stephen.__name__,1)
    >>> jhb.balance() - startbalance
    -1
    >>> stephen.balance() - startbalance
    1
    >>> t = jhb.transfer(fabio.__name__,23)
    >>> jhb.balance() - startbalance
    -24
    >>> fabio.balance() - startbalance
    23
    >>> ts = [t.amount for t in jhb.myTransactions()]
    >>> ts == [23,1]
    True
    >>> t = jhb.transfer(jhb.__name__,1)
    >>> jhb.balance() - startbalance
    -24
    >>> t = jhb.transfer(fabio.__name__,2000)
    Traceback (most recent call last):
     ...
    Errors: {'amount': 'not enough funds'}
    
    """ 
    def __init__(self):
        super(Transactions,self).__init__()
        self.__parent__ = None
        self.__name__ = None
        self.counter=1001

    def isTransactionInvalid(self,source,target,amount):
        errors = {}
        accounts = self.root['accounts']
        if not accounts.has_key(source):
	    logging.error("Source account does not exist")
            errors['source'] = 'source account does not exist'
        if not accounts.has_key(target):
	    logging.error("Target account does not exist")
            errors['target'] = 'target account does not exist'
        try:
            amount = int(amount)
            if amount <= 0:
		logging.error("Amount needs to be larger than 0")
                errors['amount'] = 'amount needs to be larger than 0'
            elif (accounts[source].balance() - amount) < 0:
		logging.error("Not enough funds")
                errors['amount'] = 'not enough funds'
        except ValueError:
	    logging.error("IsTransactionInvalid: Not a number")
            errors['amount'] = 'not a number'
                   
        if errors:
            raise Errors(errors)
        else:
            return False

    def addTransaction(self,source,target,amount):
	logging.debug("Adding Transaction: %s %s %s", source,target,amount)
        self.isTransactionInvalid(source,target,amount)
        amount = int(amount)                    
        trans = Transaction(source,target,amount)
        id = str(self.counter)
        self.counter += 1
        self[id] = trans
        accounts = self.root['accounts']
        sac = accounts[source]
        tac = accounts[target]
        sac.updateBalance()
        tac.updateBalance()
	logging.debug("Transaction added")
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

class Vouchers(BaseContainer):

    def __init__ (self):
        super(Vouchers,self).__init__()
        self.__parent__ = None
        self.__name__ = None

    def addVoucher(self,source,amount,baseurl='http://localhost:6543'):
	logging.debug("Adding voucher...")
        errors = {}
        accounts = self.root['accounts']
        if not accounts.has_key(source):
	    logging.error("Account does not exist")
            errors['source'] = 'account does not exist'
        try:
            amount = int(amount)
            if amount <=0:
		logging.error("Amount needs to be at least 1")
                errors['amount'] = 'needs to be at least 1'
        except ValueError:
	    logging.error("addVoucher: not a number")
            errors['amount'] = 'not a number'

        if len(errors):
            raise Errors(errors)            
        voucher = Voucher(source,amount,baseurl)
        self[voucher.hash] = voucher 
	logging.debug("Voucher added")
        return voucher

class Errors(Exception):
    pass

class Voucher(BaseContainer):
    """
    >>> root = make_root()
    >>> voucher = root['vouchers'].addVoucher('10001',23)
    >>> voucher.used == None
    True
    >>> try:
    ...     voucher.use('10002',24)
    ... except Errors, e:
    ...     e.message ==  {'amount': 'amount is too high'}
    True
    >>> trans = voucher.use('10002',13)
    >>> trans.amount
    13
    >>> voucher.used == trans.__name__
    True
    >>> acc = root['accounts']['10001']
    >>> len(acc.myVouchers())
    1
    """
    implements(IVoucher)

    def __init__ (self,source,amount,baseurl='http://localhost:6543'):
        super(Voucher,self).__init__()
        self.__parent__ = None
        self.__name__ = None
        self.source = source
        self.amount = amount
        self.date = datetime.now()
        self.hash = md5.md5(str(random.random())).hexdigest()
        self.used = None #transaction id
        
        #http://code.google.com/intl/de/apis/chart/types.html
        width = 150
        height = 150
        path = '/vouchers/%s/r' % self.hash
        errorcorrection = 'H|0'
        redeemurl = baseurl+path
        self.redeemurl = redeemurl
        data = dict(cht='qr',
                    chl=redeemurl,
                    chld='H|0',
                    chs='%sx%s' % (width,height))
        qrurl = 'http://chart.apis.google.com/chart?%s' % urllib.urlencode(data)
        #print 'qrurl: %s' % qrurl
        try:
            opener = urllib2.urlopen(qrurl)
            if opener.headers['content-type'] != 'image/png':
                raise BadContentTypeException('Server responded with a content-type of %s' % opener.headers['content-type'])
        except urllib2.URLError:
            opener = open('lqndemo/templates/dummyqr.png')
        self.image=opener.read()

    def use(self,target,amount):
	logging.debug("Voucher::use Using voucher: %s %s" ,target,amount)
        accounts = self.__parent__.__parent__['accounts']
        sac = accounts[self.source]
        errors = {}
        if not accounts.has_key(target):
	    logging.error("Voucher::use Account does not exist")
            errors['target'] = 'account does not exist'
        try:
            amount = int(amount)
            if amount >= self.amount:
	    	logging.error("Voucher::use Amount is too high")
                errors['amount'] = 'amount is too high'
            elif amount < 0:
	    	logging.error("Voucher::use Amount needs to be at least 1")
                errors['amount'] = 'needs to be at least 1'

        except ValueError:
	    logging.error("Voucher::use Value error: Not a number")
            errors['amount'] = 'not a number'
           
        if errors:
            raise Errors(errors)

        trans = sac.transfer(target,amount)
        self.used = trans.__name__
	logging.debug("Voucher::use Voucher used")
        return trans


def make_root():
    """ 
    >>> root = make_root()
    >>> sorted(root['accounts'].keys())
    ['10001', '10002', '10003', '10004', '10005']
    >>> root['accounts']['10001'].password
    '123'
    """
    app_root = lqnServer()
    logging.debug("Setting up root app...")
    app_root['accounts'] = Accounts()
    logging.debug("Setting up accounts...")
    for user,password in users:
        app_root['accounts'].addAccount(user,password)
    logging.debug("Setting up transactions...")
    app_root['transactions'] = Transactions()
    logging.debug("Setting up vouchers...")
    app_root['vouchers'] = Vouchers()
    logging.debug("Root app set up.")
    return app_root


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        zodb_root['app_root'] = make_root()
        import transaction
        transaction.commit()
    return zodb_root['app_root']
