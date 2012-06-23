"Helpers to add provider and account access information to the template context."
from __future__ import unicode_literals

from .models import Provider


def available_providers(request):
    "Adds the list of enabled providers to the context."
    return {'allaccess_providers':  Provider.objects.enabled()}
