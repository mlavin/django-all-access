from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError
from django.urls import include, path

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
    path('allaccess/', include('allaccess.urls')),
    path('allaccess/', include('allaccess.tests.custom.urls')),
    path('error/', error, name='test-error'),
    path('login/', login, name='test-login'),
    path('', home, name='test-home'),
]
