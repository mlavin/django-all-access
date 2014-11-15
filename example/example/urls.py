from django.conf.urls import include, url
from django.contrib import admin

from .views import home


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allaccess.urls')),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^$', home, name='home'),
]
