from __future__ import unicode_literals

from django.contrib.auth.backends import ModelBackend

from .models import AccountAccess


class AuthorizedServiceBackend(ModelBackend):
    "Authentication backend for users registered with remote service."

    def authenticate(self, identifier=None, service=None):
        "Fetch user for a given service by id."
        try:
            acccess = AccountAccess.objects.filter(
                identifier=identifier, service=service
            ).select_related('user')[0]
        except IndexError:
            return None
        else:
            return access.user
