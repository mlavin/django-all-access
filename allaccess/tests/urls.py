from django.conf.urls import url, include, handler404, handler500
from django.contrib import admin
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError


admin.autodiscover()

handler404 = 'allaccess.tests.urls.test_404'
handler500 = 'allaccess.tests.urls.test_500'


def error(request):
    return HttpResponse('Error')


def home(request):
    return HttpResponse('Home')


def login(request):
    return HttpResponse('Login')


def test_404(request, exception=None):
    return HttpResponseNotFound()


def test_500(request):
    return HttpResponseServerError()


urlpatterns = [
    url(r'^allaccess/', include('allaccess.urls')),
    url(r'^allaccess/', include('allaccess.tests.custom.urls')),
    url(r'^error/$', error, name='test-error'),
    url(r'^login/$', login, name='test-login'),
    url(r'^$', home, name='test-home'),
]
