from __future__ import unicode_literals

import base64
import hashlib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils import simplejson as json
from django.views.generic import RedirectView, View

from .clients import get_client
from .models import Provider, AccountAccess


class OAuthRedirect(RedirectView):
    "Redirect user to service to enable access."

    permanent = False  
        
    def get_redirect_url(self, **kwargs):
        "Build redirect url for a given provider."
        service = kwargs.get('service', '')
        try:
            provider = Provider.objects.filter(
                key__isnull=False, secret__isnull=False
            ).get(name=service)
        except Provider.DoesNotExist:
            raise Http404('Unknown OAuth provider.')
        else:
            client = get_client(provider)
            return client.get_redirect_url(self.request)


class OAuthCallback(View):
    "Base OAuth callback view."
        
    def get(self, request, *args, **kwargs):
        service = kwargs.get('service', '')
        try:
            provider = Provider.objects.filter(
                key__isnull=False, secret__isnull=False
            ).get(name=service)
        except Provider.DoesNotExist:
            raise Http404('Unknown OAuth provider.')
        else:
            client = get_client(provider)
            # Fetch access token
            raw_token = client.get_access_token(self.request)
            if raw_token is None:
                return self.handle_login_failure(provider, "Could not retrive token.")
            # Fetch profile info
            info = client.get_profile_info(raw_token)
            if info is None:
                return self.handle_login_failure(provider, "Could not retrive profile.")
            identifier = self.get_user_id(provider, info)
            if identifier is None:
                return self.handle_login_failure(provider, "Could not determine id.")
            # Get or create access record
            defaults = {
                'access_token': raw_token,
                'raw_data': json.dumps(info),
            }
            access, created = AccountAccess.objects.get_or_create(
                service=provider, identifier=identifier, defaults=defaults
            )
            if not created:
                for field, value in defaults.items():
                    setattr(access, field, value)
                AccountAccess.objects.filter(pk=access.pk).update(**defaults)
            user = authenticate(service=provider, identifier=identifier)
            if user is None:
                return self.handle_new_user(provider, access)
            else:
                return self.handle_existing_user(provider, user, access)

    def get_error_redirect(self, provider, reason):
        "Return url to redirect on login failure."
        return settings.LOGIN_URL

    def get_login_redirect(self, provider, user, access, new=False):
        "Return url to redirect authenticated users."
        return settings.LOGIN_REDIRECT_URL

    def get_user_id(self, provider, info):
        "Return unique identifier from the profile info."        
        return info.get('id')

    def handle_existing_user(self, provider, user, access):
        "Login user and redirect."
        login(self.request, user)
        return redirect(self.get_login_redirect(provider, user, access))

    def handle_login_failure(self, provider, reason):
        "Message user and redirect on error."
        messages.error(self.request, 'Authenication Failed.')
        return redirect(self.get_error_redirect(provider, reason))

    def handle_new_user(self, provider, access):
        "Create a shell auth.User and redirect."
        digest = hashlib.sha1(str(access)).digest()
        # Base 64 encode to get below 30 characters
        # Removed padding characters
        username = base64.urlsafe_b64encode(digest).replace('=', '')
        user = User.objects.create_user(username)
        access.user = user
        AccountAccess.objects.filter(pk=access.pk).update(user=user)
        user = authenticate(service=access.service, identifier=access.identifier)
        login(self.request, user)
        return redirect(self.get_login_redirect(provider, user, access, True))
