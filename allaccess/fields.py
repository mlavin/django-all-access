# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import binascii
import hmac

from django.conf import settings
from django.db import models
from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes, force_text

try:
    import Crypto.Cipher.AES
except ImportError:  # pragma: no cover
    raise ImportError('PyCrypto is required to use django-all-access.')


class SignatureException(Exception):
    pass


class SignedAESEncryption(object):
    cipher_class = Crypto.Cipher.AES
    prefix = b'$AES'
    #: enable hmac signature of cypher text with the same key (default: True)
    sign = True

    def __init__(self, *args, **kwargs):
        self.cipher = self.cipher_class.new(self.get_key())

    def get_key(self):
        return force_bytes(settings.SECRET_KEY.zfill(32))[:32]

    def get_signature(self, value):
        return force_bytes(hmac.new(self.get_key(), value).hexdigest())

    def get_padding(self, value):
        # We always want at least 2 chars of padding (including zero byte),
        # so we could have up to block_size + 1 chars.
        mod = (len(value) + 2) % self.cipher.block_size
        return self.cipher.block_size - mod + 2

    def add_padding(self, clear_text):
        padding = self.get_padding(clear_text)
        if padding > 0:
            return clear_text + b'\x00' + b'*' * (padding - 1)
        return clear_text

    def split_value(self, value):
        #: split value from database into _, prefix, mac, cypher_text
        parts = value.split(b'$')
        if len(parts) == 3:
            parts.insert(2, None)
        return parts

    def is_encrypted(self, value):
        return value.startswith(self.prefix)

    def is_signed(self, value):
        #: value consists of 3 or 4 $ separated parts, check for mac in 2nd
        _, prefix, mac, cypher_text = self.split_value(value)
        return mac is not None

    def decrypt(self, cypher_text):
        _, prefix, mac, cypher_text = self.split_value(cypher_text)
        if self.sign and mac and \
                not constant_time_compare(self.get_signature(cypher_text), mac):
            raise SignatureException(
                'EncryptedField cannot be decrypted. '
                'Did settings.SECRET_KEY change?'
            )
        cypher_text = binascii.a2b_hex(cypher_text)
        return self.cipher.decrypt(cypher_text).split(b'\x00')[0]

    def encrypt(self, clear_text):
        clear_text = self.add_padding(clear_text)
        cypher_text = binascii.b2a_hex(self.cipher.encrypt(clear_text))
        parts = [self.prefix]
        if self.sign:
            parts.append(self.get_signature(cypher_text))
        parts.append(cypher_text)
        return b'$'.join(parts)


class EncryptedField(models.TextField):
    """
    This code is based on http://www.djangosnippets.org/snippets/1095/
    and django-fields https://github.com/svetlyak40wt/django-fields
    """
    encryption_class = SignedAESEncryption

    def __init__(self, *args, **kwargs):
        self.cipher = self.encryption_class()
        super(EncryptedField, self).__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        value = force_bytes(value)
        if self.cipher.is_encrypted(value):
            return force_text(self.cipher.decrypt(value))
        return force_text(value)

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if self.null:
            # Normalize empty values to None
            value = value or None
        if value is None:
            return None
        value = force_bytes(value)
        if not self.cipher.is_encrypted(value):
            value = self.cipher.encrypt(value)
        return force_text(value)
