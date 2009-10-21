import unittest

from repoze.bfg import testing

class ViewTests(unittest.TestCase):
    def test_my_view(self):
        from lqndemo.views import my_view
        context = testing.DummyModel()
        request = testing.DummyRequest()
        info = my_view(context, request)
        self.assertEqual(info['project'], 'lqnDemo')
