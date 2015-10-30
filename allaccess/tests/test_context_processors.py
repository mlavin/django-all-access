from __future__ import unicode_literals

from django.test.client import RequestFactory

from .base import AllAccessTestCase
from ..context_processors import available_providers


class AvailableProvidersTestCase(AllAccessTestCase):
    "Processor to add available Providers to the context."

    def setUp(self):
        self.enabled_provider = self.create_provider(
            consumer_key=self.get_random_string(), consumer_secret=self.get_random_string()
        )
        self.disabled_provider = self.create_provider(consumer_key=None, consumer_secret=None)
        self.factory = RequestFactory()

    def test_enabled_filter(self):
        "Return only providers with key/secret pairs."
        request = self.factory.get("/")
        context = available_providers(request)
        self.assertTrue('allaccess_providers' in context)
        providers = context['allaccess_providers']
        self.assertTrue(self.enabled_provider in providers)
        self.assertFalse(self.disabled_provider in providers)

    def test_no_queries(self):
        "Context processor should not execute any queries (only lazy queryset)."
        request = self.factory.get("/")
        with self.assertNumQueries(0):
            available_providers(request)
