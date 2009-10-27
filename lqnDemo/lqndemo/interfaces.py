from zope.interface import Interface
from zope.schema import TextLine, Text, List, Dict, Int, Choice

class IlqnServer(Interface):
    """A server for the lqn project"""
    pass

class IAccountContainer(Interface):
    """An account container"""
    __name__=TextLine(title=u'accounts')

    def addAccount(realname,password=''):
        """returns a new account object"""

class ITransactionContainer(Interface):
    """A transactions container"""
    __name__=TextLine(title=u'transactions')

    def addTransaction(sourceid,targetid,amount):
        """returns a new transaction object"""

class IAccount(Interface):
    __name__= TextLine(title=u'short_name/account number')
    password = TextLine(title=u'the password')
    realname = TextLine(title=u'the name of the account holder')

    def balance():
        """Returns an int with the current balance of the account"""

    def incoming():
        """Returns a list of transactions paying to this account"""

    def outgoing():
        """Returns a list of transactions going out from this account"""

    def make_transaction(targetid,amount):
        """Make a payment to the account specified by targetid, with 
           the given amount. Returns the transaction object"""


class ITransaction(Interface):
    __name__= TextLine(title=u'short_name')
    source = Int(title=u'id of sender')
    target = Int(title=u'id of target/recipient')
    amount = Int(title=u'amount in base units')
    date = Int(title=u'date in secs since epoch')

    def getSource():
        """returns source account object"""

    def getTarget():
        """returns target object"""


class IVoucher(Interface):
    pass

