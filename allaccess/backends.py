from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import AccountAccess, Provider


class AuthorizedServiceBackend(ModelBackend):
    """
    Authentication backend for users registered with remote OAuth provider.
    """

    def authenticate(self, request, provider=None, identifier=None, **kwargs):
        """Fetch user for a given provider by id."""
        provider_q = Q(provider__name=provider)
        if isinstance(provider, Provider):
            provider_q = Q(provider=provider)
        try:
            access = AccountAccess.objects.filter(
                provider_q, identifier=identifier
            ).select_related('user')[0]
        except IndexError:
            return None
        else:
            return access.user
