try:
    # Django 1.4+
    from django.conf.urls import patterns, url
except ImportError: # pragma: no cover
    # Django 1.3
    from django.conf.urls.defaults import patterns, url

from .views import OAuthRedirect, OAuthCallback


urlpatterns = patterns('',
    url(r'^login/(?P<provider>(\w|-)+)/$', OAuthRedirect.as_view(), name='allaccess-login'),
    url(r'^callback/(?P<provider>(\w|-)+)/$', OAuthCallback.as_view(), name='allaccess-callback'),
)
