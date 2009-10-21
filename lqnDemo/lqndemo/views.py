from repoze.bfg.view import bfg_view, render_view
from lqndemo.interfaces import IlqnServer
from repoze.bfg.chameleon_zpt import render_template_to_response as rtr
from repoze.bfg.chameleon_zpt import get_template


def index(context,request):
    master = get_template('templates/master.pt')
    return rtr('templates/test.pt',master=master)

