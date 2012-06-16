from __future__ import unicode_literals

from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .models import Provider, AccountAccess


class AuthorizedServiceBackend(ModelBackend):
    "Authentication backend for users registered with remote service."

    def authenticate(self, service=None, identifier=None):
        "Fetch user for a given service by id."
        service_q = Q(service__name=service)
        if isinstance(service, Provider):
            service_q = Q(service=service)
        try:
            access = AccountAccess.objects.filter(
                service_q, identifier=identifier
            ).select_related('user')[0]
        except IndexError:
            return None
        else:
            return access.user
