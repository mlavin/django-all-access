from __future__ import unicode_literals

from urllib import urlencode
from urlparse import parse_qs

from django.core.urlresolvers import reverse
from django.utils.encoding import force_unicode

from requests.api import request
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
        callback = reverse('allaccess-callback', kwargs={'provider': self.provider.name})
        return force_unicode(request.build_absolute_uri(callback))

    def get_profile_info(self, raw_token):
        "Fetch user profile information."
        try:
            response = self.request('get', self.provider.profile_url, token=raw_token)
        except RequestException:
            # TODO: Logging
            return None
        else:
            return response.json if response.json is not None else response.text

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

    def request(self, method, url, **kwargs):
        "Build remote url request."
        return request(method, url, **kwargs)


class OAuthClient(BaseOAuthClient):

    def get_access_token(self, request):
        "Fetch access token from callback request."
        raw_token = request.session.get(self.session_key, '')
        if raw_token:
            data = {'oauth_verifier': request.GET.get('oauth_verifier', '')}
            callback = self.get_callback_url(request)
            try:
                response = self.request('post', self.provider.access_token_url, 
                                        token=raw_token, data=data, oauth_callback=callback)
            except RequestException:
                # TODO: Logging
                return None
            else:
                return response.text
        return None

    def get_request_token(self, request):
        "Fetch the OAuth request token. Only required for OAuth 1.0."
        callback = self.get_callback_url(request)
        try:
            response = self.request('post', self.provider.request_token_url, oauth_callback=callback)
        except RequestException:
            # TODO: Logging
            return None
        else:
            return response.text

    def get_redirect_args(self, request):
        "Get request parameters for redirect url."
        raw_token = self.get_request_token(request)
        token, secret = self.parse_raw_token(raw_token)
        if token is not None and secret is not None:
            request.session[self.session_key] = raw_token
        callback = self.get_callback_url(request)
        return {
            'oauth_token': token,
            'oauth_callback': callback,
        }

    def parse_raw_token(self, raw_token):
        "Parse token and secret from raw token response."
        qs = parse_qs(raw_token)
        token = qs.get('oauth_token', [None])[0]
        secret = qs.get('oauth_token_secret', [None])[0]
        return (token, secret)

    def request(self, method, url, **kwargs):
        "Build remote url request. Constructs necessary auth."
        user_token = kwargs.pop('token', '')
        token, secret = self.parse_raw_token(user_token)
        callback = kwargs.pop('oauth_callback', None)
        verifier = kwargs.get('data', {}).get('oauth_verifier')
        oauth = OAuth1(
            resource_owner_key=token,
            resource_owner_secret=secret,
            client_key=self.provider.key,
            client_secret=self.provider.secret,
            verifier=verifier,
            callback_uri=callback,
        )
        kwargs['auth'] = oauth
        return super(OAuthClient, self).request(method, url, **kwargs)

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
            response = self.request('get', self.provider.access_token_url, params=args)
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
        token = qs.get('access_token', [None])[0]
        return (token, None)

    def request(self, method, url, **kwargs):
        "Build remote url request. Constructs necessary auth."
        user_token = kwargs.pop('token', '')
        token, _ = self.parse_raw_token(user_token)
        if token is not None:
            params = kwargs.get('params', {})
            params['access_token'] = token
            kwargs['params'] = params
        return super(OAuth2Client, self).request(method, url, **kwargs)


def get_client(provider):
    "Return the API client for the given provider."
    cls = OAuth2Client
    if provider.request_token_url:
        cls = OAuthClient
    return cls(provider)
