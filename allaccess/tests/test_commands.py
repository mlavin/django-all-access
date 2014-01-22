from __future__ import unicode_literals

from django.core.management import call_command

from .base import AllAccessTestCase, Provider, skipIf

try:
    import social_auth
    SOCIAL_AUTH_MISSING = False
except ImportError:
    SOCIAL_AUTH_MISSING = True


@skipIf(SOCIAL_AUTH_MISSING, 'django-social-auth is not installed.')
class MigrateProvidersTestCase(AllAccessTestCase):
    """Management command to migrate providers from django-social-auth."""

    def test_not_enabled_providers(self):
        """Providers which aren't enabled won't be created."""
        with self.settings(AUTHENTICATION_BACKENDS=['social_auth.backends.facebook.FacebookBackend'],
            FACEBOOK_APP_ID=None, FACEBOOK_API_SECRET=None):
            call_command('migrate_social_providers')
        self.assertRaises(Provider.DoesNotExist, Provider.objects.get, name='facebook')

    def test_create_providers(self):
        """Create provider records from django-social-auth backends."""
        with self.settings(AUTHENTICATION_BACKENDS=['social_auth.backends.facebook.FacebookBackend'],
            FACEBOOK_APP_ID='XXX', FACEBOOK_API_SECRET='YYY'):
            call_command('migrate_social_providers')
        facebook = Provider.objects.get(name='facebook')
        self.assertEqual(facebook.key, 'XXX')
        self.assertEqual(facebook.secret, 'YYY')

    def test_existing_providers(self):
        """Do not change settings for existing providers."""
        self.create_provider(name='facebook', key='ABC', secret='XYZ')
        with self.settings(AUTHENTICATION_BACKENDS=['social_auth.backends.facebook.FacebookBackend'],
            FACEBOOK_APP_ID='XXX', FACEBOOK_API_SECRET='YYY'):
            call_command('migrate_social_providers')
        facebook = Provider.objects.get(name='facebook')
        self.assertEqual(facebook.key, 'ABC')
        self.assertEqual(facebook.secret, 'XYZ')
