"OAuth 1.0 and 2.0 client tests."
from __future__ import unicode_literals

from django.test.client import RequestFactory

from requests.exceptions import RequestException

from .base import AllAccessTestCase
from ..clients import OAuthClient, OAuth2Client
from ..compat import urlparse, parse_qs, patch, Mock


class BaseClientTestCase(object):
    "Common client test functionality."

    oauth_client = None

    def setUp(self):
        super(BaseClientTestCase, self).setUp()
        self.consumer_key = self.get_random_string()
        self.consumer_secret = self.get_random_string()
        self.provider = self.create_provider(
            consumer_key=self.consumer_key, consumer_secret=self.consumer_secret)
        self.oauth = self.oauth_client(self.provider)
        self.factory = RequestFactory()

    def test_redirect_url(self, *args, **kwargs):
        "Redirect url is build from provider authorization_url."
        with patch.object(self.oauth, 'get_redirect_args') as args:
            args.return_value = {'foo': 'bar'}
            request = self.factory.get('/login/')
            url = self.oauth.get_redirect_url(request, callback='/callback/')
            scheme, netloc, path, params, query, fragment = urlparse(url)
            query = parse_qs(query)
            self.assertEqual('%s://%s%s' % (scheme, netloc, path), self.provider.authorization_url)
            self.assertEqual(query, {'foo': ['bar']})

    def test_additional_redirect_args(self, *args, **kwargs):
        "Additional redirect arguments."
        with patch.object(self.oauth, 'get_redirect_args') as args:
            args.return_value = {'foo': 'bar'}
            request = self.factory.get('/login/')
            additional = {'scope': 'email'}
            url = self.oauth.get_redirect_url(request, callback='/callback/', parameters=additional)
            scheme, netloc, path, params, query, fragment = urlparse(url)
            query = parse_qs(query)
            self.assertEqual(query, {'foo': ['bar'], 'scope': ['email']})


