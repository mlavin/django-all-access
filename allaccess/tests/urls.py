from django.conf.urls import patterns, url, include
from django.http import HttpResponse


def error(request):
    return HttpResponse('Error')


def home(request):
    return HttpResponse('Home')


def login(request):
    return HttpResponse('Login')


urlpatterns = patterns('',
    url(r'^allaccess/', include('allaccess.urls')),
    url(r'^error/$', error),
    url(r'^login/$', login),
    url(r'^$', home),
)
