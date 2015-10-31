"Functional tests for using a swapped user model."

import unittest

from django.conf import settings

from .. import test_views


@unittest.skipUnless(
    'allaccess.tests.custom' in settings.INSTALLED_APPS,
    'custom user is not installed for testing')
class CustomizedCallbackTestCase(test_views.OAuthCallbackTestCase):
    "OAuth callback customized for swapped user."

    url_name = 'custom-callback'

    def test_create_new_user(self):
        "Create a new user and associate them with the provider."
        self._test_create_new_user()

    def test_existing_user(self):
        "Authenticate existing user and update their access token."
        self._test_existing_user()

    def test_authentication_redirect(self):
        "Post-authentication redirect to LOGIN_REDIRECT_URL."
        self._test_authentication_redirect()