@patch('allaccess.clients.OAuth1')
@patch('allaccess.clients.request')
class OAuthClientTestCase(BaseClientTestCase, AllAccessTestCase):
    "OAuth 1.0 client handling to match http://oauth.net/core/1.0/"

    oauth_client = OAuthClient

    def setUp(self):
        super(OAuthClientTestCase, self).setUp()
        self.provider.request_token_url = self.get_random_url()
        self.provider.save()

    def test_request_token_auth(self, requests, auth):
        "Construct post auth with provider key and secret."
        request = self.factory.get('/login/')
        self.oauth.get_request_token(request, callback='/callback/')
        self.assertTrue(auth.called)
        args, kwargs = auth.call_args
        self.assertEqual(kwargs['client_key'], self.provider.consumer_key)
        self.assertEqual(kwargs['client_secret'], self.provider.consumer_secret)
        self.assertEqual(kwargs['resource_owner_key'], None)
        self.assertEqual(kwargs['resource_owner_secret'], None)
        self.assertEqual(kwargs['verifier'], None)
        self.assertEqual(kwargs['callback_uri'], 'http://testserver/callback/')

    def test_request_token_url(self, requests, auth):
        "Post should be sent to provider's request_token_url."
        request = self.factory.get('/login/')
        self.oauth.get_request_token(request, callback='/callback/')
        self.assertTrue(requests.called)
        args, kwargs = requests.call_args
        method, url = args
        self.assertEqual(method, 'post')
        self.assertEqual(url, self.provider.request_token_url)

    def test_request_token_response(self, requests, auth):
        "Return full response text without parsing key/secret."
        response = Mock()
        response.text = 'oauth_token=token&oauth_token_secret=secret'
        requests.return_value = response
        request = self.factory.get('/login/')
        token = self.oauth.get_request_token(request, callback='/callback/')
        self.assertEqual(token, 'oauth_token=token&oauth_token_secret=secret')

    def test_request_token_failure(self, requests, auth):
        "Handle upstream server errors when fetching request token."
        requests.side_effect = RequestException('Server Down')
        request = self.factory.get('/login/')
        token = self.oauth.get_request_token(request, callback='/callback/')
        self.assertEqual(token, None)

    def test_access_token_auth(self, requests, auth):
        "Construct auth from provider key and secret and request token."
        request = self.factory.get('/callback/', {'oauth_verifier': 'verifier'})
        request.session = {self.oauth.session_key: 'oauth_token=token&oauth_token_secret=secret'}
        self.oauth.get_access_token(request)
        self.assertTrue(auth.called)
        args, kwargs = auth.call_args
        self.assertEqual(kwargs['client_key'], self.provider.consumer_key)
        self.assertEqual(kwargs['client_secret'], self.provider.consumer_secret)
        self.assertEqual(kwargs['resource_owner_key'], 'token')
        self.assertEqual(kwargs['resource_owner_secret'], 'secret')
        self.assertEqual(kwargs['verifier'], 'verifier')
        self.assertEqual(kwargs['callback_uri'], 'http://testserver/callback/')

    def test_access_token_auth_custom_callback(self, requests, auth):
        "Construct auth when a callback is given."
        request = self.factory.get('/callback/', {'oauth_verifier': 'verifier'})
        request.session = {self.oauth.session_key: 'oauth_token=token&oauth_token_secret=secret'}
        self.oauth.get_access_token(request, callback='/other/')
        self.assertTrue(auth.called)
        args, kwargs = auth.call_args
        self.assertEqual(kwargs['client_key'], self.provider.consumer_key)
        self.assertEqual(kwargs['client_secret'], self.provider.consumer_secret)
        self.assertEqual(kwargs['resource_owner_key'], 'token')
        self.assertEqual(kwargs['resource_owner_secret'], 'secret')
        self.assertEqual(kwargs['verifier'], 'verifier')
        self.assertEqual(kwargs['callback_uri'], 'http://testserver/other/')

    def test_access_token_no_request_token(self, requests, auth):
        "Handle no request token found in the session."
        request = self.factory.get('/callback/', {'oauth_verifier': 'verifier'})
        request.session = {}
        response = self.oauth.get_access_token(request)
        self.assertEqual(response, None)
        self.assertFalse(requests.called)
        self.assertFalse(auth.called)

    def test_access_token_no_verifier(self, requests, auth):
        "Don't request access token if no verifier was given."
        request = self.factory.get('/callback/')
        request.session = {self.oauth.session_key: 'oauth_token=token&oauth_token_secret=secret'}
        response = self.oauth.get_access_token(request)
        self.assertEqual(response, None)
        self.assertFalse(requests.called)
        self.assertFalse(auth.called)

    def test_access_token_bad_request_token(self, requests, auth):
        "Handle bad request token found in the session."
        request = self.factory.get('/callback/', {'oauth_verifier': 'verifier'})
        request.session = {self.oauth.session_key: 'XXXXX'}
        self.oauth.get_access_token(request)
        self.assertTrue(auth.called)
        args, kwargs = auth.call_args
        self.assertEqual(kwargs['client_key'], self.provider.consumer_key)
        self.assertEqual(kwargs['client_secret'], self.provider.consumer_secret)
        self.assertEqual(kwargs['resource_owner_key'], None)
        self.assertEqual(kwargs['resource_owner_secret'], None)
        self.assertEqual(kwargs['verifier'], 'verifier')

    def test_access_token_url(self, requests, auth):
        "Post should be sent to provider's access_token_url."
        request = self.factory.get('/callback/', {'oauth_verifier': 'verifier'})
        request.session = {self.oauth.session_key: 'oauth_token=token&oauth_token_secret=secret'}
        self.oauth.get_access_token(request)
        self.assertTrue(requests.called)
        args, kwargs = requests.call_args
        method, url = args
        self.assertEqual(method, 'post')
        self.assertEqual(url, self.provider.access_token_url)

    def test_access_token_response(self, requests, auth):
        "Return full response text without parsing key/secret."
        response = Mock()
        response.text = 'oauth_token=token&oauth_token_secret=secret'
        requests.return_value = response
        request = self.factory.get('/callback/', {'oauth_verifier': 'verifier'})
        request.session = {self.oauth.session_key: 'oauth_token=token&oauth_token_secret=secret'}
        token = self.oauth.get_access_token(request)
        self.assertEqual(token, 'oauth_token=token&oauth_token_secret=secret')

    def test_access_token_failure(self, requests, auth):
        "Handle upstream server errors when fetching access token."
        requests.side_effect = RequestException('Server Down')
        request = self.factory.get('/callback/', {'oauth_verifier': 'verifier'})
        request.session = {self.oauth.session_key: 'oauth_token=token&oauth_token_secret=secret'}
        token = self.oauth.get_access_token(request)
        self.assertEqual(token, None)

    def test_profile_info_auth(self, requests, auth):
        "Construct auth from provider key and secret and user token."
        raw_token = 'oauth_token=token&oauth_token_secret=secret'
        self.oauth.get_profile_info(raw_token)
        self.assertTrue(auth.called)
        args, kwargs = auth.call_args
        self.assertEqual(kwargs['client_key'], self.provider.consumer_key)
        self.assertEqual(kwargs['client_secret'], self.provider.consumer_secret)
        self.assertEqual(kwargs['resource_owner_key'], 'token')
        self.assertEqual(kwargs['resource_owner_secret'], 'secret')

    def test_profile_info_url(self, requests, auth):
        "Make get request for profile url."
        raw_token = 'oauth_token=token&oauth_token_secret=secret'
        self.oauth.get_profile_info(raw_token)
        self.assertTrue(requests.called)
        args, kwargs = requests.call_args
        method, url = args
        self.assertEqual(method, 'get')
        self.assertEqual(url, self.provider.profile_url)

    def test_profile_info_failure(self, requests, auth):
        "Handle upstream server errors when fetching profile info."
        requests.side_effect = RequestException('Server Down')
        raw_token = 'oauth_token=token&oauth_token_secret=secret'
        response = self.oauth.get_profile_info(raw_token)
        self.assertEqual(response, None)

    def test_request_with_user_token(self, requests, auth):
        "Use token for request auth."
        token = 'oauth_token=token&oauth_token_secret=secret'
        self.oauth = self.oauth_client(self.provider, token=token)
        self.oauth.request('get', 'http://example.com/')
        self.assertTrue(auth.called)
        args, kwargs = auth.call_args
        self.assertEqual(kwargs['client_key'], self.provider.consumer_key)
        self.assertEqual(kwargs['client_secret'], self.provider.consumer_secret)
        self.assertEqual(kwargs['resource_owner_key'], 'token')
        self.assertEqual(kwargs['resource_owner_secret'], 'secret')


