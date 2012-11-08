from __future__ import unicode_literals
from datetime import datetime

from django.db import models

from .clients import get_client
from .compat import AUTH_USER_MODEL
from .fields import EncryptedField


class ProviderManager(models.Manager):
    "Additional manager methods for Providers."

    def enabled(self):
        "Filter down providers which have key/secret pairs."
        return super(ProviderManager, self).filter(key__isnull=False, secret__isnull=False)


class Provider(models.Model):
    "Configuration for OAuth provider."

    name = models.CharField(max_length=50, unique=True)
    request_token_url = models.URLField(blank=True)
    authorization_url = models.URLField()
    access_token_url = models.URLField()
    profile_url = models.URLField()
    key = EncryptedField(blank=True, null=True, default=None)
    secret = EncryptedField(blank=True, null=True, default=None)

    objects = ProviderManager()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.key = self.key or None
        self.secret = self.secret or None
        super(Provider, self).save(*args, **kwargs)

    def enabled(self):
        return self.key is not None and self.secret is not None
    enabled.boolean = True


class AccountAccess(models.Model):
    "Authorized remote OAuth provider."

    identifier = models.CharField(max_length=255)
    provider = models.ForeignKey(Provider)
    user = models.ForeignKey(AUTH_USER_MODEL, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, default=datetime.now)
    modified = models.DateTimeField(auto_now=True, default=datetime.now)    
    access_token = EncryptedField(blank=True, null=True, default=None)

    class Meta(object):
        unique_together = ('identifier', 'provider')

    def __unicode__(self):
        return '{0} {1}'.format(self.provider, self.identifier)

    def save(self, *args, **kwargs):
        self.access_token = self.access_token or None
        super(AccountAccess, self).save(*args, **kwargs)

    @property
    def api_client(self):
        return get_client(self.provider, self.access_token or '')
