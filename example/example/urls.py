from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import logout_then_login

from .views import home


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allaccess.urls')),
    url(r'^logout/$', logout_then_login, name='logout'),
    url(r'^$', home, name='home'),
]
