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

    def test_redirect_url(self, *args, **kwargs):
        "Redirect url is build from provider authorization_url."
        with patch.object(self.oauth, 'get_redirect_args') as args:
            args.return_value = {'foo': 'bar'}
            request = MagicMock()
            url = self.oauth.get_redirect_url(request)
            expected = self.provider.authorization_url + '?foo=bar'
            self.assertEqual(url, expected)


@patch('allaccess.clients.OAuth1')
@patch('allaccess.clients.requests')
class OAuthClientTestCase(BaseClientTestCase):
    "OAuth 1.0 client handling to match http://oauth.net/core/1.0/"

    oauth_client = OAuthClient

    def setUp(self):
        super(OAuthClientTestCase, self).setUp()
        self.provider.request_token_url = self.get_random_url()
        self.provider.save()

    def test_request_token_auth(self, requests, auth):
        "Construct post auth with provider key and secret."
        request = MagicMock()
        self.oauth.get_request_token(request)
        self.assertTrue(auth.called)
        args, kwargs = auth.call_args
        self.assertTrue(kwargs['client_key'], self.provider.key)
        self.assertTrue(kwargs['client_secret'], self.provider.secret)

    def test_request_token_url(self, requests, auth):
        "Post should be sent to provider's request_token_url."
        request = MagicMock()
        self.oauth.get_request_token(request)
        self.assertTrue(requests.post.called)
        args, kwargs = requests.post.call_args
        self.assertTrue(kwargs['url'], self.provider.request_token_url)

    def test_request_token_response(self, requests, auth):
        "Key and secret should be parsed from the server response."
        response = Mock()
        response.text = 'oauth_token=token&oauth_token_secret=secret'
        requests.post.return_value = response
        request = MagicMock()
        token, secret = self.oauth.get_request_token(request)
        self.assertEqual(token, 'token')
        self.assertEqual(secret, 'secret')

    def test_request_token_invalid_token(self, requests, auth):
        "Handle invalid server responses."
        response = Mock()
        response.text = 'XXXXXXXXXXXXXXXXXXX'
        requests.post.return_value = response
        request = MagicMock()
        token, secret = self.oauth.get_request_token(request)
        self.assertEqual(token, None)
        self.assertEqual(secret, None)

    def test_request_token_failure(self, requests, auth):
        "Handle upstream server errors."
        requests.post.side_effect = RequestException('Server Down')
        request = MagicMock()
        token, secret = self.oauth.get_request_token(request)
        self.assertEqual(token, None)
        self.assertEqual(secret, None)

    def test_request_token_save(self, requests, auth):
        "Raw token response should be saved to the session."
        response = Mock()
        raw_token = 'oauth_token=token&oauth_token_secret=secret'
        response.text = raw_token
        requests.post.return_value = response
        request = MagicMock()
        request.session = {}
        self.oauth.get_request_token(request)
        self.assertEqual(request.session[self.oauth.session_key], raw_token)


@patch('allaccess.clients.requests')
class OAuth2ClientTestCase(BaseClientTestCase):
    "OAuth 2.0 client handling."

    oauth_client = OAuth2Client
