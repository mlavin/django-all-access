from __future__ import unicode_literals

from django.core.management.base import NoArgsCommand, CommandError
from django.test.client import RequestFactory

from allaccess.models import Provider


class Command(NoArgsCommand):
    "Convert existing providers from django-social-auth to django-all-access."

    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity'))
        try:
            from social_auth import version
            from social_auth.backends import get_backends, BaseOAuth
        except ImportError: # pragma: no cover
            raise CommandError("django-social-auth is not installed.")
        request = RequestFactory().get('/')
        for name, backend in get_backends().items():
            if issubclass(backend, BaseOAuth) and backend.enabled():
                if version < (0, 7):
                    # Prior to 0.7 get_key_and_secret was an instance method
                    backend = backend(request, '/')
                # Create providers if they don't already exist
                key, secret = backend.get_key_and_secret()
                defaults = {
                    'request_token_url': getattr(backend, 'REQUEST_TOKEN_URL', '') or '',
                    'authorization_url': getattr(backend, 'AUTHORIZATION_URL', '') or '',
                    'access_token_url': getattr(backend, 'ACCESS_TOKEN_URL', '') or '',
                    'profile_url': '',
                    'consumer_key': key or None,
                    'consumer_secret': secret or None,
                }
                provider, created = Provider.objects.get_or_create(name=name, defaults=defaults)
                if created and verbosity > 0:
                    self.stdout.write('New provider created from "%s" backend.\n' % name)
