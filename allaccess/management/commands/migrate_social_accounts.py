from __future__ import unicode_literals

from django.core.management.base import NoArgsCommand, CommandError

from allaccess.models import Provider, AccountAccess


class Command(NoArgsCommand):
    "Convert existing associations from django-social-auth to django-all-access."

    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity'))
        try:
            from social_auth.models import UserSocialAuth
        except ImportError: # pragma: no cover
            raise CommandError("django-social-auth is not installed.")
        providers = {}
        missing = object()
        total_created = 0
        total_skipped = 0
        total_exiting = 0
        for social in UserSocialAuth.objects.all():
            provider = providers.get(social.provider, None)
            if provider is None:
                try:
                    provider = Provider.objects.get(name=social.provider)
                except Provider.DoesNotExist:
                    providers[social.provider] = missing
                    if verbosity > 0:
                        self.stdout.write('No "%s" provider found.\n' % social.provider)
                else:
                    providers[provider.name] = provider
            if provider is not None and provider is not missing:
                defaults = {
                    'user': social.user,
                }
                access, created = AccountAccess.objects.get_or_create(
                    identifier=social.uid, provider=provider, defaults=defaults
                )
                if created:
                    total_created += 1
                else:
                    total_exiting += 1
            else:
                total_skipped += 1
        if verbosity > 0:
            self.stdout.write('%s associations created.\n' % total_created)
            self.stdout.write('%s associations already existed.\n' % total_exiting)
            self.stdout.write('%s associations skipped.\n' % total_skipped)
