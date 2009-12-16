import unittest

from models import BaseContainer
from models import Errors, Accounts, Account, make_root

from repoze.bfg import testing

#class ViewTests(unittest.TestCase):
#    def disabled_test_my_view(self):
#        from lqndemo.views import my_view
#        context = testing.DummyModel()
#        request = testing.DummyRequest()
#        info = my_view(context, request)
#        self.assertEqual(info['project'], 'lqnDemo')

class ModelTests(unittest.TestCase):
    def basecontainer_test_setitem(self):
        container = BaseContainer()
        container.__setitem__('foo', 'bar')
        self.assertEqual(container.data['foo'],'bar')
        
    def basecontainer_test_todict(self):
        container = BaseContainer()
        container.__setitem__('foo','bar')
        data = container.to_dict()
        self.assertTrue(isinstance(data,dict))
        
    def basecontainer_test_update(self):
        container = BaseContainer()
        container.__setitem__('foo', 'bar')
        container.update({'foo':'barfoo'})
        self.assertEqual(container.data['foo'],'barfoo')
        container.update([('foo', 'foobar'),])
        self.assertEqual(container.data['foo'],'foobar')
        container.update(foo='barbar')
        self.assertEqual(container.data['foo'],'barbar')
        
    def accounts_test_addaccount(self):
        accounts = Accounts()
        account = accounts.addAccount("lqntest","katz")
        self.assertEqual(account.balance(),account.__startbalance__)
        self.assertEqual(account.realname, "lqntest")
        self.assertEqual(account.password, "katz")
    
    def accounts_test_update_account(self):
        root = make_root()
        accounts = root['accounts']
        transactions = root['transactions']
        amount = 10
    
        account_sender   = accounts.addAccount("lqntest","katz")
        account_receiver = accounts.addAccount("lqntestreceiver","test")
        sender_balance_before = account_sender.balance()
        receiver_balance_before = account_receiver.balance()
        t = account_sender.transfer(account_receiver.__name__,amount)
        #t = transactions.addTransaction(account_sender.__name__,account_receiver.__name__,amount)
        self.assertEqual(account_sender.balance(), sender_balance_before - amount)
        self.assertEqual(account_receiver.balance(), receiver_balance_before + amount)
        self.assertEqual(t.amount, amount)
        
        new_balance = account_sender.balance()
        account_sender.transfer(account_sender.__name__,amount)
        self.assertEqual(account_sender.balance(), new_balance )
        try:        
            account_sender.transfer(account_receiver.__name__, 20000)
            self.fail()
        except Errors:
            pass
            
        