from django.contrib import admin
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError
try:
    # Django 1.4+
    from django.conf.urls import patterns, url, include, handler404, handler500
except ImportError: # pragma: no cover
    # Django 1.3
    from django.conf.urls.defaults import patterns, url, include, handler404, handler500


admin.autodiscover()

handler404 = 'allaccess.tests.urls.test_404'
handler500 = 'allaccess.tests.urls.test_500'


def error(request):
    return HttpResponse('Error')


def home(request):
    return HttpResponse('Home')


def login(request):
    return HttpResponse('Login')


def test_404(request):
    return HttpResponseNotFound()


def test_500(request):
    return HttpResponseServerError()


urlpatterns = patterns('',
    url(r'^allaccess/', include('allaccess.urls')),
    url(r'^allaccess/', include('allaccess.tests.custom.urls')),
    url(r'^error/$', error),
    url(r'^login/$', login),
    url(r'^$', home),
)
