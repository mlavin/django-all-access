from __future__ import unicode_literals

from urllib import urlencode
from urlparse import parse_qs

from django.core.urlresolvers import reverse

import requests
from requests.auth import OAuth1
from requests.exceptions import RequestException


class BaseOAuthClient(object):
    
    def __init__(self, provider):
        self.provider = provider

    def get_access_token(self, request):
        "Fetch access token from callback request."
        raise NotImplementedError('Defined in a sub-class') # pragma: no cover

    def get_callback_url(self, request):
        "Construct the callback url for a given provider."
        callback = reverse('allaccess-callback', kwargs={'service': self.provider.name})
        return request.build_absolute_uri(callback)

    def get_profile_info(self, raw_token):
        "Fetch user profile information."
        raise NotImplementedError('Defined in a sub-class') # pragma: no cover

    def get_redirect_args(self, request):
        "Get request parameters for redirect url."
        raise NotImplementedError('Defined in a sub-class') # pragma: no cover

    def get_redirect_url(self, request):
        "Build authentication redirect url."
        args = self.get_redirect_args(request)
        params = urlencode(args)
        return '{0}?{1}'.format(self.provider.authorization_url, params)

    def parse_raw_token(self, raw_token):
        "Parse token and secret from raw token response."
        raise NotImplementedError('Defined in a sub-class') # pragma: no cover


class OAuthClient(BaseOAuthClient):

    def get_access_token(self, request):
        "Fetch access token from callback request."
        raw_token = request.session.get(self.session_key, '')
        request_token, request_secret = self.parse_raw_token(raw_token)
        if request_token is not None and request_secret is not None:
            oauth_verifier = request.GET.get('oauth_verifier', '')
            oauth = OAuth1(
                resource_owner_key=request_token,
                resource_owner_secret=request_secret,
                client_key=self.provider.key,
                client_secret=self.provider.secret,
                verifier=oauth_verifier,
            )
            try:
                response = requests.post(
                    self.provider.access_token_url,
                    {'oauth_verifier': oauth_verifier},
                    auth=oauth
                )
            except RequestException:
                # TODO: Logging
                return None
            else:
                return response.text
        return None

    def get_profile_info(self, raw_token):
        "Fetch user profile information."
        token, secret = self.parse_raw_token(raw_token)
        oauth = OAuth1(
            resource_owner_key=token,
            resource_owner_secret=secret,
            client_key=self.provider.key,
            client_secret=self.provider.secret,
        )
        try:
            response = requests.get(self.provider.profile_url, auth=oauth)
        except RequestException:
            # TODO: Logging
            return None
        else:
            return response.json

    def get_request_token(self, request):
        "Fetch the OAuth request token. Only required for OAuth 1.0."
        oauth = OAuth1(client_key=self.provider.key, client_secret=self.provider.secret)
        # TODO: requests supresses HttpErrors but we may want to log them
        try:
            response = requests.post(url=self.provider.request_token_url, auth=oauth)
        except RequestException:
            # TODO: Logging
            raw_token = ''
        else:
            raw_token = response.text
            # Store token in the session for callback
            request.session[self.session_key] = raw_token
        return self.parse_raw_token(raw_token)

    def get_redirect_args(self, request):
        "Get request parameters for redirect url."
        token, _ = self.get_request_token(request)
        callback = self.get_callback_url(request)
        return {
            'oauth_token': token,
            'callback_url': callback,
        }

    def parse_raw_token(self, raw_token):
        "Parse token and secret from raw token response."
        qs = parse_qs(raw_token)
        token = qs.get('oauth_token', [None])[0]
        secret = qs.get('oauth_token_secret', [None])[0]
        return (token, secret)

    @property
    def session_key(self):
        return 'allaccess-{0}-request-token'.format(self.provider.name)


class OAuth2Client(BaseOAuthClient):

    def get_access_token(self, request):
        "Fetch access token from callback request."
        callback = self.get_callback_url(request)
        args = {
            'client_id': self.provider.key,
            'redirect_uri': callback,
            'client_secret': self.provider.secret,
            'code': request.GET.get('code', '')
        }
        try:
            response = requests.get(self.provider.access_token_url, params=args)
        except RequestException:
            # TODO: Logging
            return None
        else:
            return response.text

    def get_redirect_args(self, request):
        "Get request parameters for redirect url."
        callback = self.get_callback_url(request)
        return {
            'client_id': self.provider.key,
            'redirect_uri': callback,
            'response_type': 'code',
        }

    def parse_raw_token(self, raw_token):
        "Parse token and secret from raw token response."
        qs = parse_qs(raw_token)
        token = qs['access_token'][0]
        return (token, None)


def get_client(provider):
    "Return the API client for the given provider."
    cls = OAuth2Client
    if provider.request_token_url:
        cls = OAuthClient
    return cls(provider)
