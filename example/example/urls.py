from django.contrib import admin
from django.contrib.auth.views import logout_then_login
from django.urls import include, path

from .views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allaccess.urls')),
    path('logout/', logout_then_login, name='logout'),
    path('', home, name='home'),
]
