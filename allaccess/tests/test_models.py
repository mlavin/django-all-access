"Models and field encryption tests."
from __future__ import unicode_literals

from .base import AllAccessTestCase, Provider, AccountAccess


class ProviderTestCase(AllAccessTestCase):
    "Custom provider methods and key/secret encryption."

    def setUp(self):
        self.provider = self.create_provider()

    def test_save_empty_key(self):
        "None/blank key should normalize to None which is not encrypted."
        self.provider.key = ''
        self.provider.save()
        self.assertEqual(self.provider.key, None)

        self.provider.key = None
        self.provider.save()
        self.assertEqual(self.provider.key, None)

    def test_save_empty_secret(self):
        "None/blank secret should normalize to None which is not encrypted."
        self.provider.secret = ''
        self.provider.save()
        self.assertEqual(self.provider.secret, None)

        self.provider.secret = None
        self.provider.save()
        self.assertEqual(self.provider.secret, None)

    def test_encrypted_save(self):
        "Encrypt key/secret on save."
        key = self.get_random_string()
        secret = self.get_random_string()
        self.provider.key = key
        self.provider.secret = secret
        self.provider.save()
        found_key = Provider.objects.filter(key=key).exists()
        self.assertFalse(found_key, "Cannot filter on unencrypted key.")
        found_secret = Provider.objects.filter(secret=secret).exists()
        self.assertFalse(found_secret, "Cannot filter on unencrypted secret.")

    def test_encrypted_fetch(self):
        "Decrypt key/secret on save."
        key = self.get_random_string()
        secret = self.get_random_string()
        self.provider.key = key
        self.provider.secret = secret
        self.provider.save()
        provider = Provider.objects.get(pk=self.provider.pk)
        self.assertEqual(provider.key, key, "Could not decrypt key.")
        self.assertEqual(provider.secret, secret, "Could not decrypt secret.")

    def test_encrypted_prefix(self):
        "Check encyption prefix."
        key = self.get_random_string()
        secret = self.get_random_string()
        self.provider.key = key
        self.provider.secret = secret
        self.provider.save()
        provider = Provider.objects.extra(
            select={'raw_key': 'key', 'raw_secret': 'secret'}
        ).get(pk=self.provider.pk)
        self.assertNotEqual(provider.raw_key, key)
        self.assertTrue(provider.raw_key.startswith('$AES$'))
        self.assertNotEqual(provider.raw_secret, secret)
        self.assertTrue(provider.raw_secret.startswith('$AES$'))

    def test_enabled_filter(self):
        "Return only providers with key/secret pairs."
        key = self.get_random_string()
        secret = self.get_random_string()
        self.provider.key = key
        self.provider.secret = secret
        self.provider.save()
        other_provider = self.create_provider(key=None, secret=None)
        self.assertTrue(self.provider.enabled())
        self.assertTrue(self.provider in Provider.objects.enabled())
        self.assertFalse(other_provider.enabled())
        self.assertFalse(other_provider in Provider.objects.enabled())


class AccountAccessTestCase(AllAccessTestCase):
    "Custom AccountAccess methods and access token encryption."

    def setUp(self):
        self.access = self.create_access()

    def test_save_empty_token(self):
        "None/blank access token should normalize to None which is not encrypted."
        self.access.access_token = ''
        self.access.save()
        self.assertEqual(self.access.access_token, None)

        self.access.access_token = None
        self.access.save()
        self.assertEqual(self.access.access_token, None)

    def test_encrypted_save(self):
        "Encrypt access token on save."
        access_token = self.get_random_string()
        self.access.access_token = access_token
        self.access.save()
        found = AccountAccess.objects.filter(access_token=access_token).exists()
        self.assertFalse(found, "Cannot filter on unencrypted token.")
        access = AccountAccess.objects.get(pk=self.access.pk)
        self.assertEqual(access.access_token, access_token, "Token should be unencrypted on fetch.")

    def test_encrypted_update(self):
        "Access token should be encrypted on update."
        access_token = self.get_random_string()
        AccountAccess.objects.filter(pk=self.access.pk).update(access_token=access_token)
        found = AccountAccess.objects.filter(access_token=access_token).exists()
        self.assertFalse(found, "Cannot filter on unencrypted token.")

    def test_raw_token_storage(self):
        "Fetch raw token encrypted token."
        access_token = self.get_random_string()
        self.access.access_token = access_token
        self.access.save()
        access = AccountAccess.objects.extra(
            select={'raw_token': 'access_token'}
        ).get(pk=self.access.pk)
        self.assertNotEqual(access.raw_token, access_token)
        self.assertTrue(access.raw_token.startswith('$AES$'))

    def test_fetch_api_client(self):
        "Get API client with the provider and user token set."
        access_token = self.get_random_string()
        self.access.access_token = access_token
        self.access.save()
        api = self.access.api_client
        self.assertEqual(api.provider, self.access.provider)
        self.assertEqual(api.token, self.access.access_token)
