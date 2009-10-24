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
    return rtr('templates/index.pt',context=context,request=request,master=master,logged_in=logged_in,message=None)

def send(context,request):
    post = request.POST
    logged_in = authenticated_userid(request)
    accounts = context['accounts']
    errors = {}
    message = ''
    if post.has_key('amount'):
        amount = post.get('amount','')
        try:
            amount = int(amount)
        except ValueError:
            errors['amount'] = 'not a valid number'
        if amount <= 0:
            errors['amount'] = 'amount needs be at least 1'
        target = post.get('target','')    
        if not accounts.has_key(target):
            errors['target'] = 'not a valid account'                

        if errors:
            message= 'please correct the errors'
        else:       
            source = accounts.get(logged_in)
            source.transfer(target,amount)
            return HTTPFound(location='/')
    
            
    master = get_template('templates/master.pt')
    return rtr('templates/send.pt',context=context,request=request,master=master,logged_in=logged_in,message=message,errors=errors)

def receive(context,request):
    master = get_template('templates/master.pt')
    logged_in = authenticated_userid(request)
    accounts = context['accounts']
    errors = {}
    message = ''
    post = request.POST
    if post.has_key('amount'):
        amount = post.get('amount','')
        try:
            amount = int(amount)
        except ValueError:
            errors['amount'] = 'not a valid number'
        if amount <= 0:
            errors['amount'] = 'amount needs be at least 1'
        source = post.get('source','')    
        if not accounts.has_key(source):
            errors['source'] = 'not a valid account'                
        else:
            pin = post.get('pin','')
            if pin != accounts.get(source).password:
                errors['pin'] = 'invalid password'
        if errors:
            message= 'please correct the errors'
        else:       
            tacc = accounts.get(logged_in)
            sacc = accounts.get(source)
            sacc.transfer(logged_in,amount)
            return rtr('templates/paid.pt',context=context,request=request,master=master,logged_in=logged_in,source=sacc,target=tacc,amount=amount,message=message)

    return rtr('templates/receive.pt',context=context,request=request,master=master,logged_in=logged_in,message=None,errors=errors)

def transactions(context,request):
    master = get_template('templates/master.pt')
    logged_in = authenticated_userid(request)
    return rtr('templates/transactions.pt',context=context,request=request,master=master,logged_in=logged_in,message=None)

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


