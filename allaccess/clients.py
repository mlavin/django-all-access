from __future__ import unicode_literals

import json
import logging

from django.utils.crypto import constant_time_compare, get_random_string
from django.utils.encoding import force_text

from requests.api import request
from requests_oauthlib import OAuth1
from requests.exceptions import RequestException

from .compat import urlencode, parse_qs


logger = logging.getLogger('allaccess.clients')


class BaseOAuthClient(object):

    def __init__(self, provider, token=''):
        self.provider = provider
        self.token = token

    def get_access_token(self, request, callback=None):
        "Fetch access token from callback request."
        raise NotImplementedError('Defined in a sub-class')  # pragma: no cover

    def get_profile_info(self, raw_token):
        "Fetch user profile information."
        try:
            response = self.request('get', self.provider.profile_url, token=raw_token)
            response.raise_for_status()
        except RequestException as e:
            logger.error('Unable to fetch user profile: {0}'.format(e))
            return None
        else:
            return response.json() or response.text

    def get_redirect_args(self, request, callback):
        "Get request parameters for redirect url."
        raise NotImplementedError('Defined in a sub-class')  # pragma: no cover

    def get_redirect_url(self, request, callback, parameters=None):
        "Build authentication redirect url."
        args = self.get_redirect_args(request, callback=callback)
        additional = parameters or {}
        args.update(additional)
        params = urlencode(args)
        return '{0}?{1}'.format(self.provider.authorization_url, params)

    def parse_raw_token(self, raw_token):
        "Parse token and secret from raw token response."
        raise NotImplementedError('Defined in a sub-class')  # pragma: no cover

    def request(self, method, url, **kwargs):
        "Build remote url request."
        return request(method, url, **kwargs)

    @property
    def session_key(self):
        raise NotImplementedError('Defined in a sub-class')  # pragma: no cover


class OAuthClient(BaseOAuthClient):

    def get_access_token(self, request, callback=None):
        "Fetch access token from callback request."
        raw_token = request.session.get(self.session_key, None)
        verifier = request.GET.get('oauth_verifier', None)
        if raw_token is not None and verifier is not None:
            data = {'oauth_verifier': verifier}
            callback = request.build_absolute_uri(callback or request.path)
            callback = force_text(callback)
            try:
                response = self.request('post', self.provider.access_token_url,
                                        token=raw_token, data=data, oauth_callback=callback)
                response.raise_for_status()
            except RequestException as e:
                logger.error('Unable to fetch access token: {0}'.format(e))
                return None
            else:
                return response.text
        return None

    def get_request_token(self, request, callback):
        "Fetch the OAuth request token. Only required for OAuth 1.0."
        callback = force_text(request.build_absolute_uri(callback))
        try:
            response = self.request(
                'post', self.provider.request_token_url, oauth_callback=callback)
            response.raise_for_status()
        except RequestException as e:
            logger.error('Unable to fetch request token: {0}'.format(e))
            return None
        else:
            return response.text

    def get_redirect_args(self, request, callback):
        "Get request parameters for redirect url."
        callback = force_text(request.build_absolute_uri(callback))
        raw_token = self.get_request_token(request, callback)
        token, secret = self.parse_raw_token(raw_token)
        if token is not None and secret is not None:
            request.session[self.session_key] = raw_token
        return {
            'oauth_token': token,
            'oauth_callback': callback,
        }

    def parse_raw_token(self, raw_token):
        "Parse token and secret from raw token response."
        if raw_token is None:
            return (None, None)
        qs = parse_qs(raw_token)
        token = qs.get('oauth_token', [None])[0]
        secret = qs.get('oauth_token_secret', [None])[0]
        return (token, secret)

    def request(self, method, url, **kwargs):
        "Build remote url request. Constructs necessary auth."
        user_token = kwargs.pop('token', self.token)
        token, secret = self.parse_raw_token(user_token)
        callback = kwargs.pop('oauth_callback', None)
        verifier = kwargs.get('data', {}).pop('oauth_verifier', None)
        oauth = OAuth1(
            resource_owner_key=token,
            resource_owner_secret=secret,
            client_key=self.provider.consumer_key,
            client_secret=self.provider.consumer_secret,
            verifier=verifier,
            callback_uri=callback,
        )
        kwargs['auth'] = oauth
        return super(OAuthClient, self).request(method, url, **kwargs)

    @property
    def session_key(self):
        return 'allaccess-{0}-request-token'.format(self.provider.name)


class OAuth2Client(BaseOAuthClient):

    def check_application_state(self, request, callback):
        "Check optional state parameter."
        stored = request.session.get(self.session_key, None)
        returned = request.GET.get('state', None)
        check = False
        if stored is not None:
            if returned is not None:
                check = constant_time_compare(stored, returned)
            else:
                logger.error('No state parameter returned by the provider.')
        else:
            logger.error('No state stored in the sesssion.')
        return check

    def get_access_token(self, request, callback=None):
        "Fetch access token from callback request."
        callback = request.build_absolute_uri(callback or request.path)
        if not self.check_application_state(request, callback):
            logger.error('Application state check failed.')
            return None
        if 'code' in request.GET:
            args = {
                'client_id': self.provider.consumer_key,
                'redirect_uri': callback,
                'client_secret': self.provider.consumer_secret,
                'code': request.GET['code'],
                'grant_type': 'authorization_code',
            }
        else:
            logger.error('No code returned by the provider')
            return None
        try:
            response = self.request('post', self.provider.access_token_url, data=args)
            response.raise_for_status()
        except RequestException as e:
            logger.error('Unable to fetch access token: {0}'.format(e))
            return None
        else:
            return response.text

    def get_application_state(self, request, callback):
        "Generate state optional parameter."
        return get_random_string(32)

    def get_redirect_args(self, request, callback):
        "Get request parameters for redirect url."
        callback = request.build_absolute_uri(callback)
        args = {
            'client_id': self.provider.consumer_key,
            'redirect_uri': callback,
            'response_type': 'code',
        }
        state = self.get_application_state(request, callback)
        if state is not None:
            args['state'] = state
            request.session[self.session_key] = state
        return args

    def parse_raw_token(self, raw_token):
        "Parse token and secret from raw token response."
        if raw_token is None:
            return (None, None)
        # Load as json first then parse as query string
        try:
            token_data = json.loads(raw_token)
        except ValueError:
            qs = parse_qs(raw_token)
            token = qs.get('access_token', [None])[0]
        else:
            token = token_data.get('access_token', None)
        return (token, None)

    def request(self, method, url, **kwargs):
        "Build remote url request. Constructs necessary auth."
        user_token = kwargs.pop('token', self.token)
        token, _ = self.parse_raw_token(user_token)
        if token is not None:
            params = kwargs.get('params', {})
            params['access_token'] = token
            kwargs['params'] = params
        return super(OAuth2Client, self).request(method, url, **kwargs)

    @property
    def session_key(self):
        return 'allaccess-{0}-request-state'.format(self.provider.name)


def get_client(provider, token=''):
    "Return the API client for the given provider."
    cls = OAuth2Client
    if provider.request_token_url:
        cls = OAuthClient
    return cls(provider, token)
