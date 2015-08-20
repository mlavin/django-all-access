Migrating from Django-Social-Auth
====================================

`django-social-auth <https://github.com/omab/django-social-auth>`_ is a popular alternative
package for handling social registrations. It has since been deprecated and work has
shifted to a more general `python-social-auth <https://github.com/omab/python-social-auth>`_. While
these packages share many of the same goals they have very different approaches. There
are some included utilities to migrate existing data from django-social-auth into django-all-access.

The following commands have been tested with ``django-social-auth>=0.5,<0.8``.


.. versionadded:: 0.6

Creating Providers
------------------------------------

django-social-auth defines providers as a pair of Python classes: a SocialAuthBackend subclass and
a BaseAuth subclass. The SocialAuthBackend subclass is a django.contrib.auth backend which would
be added to the project's ``AUTHENTICATION_BACKENDS``. The BaseAuth defines the OpenID, OAuth, OAuth2,
or other workflow to authenticate with the remote service. The necessary consumer keys and secrets
are defined in the settings file.

On the other hand, django-all-access only handles OAuth 1.0a and OAuth 2.0 providers and these values
are stored in the database. As such, not all provider information can be migrated from django-social-auth
to django-all-access.

To migrate existing providers, you can run the ``migrate_social_providers`` command::

    python manage.py migrate_social_providers

This will create ``Provider`` records based on the enabled OAuth providers from django-social-auth.
This includes the ``name``, ``request_token_url`` (for OAuth 1.0a), ``authorization_url``, ``access_token_url``,
``key`` and ``secret``. Because of a lack of standardization in the django-social-auth backends, the
``profile_url`` cannot be added and needs to be populated manually after running the command. The command
will not make any changes to existing providers (matched based on the name) so it is safe to run
this command more than once.


.. versionadded:: 0.6

Creating Accounts
------------------------------------

Once the providers have been migrated, you can migrate the account association information. Again
because django-all-access only supports OAuth based providers, it is not possible to migrate all
of the associations. In particular associations with OpenID providers or BrowserID accounts cannot
be migrated.

To migrate existing accounts you can run the ``migrate_social_accounts`` command::

    python manage.py migrate_social_accounts

The command will give a summary of the number of accounts created, skipped or already existed. As
with ``migrate_social_providers``, this command does not modify existing associations and can be
run multiple times.
