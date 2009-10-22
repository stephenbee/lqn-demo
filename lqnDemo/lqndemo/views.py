from repoze.bfg.view import bfg_view, render_view
from lqndemo.interfaces import IlqnServer
from repoze.bfg.chameleon_zpt import render_template_to_response as rtr
from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.security import remember, forget
from repoze.bfg.security import authenticated_userid
from security import users
from webob.exc import HTTPFound

def index(context,request):
    master = get_template('templates/master.pt')
    logged_in = authenticated_userid(request)
    return rtr('templates/index.pt',context=context,request=request,master=master,logged_in=logged_in)

def send(context,request):
    if request.POST.has_key('amount'):
        print 'sending something'
    master = get_template('templates/master.pt')
    logged_in = authenticated_userid(request)
    return rtr('templates/send.pt',context=context,request=request,master=master,logged_in=logged_in)

def receive(context,request):
    master = get_template('templates/master.pt')
    logged_in = authenticated_userid(request)
    return rtr('templates/receive.pt',context=context,request=request,master=master,logged_in=logged_in)

def transactions(context,request):
    master = get_template('templates/master.pt')
    logged_in = authenticated_userid(request)
    return rtr('templates/transactions.pt',context=context,request=request,master=master,logged_in=logged_in)

def login(context,request):
    referrer = request.url
    if referrer == '/login.html':
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    if 'login' in request.POST.keys():
        login = request.params['login']
        password = request.params['password']
        accounts = context['accounts']
        #import pdb; pdb.set_trace()
        if password and accounts.has_key(login) and str(password) == str(accounts.get(login).password):
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
    master = get_template('templates/master.pt')
    logged_in = authenticated_userid(request)
    return rtr('templates/login.pt',context=context,request=request,master=master,message='',logged_in=logged_in,came_from=came_from)

def logout(context, request):
    headers = forget(request)
    return HTTPFound(location = '/',
                     headers = headers)


