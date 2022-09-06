from django.urls import re_path

from .views import CustomCallback, CustomRedirect

urlpatterns = [
    re_path(r'^custom-login/(?P<provider>(\w|-)+)/$',
        CustomRedirect.as_view(), name='custom-login'),
    re_path(r'^custom-callback/(?P<provider>(\w|-)+)/$',
        CustomCallback.as_view(), name='custom-callback'),
]
