"Models and field encryption tests."
from __future__ import unicode_literals

from .base import AllAccessTestCase, Provider


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
        key_field = Provider._meta.get_field('key')
        encrypted_key = key_field.get_db_prep_value('key')
        self.assertTrue(encrypted_key.startswith('$AES$'))
        secret_field = Provider._meta.get_field('secret')
        encrypted_secret = secret_field.get_db_prep_value('secret')
        self.assertTrue(encrypted_secret.startswith('$AES$'))
