from repoze.bfg.view import bfg_view, render_view
from lqndemo.interfaces import IlqnServer
from repoze.bfg.chameleon_zpt import render_template_to_response as rtr
from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.security import remember, forget
from repoze.bfg.security import authenticated_userid
from security import users
from webob.exc import HTTPFound
from models import Errors
from webob import Response
import logging


def index(context,request):
    master = get_template('templates/master.pt')
    logged_in = authenticated_userid(request)
    return rtr('templates/index.pt',context=context,request=request,master=master,logged_in=logged_in,message=None)

def send(context,request):
    logging.debug("Sending katz...")
    post = request.POST
    logged_in = authenticated_userid(request)
    accounts = context['accounts']
    errors={}
    message = ''
    if post.has_key('amount'):
        source = accounts.get(logged_in)
        amount = post.get('amount','')
        target = post.get('target','')   
	logging.debug("Source: %s Amount: %s Target: %s",source,amount,target)
        #errors = context['transactions'].isTransactionInvalid(logged_in,target,amount)
        if str(post.get('pin','')) != str(source.password):
	    logging.error("views.py::send Wrong pin")
            errors['pin'] = 'wrong pin'
        try:
            source.transfer(target,amount)
       	    logging.debug("Sending katz successful")
        except Errors, e:
            errors.update(e.message)

        if len(errors):
            message= 'please correct the errors'
        else:       
            return HTTPFound(location='/')
    
            
    master = get_template('templates/master.pt')
    return rtr('templates/send.pt',context=context,request=request,master=master,logged_in=logged_in,message=message,errors=errors)

def receive(context,request):
    logging.debug("Receiving Katz...")
    post = request.POST
    logged_in = authenticated_userid(request)
    accounts = context['accounts']
    errors={}
    message = ''
    master = get_template('templates/master.pt')
    if post.has_key('amount'):
        source = post.get('source','')    
        amount = post.get('amount','')
        target = accounts.get(logged_in)
	logging.debug("Source: %s Amount: %s Target: %s",source,amount,target)
        #errors = context['transactions'].isTransactionInvalid(source,logged_in,amount)
        if str(post.get('pin','')) != str(target.password):
	    logging.error("views.py::receive Invalid pin")
            errors['pin'] = 'invalid pin'

        try:
            tacc = accounts.get(logged_in)
            sacc = accounts.get(source)
            sacc.transfer(logged_in,amount)
            return rtr('templates/paid.pt',context=context,request=request,master=master,logged_in=logged_in,source=sacc,target=tacc,amount=amount,message=message)
        except Errors, e:
            errors.update(e.message)

        if errors:
            message= 'please correct the errors'

    return rtr('templates/receive.pt',context=context,request=request,master=master,logged_in=logged_in,message=None,errors=errors)

def vouchers(context,request):
    master = get_template('templates/master.pt')
    logged_in = authenticated_userid(request)
    errors={}
    post = request.POST
    if 'amount' in post:
        try:
	    logging.debug("views.py::vouchers Adding voucher")
            trans = context['vouchers'].addVoucher(logged_in,post.get('amount'),request.application_url)
	    logging.debug("views.py::vouchers Adding voucher ok")
        except Errors,e:
	    logging.error(e.message)
            errors = e.message
    return rtr('templates/vouchers.pt',context=context,request=request,master=master,logged_in=logged_in,message=None,errors=errors)

def redeem(context,request):
    master = get_template('templates/master.pt')
    logged_in = authenticated_userid(request)
    errors = {}
    post = request.POST
    message = ''
    if context.used:
        message = 'Voucher is already used'
	logging.error("views.py::redeem " + message)
        errors['voucher']   = message
    elif post.has_key('amount'):
        try:
	    logging.debug("views.py::redeem Redeeming voucher..." )
            trans = context.use(logged_in,post.get('amount'))
	    logging.debug("views.py::redeem Redeeming voucher ok." )
            return HTTPFound(location='/')
        except Errors, e:
            errors = e.message
    return rtr('templates/redeem.pt',context=context,request=request,master=master,logged_in=logged_in,message=message,errors=errors)


def transactions(context,request):
    master = get_template('templates/master.pt')
    logged_in = authenticated_userid(request)
    return rtr('templates/transactions.pt',context=context,request=request,master=master,logged_in=logged_in,message=None)

def login(context,request):
    referrer = request.url
    if referrer == '/login.html':
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    logging.debug("views.py::login Logging in...")
    if 'login' in request.POST.keys():
        login = request.params['login']
        password = request.params['password']
        accounts = context['accounts']
        #import pdb; pdb.set_trace()
        if password and accounts.has_key(login) and str(password) == str(accounts.get(login).password):
            headers = remember(request, login)
            logging.debug("views.py::login : Login OK.")
            return HTTPFound(location = came_from,
                             headers = headers)
    master = get_template('templates/master.pt')
    logged_in = authenticated_userid(request)
    return rtr('templates/login.pt',context=context,request=request,master=master,message='',logged_in=logged_in,came_from=came_from)

  
def qrcode(context,request):
    response = Response()
    response.status = 200
    response.body = context.image
    response.headerlist = [('Content-type', 'image/png')]
    return response

def logout(context, request):
    logging.debug("Logging out...")
    headers = forget(request)
    logging.debug("Logged out")
    return HTTPFound(location = '/',
                     headers = headers)


