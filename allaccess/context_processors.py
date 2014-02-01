"Helpers to add provider and account access information to the template context."
from __future__ import unicode_literals

from django.utils.functional import SimpleLazyObject

from .compat import APPENGINE 
from .models import Provider


def _get_enabled():
    """Wrapped function for filtering enabled providers."""
    providers = Provider.objects.all()
    return [p for p in providers if p.enabled()]


def available_providers(request):
    "Adds the list of enabled providers to the context."
    if APPENGINE:
        # Note: AppEngine inequality queries are limited to one property.
        # See https://developers.google.com/appengine/docs/python/datastore/queries#Python_Restrictions_on_queries
        # Users have also noted that the exclusion queries don't work
        # See https://github.com/mlavin/django-all-access/pull/46
        # So this is lazily-filtered in Python
        qs = SimpleLazyObject(lambda: _get_enabled())
    else:
        qs = Provider.objects.filter(consumer_secret__isnull=False, consumer_key__isnull=False)
    return {'allaccess_providers': qs}
