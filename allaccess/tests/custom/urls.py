from django.conf.urls import url

from .views import CustomRedirect, CustomCallback


urlpatterns = [
    url(r'^custom-login/(?P<provider>(\w|-)+)/$',
        CustomRedirect.as_view(), name='custom-login'),
    url(r'^custom-callback/(?P<provider>(\w|-)+)/$',
        CustomCallback.as_view(), name='custom-callback'),
]