@patch('allaccess.clients.request')
class OAuth2ClientTestCase(BaseClientTestCase, AllAccessTestCase):
    "OAuth 2.0 client handling."

    oauth_client = OAuth2Client

    def test_access_token_url(self, requests):
        "Get should be sent to provider's access_token_url."
        request = self.factory.get('/callback/', {'code': 'code', 'state': 'foo'})
        request.session = {self.oauth.session_key: 'foo'}
        self.oauth.get_access_token(request)
        self.assertTrue(requests.called)
        args, kwargs = requests.call_args
        method, url = args
        self.assertEqual(method, 'post')
        self.assertEqual(url, self.provider.access_token_url)

    def test_access_token_parameters(self, requests):
        "Check parameters used when fetching access token."
        request = self.factory.get('/callback/', {'code': 'code', 'state': 'foo'})
        request.session = {self.oauth.session_key: 'foo'}
        self.oauth.get_access_token(request)
        self.assertTrue(requests.called)
        args, kwargs = requests.call_args
        params = kwargs['data']
        self.assertEqual(params['redirect_uri'], 'http://testserver/callback/')
        self.assertEqual(params['code'], 'code')
        self.assertEqual(params['grant_type'], 'authorization_code')
        self.assertEqual(params['client_id'], self.provider.consumer_key)
        self.assertEqual(params['client_secret'], self.provider.consumer_secret)

    def test_access_token_custom_callback(self, requests):
        "Check parameters used with custom callback."
        request = self.factory.get('/callback/', {'code': 'code', 'state': 'foo'})
        request.session = {self.oauth.session_key: 'foo'}
        self.oauth.get_access_token(request, callback='/other/')
        self.assertTrue(requests.called)
        args, kwargs = requests.call_args
        params = kwargs['data']
        self.assertEqual(params['redirect_uri'], 'http://testserver/other/')
        self.assertEqual(params['code'], 'code')
        self.assertEqual(params['grant_type'], 'authorization_code')
        self.assertEqual(params['client_id'], self.provider.consumer_key)
        self.assertEqual(params['client_secret'], self.provider.consumer_secret)

    def test_access_token_no_code(self, requests):
        "Don't request token if no code was given to the callback."
        request = self.factory.get('/callback/', {'state': 'foo'})
        request.session = {self.oauth.session_key: 'foo'}
        token = self.oauth.get_access_token(request)
        self.assertEqual(token, None)
        self.assertFalse(requests.called)

    def test_access_token_response(self, requests):
        "Return full response text without parsing key/secret."
        response = Mock()
        response.text = 'access_token=USER_ACESS_TOKEN'
        requests.return_value = response
        request = self.factory.get('/callback/', {'code': 'code', 'state': 'foo'})
        request.session = {self.oauth.session_key: 'foo'}
        token = self.oauth.get_access_token(request)
        self.assertEqual(token, 'access_token=USER_ACESS_TOKEN')

    def test_access_token_failure(self, requests):
        "Handle upstream server errors when fetching access token."
        requests.side_effect = RequestException('Server Down')
        request = self.factory.get('/callback/', {'code': 'code', 'state': 'foo'})
        request.session = {self.oauth.session_key: 'foo'}
        token = self.oauth.get_access_token(request)
        self.assertEqual(token, None)

    def test_profile_info_auth(self, requests):
        "Pass access token when requesting profile info."
        raw_token = 'access_token=USER_ACESS_TOKEN'
        self.oauth.get_profile_info(raw_token)
        self.assertTrue(requests.called)
        args, kwargs = requests.call_args
        self.assertEqual(kwargs['params']['access_token'], 'USER_ACESS_TOKEN')

    def test_profile_info_url(self, requests):
        "Make get request for profile url."
        raw_token = 'access_token=USER_ACESS_TOKEN'
        self.oauth.get_profile_info(raw_token)
        self.assertTrue(requests.called)
        args, kwargs = requests.call_args
        method, url = args
        self.assertEqual(method, 'get')
        self.assertEqual(url, self.provider.profile_url)

    def test_profile_info_failure(self, requests):
        "Handle upstream server errors when fetching profile info."
        requests.side_effect = RequestException('Server Down')
        raw_token = 'access_token=USER_ACESS_TOKEN'
        response = self.oauth.get_profile_info(raw_token)
        self.assertEqual(response, None)

    def test_parse_token_response_json(self, requests):
        "Parse token response which is JSON encoded per spec."
        raw_token = '{"access_token": "USER_ACESS_TOKEN"}'
        token, secret = self.oauth.parse_raw_token(raw_token)
        self.assertEqual(token, 'USER_ACESS_TOKEN')
        self.assertEqual(secret, None)

    def test_parse_error_response_json(self, requests):
        "Parse token error response which is JSON encoded per spec."
        raw_token = '{"error": "invalid_request"}'
        token, secret = self.oauth.parse_raw_token(raw_token)
        self.assertEqual(token, None)
        self.assertEqual(secret, None)

    def test_parse_token_response_query(self, requests):
        "Parse token response which is url encoded (FB)."
        raw_token = 'access_token=USER_ACESS_TOKEN'
        token, secret = self.oauth.parse_raw_token(raw_token)
        self.assertEqual(token, 'USER_ACESS_TOKEN')
        self.assertEqual(secret, None)

    def test_parse_invalid_token_response(self, requests):
        "Parse garbage token response."
        raw_token = 'XXXXX'
        token, secret = self.oauth.parse_raw_token(raw_token)
        self.assertEqual(token, None)
        self.assertEqual(secret, None)

    def test_access_token_no_state_session(self, requests):
        "Handle no state found in the session."
        request = self.factory.get('/callback/', {'code': 'code', 'state': 'foo'})
        request.session = {}
        response = self.oauth.get_access_token(request)
        self.assertEqual(response, None)
        self.assertFalse(requests.called)

    def test_access_token_no_state_provider(self, requests):
        "Handle no state returned by the provider."
        request = self.factory.get('/callback/', {'code': 'code'})
        request.session = {self.oauth.session_key: 'foo'}
        response = self.oauth.get_access_token(request)
        self.assertEqual(response, None)
        self.assertFalse(requests.called)

    def test_access_token_state_incorrect(self, requests):
        "Handle invalid state returned by the provider"
        request = self.factory.get('/callback/', {'code': 'code', 'state': 'bar'})
        request.session = {self.oauth.session_key: 'foo'}
        response = self.oauth.get_access_token(request)
        self.assertEqual(response, None)
        self.assertFalse(requests.called)

    def test_request_with_user_token(self, requests):
        "Use token for request auth."
        token = '{"access_token": "USER_ACESS_TOKEN"}'
        self.oauth = self.oauth_client(self.provider, token=token)
        self.oauth.request('get', 'http://example.com/')
        self.assertTrue(requests.called)
        args, kwargs = requests.call_args
        self.assertEqual(kwargs['params']['access_token'], 'USER_ACESS_TOKEN')
