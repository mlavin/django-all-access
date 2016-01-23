from __future__ import unicode_literals

import base64
import hashlib
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect
from django.utils.encoding import smart_bytes, force_text
from django.views.generic import RedirectView, View

from .clients import get_client
from .models import Provider, AccountAccess


logger = logging.getLogger('allaccess.views')


class OAuthClientMixin(object):
    "Mixin for getting OAuth client for a provider."

    client_class = None

    def get_client(self, provider):
        "Get instance of the OAuth client for this provider."
        if self.client_class is not None:
            return self.client_class(provider)
        return get_client(provider)


class OAuthRedirect(OAuthClientMixin, RedirectView):
    "Redirect user to OAuth provider to enable access."

    permanent = False
    params = None

    def get_additional_parameters(self, provider):
        "Return additional redirect parameters for this provider."
        return self.params or {}

    def get_callback_url(self, provider):
        "Return the callback url for this provider."
        return reverse('allaccess-callback', kwargs={'provider': provider.name})

    def get_redirect_url(self, **kwargs):
        "Build redirect url for a given provider."
        name = kwargs.get('provider', '')
        try:
            provider = Provider.objects.get(name=name)
        except Provider.DoesNotExist:
            raise Http404('Unknown OAuth provider.')
        else:
            if not provider.enabled():
                raise Http404('Provider %s is not enabled.' % name)
            client = self.get_client(provider)
            callback = self.get_callback_url(provider)
            params = self.get_additional_parameters(provider)
            return client.get_redirect_url(self.request, callback=callback, parameters=params)


class OAuthCallback(OAuthClientMixin, View):
    "Base OAuth callback view."

    provider_id = None

    def get(self, request, *args, **kwargs):
        name = kwargs.get('provider', '')
        try:
            provider = Provider.objects.get(name=name)
        except Provider.DoesNotExist:
            raise Http404('Unknown OAuth provider.')
        else:
            if not provider.enabled():
                raise Http404('Provider %s is not enabled.' % name)
            client = self.get_client(provider)
            callback = self.get_callback_url(provider)
            # Fetch access token
            raw_token = client.get_access_token(self.request, callback=callback)
            if raw_token is None:
                return self.handle_login_failure(provider, "Could not retrieve token.")
            # Fetch profile info
            info = client.get_profile_info(raw_token)
            if info is None:
                return self.handle_login_failure(provider, "Could not retrieve profile.")
            identifier = self.get_user_id(provider, info)
            if identifier is None:
                return self.handle_login_failure(provider, "Could not determine id.")
            # Get or create access record
            defaults = {
                'access_token': raw_token,
            }
            access, created = AccountAccess.objects.get_or_create(
                provider=provider, identifier=identifier, defaults=defaults
            )
            if not created:
                access.access_token = raw_token
                AccountAccess.objects.filter(pk=access.pk).update(**defaults)
            user = authenticate(provider=provider, identifier=identifier)
            if user is None:
                return self.handle_new_user(provider, access, info)
            else:
                return self.handle_existing_user(provider, user, access, info)

    def get_callback_url(self, provider):
        "Return callback url if different than the current url."
        return None

    def get_error_redirect(self, provider, reason):
        "Return url to redirect on login failure."
        return settings.LOGIN_URL

    def get_login_redirect(self, provider, user, access, new=False):
        "Return url to redirect authenticated users."
        return settings.LOGIN_REDIRECT_URL

    def get_or_create_user(self, provider, access, info):
        "Create a shell auth.User."
        digest = hashlib.sha1(smart_bytes(access)).digest()
        # Base 64 encode to get below 30 characters
        # Removed padding characters
        username = force_text(base64.urlsafe_b64encode(digest)).replace('=', '')
        User = get_user_model()
        kwargs = {
            User.USERNAME_FIELD: username,
            'email': '',
            'password': None
        }
        return User.objects.create_user(**kwargs)

    def get_user_id(self, provider, info):
        "Return unique identifier from the profile info."
        id_key = self.provider_id or 'id'
        result = info
        try:
            for key in id_key.split('.'):
                result = result[key]
            return result
        except KeyError:
            return None

    def handle_existing_user(self, provider, user, access, info):
        "Login user and redirect."
        login(self.request, user)
        return redirect(self.get_login_redirect(provider, user, access))

    def handle_login_failure(self, provider, reason):
        "Message user and redirect on error."
        logger.error('Authenication Failure: {0}'.format(reason))
        messages.error(self.request, 'Authenication Failed.')
        return redirect(self.get_error_redirect(provider, reason))

    def handle_new_user(self, provider, access, info):
        "Create a shell auth.User and redirect."
        user = self.get_or_create_user(provider, access, info)
        access.user = user
        AccountAccess.objects.filter(pk=access.pk).update(user=user)
        user = authenticate(provider=access.provider, identifier=access.identifier)
        login(self.request, user)
        return redirect(self.get_login_redirect(provider, user, access, True))
