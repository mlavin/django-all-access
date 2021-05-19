from django.urls import path

from .views import OAuthCallback, OAuthRedirect

urlpatterns = [
    path('login/<str:provider>/', OAuthRedirect.as_view(), name='allaccess-login'),
    path('callback/<str:provider>/', OAuthCallback.as_view(), name='allaccess-callback'),
]
