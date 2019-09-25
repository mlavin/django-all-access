from django.urls import re_path

from .views import OAuthCallback, OAuthRedirect

urlpatterns = [
    re_path(r'^login/(?P<provider>(\w|-)+)/$', OAuthRedirect.as_view(), name='allaccess-login'),
    re_path(r'^callback/(?P<provider>(\w|-)+)/$', OAuthCallback.as_view(), name='allaccess-callback'),
]
