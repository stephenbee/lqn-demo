from repoze.bfg.view import bfg_view, render_view
from lqndemo.interfaces import IlqnServer
from repoze.bfg.chameleon_zpt import render_template_to_response as rtr
from repoze.bfg.chameleon_zpt import get_template


def index(context,request):
    master = get_template('templates/master.pt')
    return rtr('templates/index.pt',master=master)

def send(context,request):
    if request.POST.has_key('amount'):
        print 'sending something'
    master = get_template('templates/master.pt')
    return rtr('templates/send.pt',master=master)

def receive(context,request):
    master = get_template('templates/master.pt')
    return rtr('templates/receive.pt',master=master)

def transactions(context,request):
    master = get_template('templates/master.pt')
    return rtr('templates/transactions.pt',master=master)




