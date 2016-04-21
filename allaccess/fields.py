from __future__ import unicode_literals

import binascii
import hmac

from django.conf import settings
from django.db import models
from django.utils.encoding import force_bytes, force_text

try:
    import Crypto.Cipher.AES
except ImportError:  # pragma: no cover
    raise ImportError('PyCrypto is required to use django-all-access.')


def compare_digest(a, b):
    try:
        # new in python 2.7.7
        from hmac import compare_digest
        return compare_digest(a, b)
    except ImportError:
        return a == b


class EncryptedField(models.TextField):
    """
    This code is based on http://www.djangosnippets.org/snippets/1095/
    and django-fields https://github.com/svetlyak40wt/django-fields
    """
    cipher_class = Crypto.Cipher.AES
    prefix = b'$AES$'

    def __init__(self, *args, **kwargs):
        self.cipher = self.cipher_class.new(force_bytes(settings.SECRET_KEY)[:32])
        super(EncryptedField, self).__init__(*args, **kwargs)

    def _is_encrypted(self, value):
        return value.startswith(self.prefix)

    def _split_value(self, value):
        #: split value from database into _, prefix, hmac, cypher_text
        parts = value.split(b'$')
        if len(parts) == 3:
            parts.insert(2, None)
        return parts

    def _is_signed(self, value):
        #: value consists of 3 or 4 $ separated parts, check for hmac in 2nd
        _, prefix, hmac, cypher_text = self._split_value(value)
        return hmac is not None

    def _get_padding(self, value):
        # We always want at least 2 chars of padding (including zero byte),
        # so we could have up to block_size + 1 chars.
        mod = (len(value) + 2) % self.cipher.block_size
        return self.cipher.block_size - mod + 2


    def _encrypt(self, clear_text):
        padding = self._get_padding(clear_text)
        if padding > 0:
            clear_text = clear_text + b'\x00' + b'*' * (padding - 1)
        return self.prefix + binascii.b2a_hex(self.cipher.encrypt(clear_text))

    def _get_signature(self, value):
        return hmac.new(force_bytes(settings.SECRET_KEY), value).hexdigest()

    def _decrypt(self, cypher_text):
        _, prefix, hmac, cypher_text = self._split_value(cypher_text)
        if compare_digest(self._get_signature(cypher_text), hmac):
            cypher_text = binascii.a2b_hex(cypher_text)
            return self.cipher.decrypt(cypher_text).split(b'\x00')[0]
        raise Exception('SignatureException: '
                        'EncryptedField cannot be decrypted. '
                        'Did settings.SECRET_KEY change?')

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        value = force_bytes(value)
        if self._is_encrypted(value):
            return force_text(self._decrypt(value))
        return force_text(value)

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if self.null:
            # Normalize empty values to None
            value = value or None
        if value is None:
            return None
        value = force_bytes(value)
        if not self._is_encrypted(value):
            value = self._encrypt(value)
        return force_text(value)
