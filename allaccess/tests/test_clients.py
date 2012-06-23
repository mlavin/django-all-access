"OAuth 1.0 and 2.0 client tests."
from __future__ import unicode_literals

from django.test.client import RequestFactory

from mock import patch, MagicMock, Mock
from requests.exceptions import RequestException

from .base import AllAccessTestCase
from allaccess.clients import OAuthClient, OAuth2Client


class BaseClientTestCase(AllAccessTestCase):
    "Common client test functionality."

    oauth_client = None

    def setUp(self):
        self.key = self.get_random_string()
        self.secret = self.get_random_string()
        self.provider = self.create_provider(key=self.key, secret=self.secret)
        self.oauth = self.oauth_client(self.provider)
        self.factory = RequestFactory()

    def test_redirect_url(self, *args, **kwargs):
        "Redirect url is build from provider authorization_url."
        with patch.object(self.oauth, 'get_redirect_args') as args:
            args.return_value = {'foo': 'bar'}
            request = MagicMock()
            url = self.oauth.get_redirect_url(request, callback='/callback/')
            expected = self.provider.authorization_url + '?foo=bar'
            self.assertEqual(url, expected)


@patch('allaccess.clients.OAuth1')
@patch('allaccess.clients.request')
class OAuthClientTestCase(BaseClientTestCase):
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
        self.assertEqual(kwargs['client_key'], self.provider.key)
        self.assertEqual(kwargs['client_secret'], self.provider.secret)
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
        request = MagicMock()
        request.session = {self.oauth.session_key: 'oauth_token=token&oauth_token_secret=secret'}
        request.GET = {'oauth_verifier': 'verifier'}
        self.oauth.get_access_token(request)
        self.assertTrue(auth.called)
        args, kwargs = auth.call_args
        self.assertEqual(kwargs['client_key'], self.provider.key)
        self.assertEqual(kwargs['client_secret'], self.provider.secret)
        self.assertEqual(kwargs['resource_owner_key'], 'token')
        self.assertEqual(kwargs['resource_owner_secret'], 'secret')
        self.assertEqual(kwargs['verifier'], 'verifier')

    def test_access_token_no_request_token(self, requests, auth):
        "Handle no request token found in the session."
        request = MagicMock()
        request.session = {}
        request.GET = {'oauth_verifier': 'verifier'}
        response = self.oauth.get_access_token(request)
        self.assertEqual(response, None)
        self.assertFalse(requests.called)
        self.assertFalse(auth.called)

    def test_access_token_bad_request_token(self, requests, auth):
        "Handle bad request token found in the session."
        request = MagicMock()
        request.session = {self.oauth.session_key: 'XXXXX'}
        request.GET = {'oauth_verifier': 'verifier'}
        self.oauth.get_access_token(request)
        self.assertTrue(auth.called)
        args, kwargs = auth.call_args
        self.assertEqual(kwargs['client_key'], self.provider.key)
        self.assertEqual(kwargs['client_secret'], self.provider.secret)
        self.assertEqual(kwargs['resource_owner_key'], None)
        self.assertEqual(kwargs['resource_owner_secret'], None)
        self.assertEqual(kwargs['verifier'], 'verifier')

    def test_access_token_url(self, requests, auth):
        "Post should be sent to provider's access_token_url."
        request = MagicMock()
        request.session = {self.oauth.session_key: 'oauth_token=token&oauth_token_secret=secret'}
        request.GET = {'oauth_verifier': 'verifier'}
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
        request = MagicMock()
        request.session = {self.oauth.session_key: 'oauth_token=token&oauth_token_secret=secret'}
        request.GET = {'oauth_verifier': 'verifier'}
        token = self.oauth.get_access_token(request)
        self.assertEqual(token, 'oauth_token=token&oauth_token_secret=secret')

    def test_access_token_failure(self, requests, auth):
        "Handle upstream server errors when fetching access token."
        requests.side_effect = RequestException('Server Down')
        request = MagicMock()
        request.session = {self.oauth.session_key: 'oauth_token=token&oauth_token_secret=secret'}
        request.GET = {'oauth_verifier': 'verifier'}
        token = self.oauth.get_access_token(request)
        self.assertEqual(token, None)

    def test_profile_info_auth(self, requests, auth):
        "Construct auth from provider key and secret and user token."
        raw_token = 'oauth_token=token&oauth_token_secret=secret'
        self.oauth.get_profile_info(raw_token)
        self.assertTrue(auth.called)
        args, kwargs = auth.call_args
        self.assertEqual(kwargs['client_key'], self.provider.key)
        self.assertEqual(kwargs['client_secret'], self.provider.secret)
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


@patch('allaccess.clients.request')
class OAuth2ClientTestCase(BaseClientTestCase):
    "OAuth 2.0 client handling."

    oauth_client = OAuth2Client

    def test_access_token_url(self, requests):
        "Get should be sent to provider's access_token_url."
        request = MagicMock()
        request.GET = {'code': 'code'}
        self.oauth.get_access_token(request)
        self.assertTrue(requests.called)
        args, kwargs = requests.call_args
        method, url = args
        self.assertEqual(method, 'get')        
        self.assertEqual(url, self.provider.access_token_url)

    def test_access_token_response(self, requests):
        "Return full response text without parsing key/secret."
        response = Mock()
        response.text = 'access_token=USER_ACESS_TOKEN'
        requests.return_value = response
        request = MagicMock()
        request.GET = {'code': 'code'}
        token = self.oauth.get_access_token(request)
        self.assertEqual(token, 'access_token=USER_ACESS_TOKEN')

    def test_access_token_failure(self, requests):
        "Handle upstream server errors when fetching access token."
        requests.side_effect = RequestException('Server Down')
        request = MagicMock()
        request.GET = {'code': 'code'}
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
