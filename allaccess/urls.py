from django.urls import path

from .views import OAuthCallback, OAuthRedirect

urlpatterns = [
    path('login/(?P<str:provider>/', OAuthRedirect.as_view(), name='allaccess-login'),
    path('callback/(?P<str:provider>/', OAuthCallback.as_view(), name='allaccess-callback'),
]
