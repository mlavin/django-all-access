from __future__ import unicode_literals

from django.core.management.base import NoArgsCommand, CommandError

from allaccess.models import Provider 


class Command(NoArgsCommand):
    "Convert existing providers from django-social-auth to django-all-access."

    def handle_noargs(self, **options):
        try:
            from social_auth.backends import get_backends, BaseOAuth
        except ImportError:
            raise CommandError("django-social-auth is not installed.")
        for name, backend in get_backends(force_load=True).items():
            if issubclass(backend, BaseOAuth) and backend.enabled():
                # Create providers if they don't already exist
                key, secret = backend.get_key_and_secret()
                defaults = {
                    'request_token_url': getattr(backend, 'REQUEST_TOKEN_URL', ''),
                    'authorization_url': getattr(backend, 'AUTHORIZATION_URL', ''),
                    'access_token_url': getattr(backend, 'ACCESS_TOKEN_URL', ''),
                    'profile_url': '',
                    'key': key or None,
                    'secret': secret or None,
                }
                provider, created = Provider.objects.get_or_create(name=name, defaults=defaults)
                if created:
                    self.stdout.write('New provider created from "%s" backend.\n' % name)
