from __future__ import unicode_literals

from django.conf import settings
from django.core.management import call_command
from django.utils import six

from .base import AllAccessTestCase, Provider, AccountAccess, skipIf

try:
    import social_auth
    SOCIAL_AUTH_MISSING = 'social_auth' not in settings.INSTALLED_APPS
except ImportError:
    SOCIAL_AUTH_MISSING = True


@skipIf(SOCIAL_AUTH_MISSING, 'django-social-auth is not installed.')
class MigrateProvidersTestCase(AllAccessTestCase):
    """Management command to migrate providers from django-social-auth."""

    def test_not_enabled_providers(self):
        """Providers which aren't enabled won't be created."""
        with self.settings(AUTHENTICATION_BACKENDS=['social_auth.backends.facebook.FacebookBackend'],
            FACEBOOK_APP_ID=None, FACEBOOK_API_SECRET=None):
            del settings.FACEBOOK_APP_ID
            del settings.FACEBOOK_API_SECRET
            call_command('migrate_social_providers', stdout=six.StringIO(), stderr=six.StringIO())
        self.assertRaises(Provider.DoesNotExist, Provider.objects.get, name='facebook')

    def test_create_providers(self):
        """Create provider records from django-social-auth backends."""
        with self.settings(AUTHENTICATION_BACKENDS=['social_auth.backends.facebook.FacebookBackend'],
            FACEBOOK_APP_ID='XXX', FACEBOOK_API_SECRET='YYY'):
            call_command('migrate_social_providers', stdout=six.StringIO(), stderr=six.StringIO())
        facebook = Provider.objects.get(name='facebook')
        self.assertEqual(facebook.consumer_key, 'XXX')
        self.assertEqual(facebook.consumer_secret, 'YYY')

    def test_existing_providers(self):
        """Do not change settings for existing providers."""
        self.create_provider(name='facebook', consumer_key='ABC', consumer_secret='XYZ')
        with self.settings(AUTHENTICATION_BACKENDS=['social_auth.backends.facebook.FacebookBackend'],
            FACEBOOK_APP_ID='XXX', FACEBOOK_API_SECRET='YYY'):
            call_command('migrate_social_providers', stdout=six.StringIO(), stderr=six.StringIO())
        facebook = Provider.objects.get(name='facebook')
        self.assertEqual(facebook.consumer_key, 'ABC')
        self.assertEqual(facebook.consumer_secret, 'XYZ')


@skipIf(SOCIAL_AUTH_MISSING, 'django-social-auth is not installed.')
class MigrateAccountsTestCase(AllAccessTestCase):
    """Management command to migrate accounts from django-social-auth."""

    def create_user_social_auth(self, **kwargs):
        from social_auth.models import UserSocialAuth
        defaults = {
            'provider': 'facebook',
            'uid': self.get_random_string(),
        }
        defaults.update(kwargs)
        if 'user' not in defaults:
            defaults['user'] = self.create_user()
        return UserSocialAuth.objects.create(**defaults)

    def test_unknown_provider(self):
        """Associations to unknown providers are skipped."""
        self.create_user_social_auth(provider='facebook')
        self.create_user_social_auth(provider='facebook')
        call_command('migrate_social_accounts', stdout=six.StringIO(), stderr=six.StringIO())
        self.assertEqual(AccountAccess.objects.count(), 0)

    def test_create_association(self):
        """Create a new AccountAccess from an existing UserSocialAuth."""
        provider = self.create_provider(name='facebook')
        auth = self.create_user_social_auth(provider='facebook')
        call_command('migrate_social_accounts', stdout=six.StringIO(), stderr=six.StringIO())
        self.assertEqual(AccountAccess.objects.count(), 1)
        access = AccountAccess.objects.latest('pk')
        self.assertEqual(access.identifier, auth.uid)
        self.assertEqual(access.provider, provider)
        self.assertEqual(access.user, auth.user)

    def test_existing_association(self):
        """Existing AccountAccess records should not be modified."""
        provider = self.create_provider(name='facebook')
        access = self.create_access(provider=provider)
        auth = self.create_user_social_auth(provider='facebook', uid=access.identifier)
        self.assertNotEqual(access.user, auth.user)
        call_command('migrate_social_accounts', stdout=six.StringIO(), stderr=six.StringIO())
        self.assertEqual(AccountAccess.objects.count(), 1)
        access = AccountAccess.objects.get(pk=access.pk)
        self.assertNotEqual(access.user, auth.user)
