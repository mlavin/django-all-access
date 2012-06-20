from __future__ import unicode_literals

from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import Provider, AccountAccess


class AuthorizedServiceBackend(ModelBackend):
    "Authentication backend for users registered with remote OAuth provider."

    def authenticate(self, provider=None, identifier=None):
        "Fetch user for a given provider by id."
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
