from django.conf.urls import patterns, url

from .views import OAuthRedirect, OAuthCallback


urlpatterns = patterns('',
    url(r'^login/(?P<service>(\w|-)+)/$', OAuthRedirect.as_view(), name='allaccess-login'),
    url(r'^callback/(?P<service>(\w|-)+)/$', OAuthCallback.as_view(), name='allaccess-callback'),
)
