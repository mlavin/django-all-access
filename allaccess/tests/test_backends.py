from django.contrib.auth import authenticate

from .base import AllAccessTestCase


class AuthBackendTestCase(AllAccessTestCase):
    "Custom contrib.auth backend tests."

    def setUp(self):
        self.user = self.create_user()
        self.access = self.create_access(user=self.user)

    def test_successful_authenticate(self):
        "User successfully authenticated."
        provider = self.access.provider
        identifier = self.access.identifier
        user = authenticate(provider=provider, identifier=identifier)
        self.assertEqual(user, self.user, "Correct user was not returned.")

    def test_provider_name(self):
        "Match on provider name as a string."
        provider = self.access.provider.name
        identifier = self.access.identifier
        user = authenticate(provider=provider, identifier=identifier)
        self.assertEqual(user, self.user, "Correct user was not returned.")

    def test_failed_authentication(self):
        "No matches found for the provider/id pair."
        provider = self.access.provider
        identifier = self.access.identifier
        self.access.delete()
        user = authenticate(provider=provider, identifier=identifier)
        self.assertEqual(user, None, "No user should be returned.")

    def test_match_no_user(self):
        "Matched access is not associated with a user."
        self.access.user = None
        self.access.save()
        user = authenticate(provider=self.access.provider, identifier=self.access.identifier)
        self.assertEqual(user, None, "No user should be returned.")

    def test_performance(self):
        "Only one query should be required to get the user."
        with self.assertNumQueries(1):
            authenticate(provider=self.access.provider, identifier=self.access.identifier)
