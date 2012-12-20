try:
    # Django 1.4+
    from django.conf.urls import patterns, url
except ImportError: # pragma: no cover
    # Django 1.3
    from django.conf.urls.defaults import patterns, url

from .views import CustomRedirect, CustomCallback


urlpatterns = patterns('',
    url(r'^custom-login/(?P<provider>(\w|-)+)/$', CustomRedirect.as_view(), name='custom-login'),
    url(r'^custom-callback/(?P<provider>(\w|-)+)/$', CustomCallback.as_view(), name='custom-callback'),
)
