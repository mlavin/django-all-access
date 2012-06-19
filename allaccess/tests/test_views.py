from urlparse import urlparse, parse_qs

from django.core.urlresolvers import reverse

from mock import patch

from .base import AllAccessTestCase


class BaseViewTestCase(AllAccessTestCase):
    "Common view test functionality."
    
    urls = 'allaccess.tests.urls'
    url_name = None

    def setUp(self):
        self.key = self.get_random_string()
        self.secret = self.get_random_string()
        self.provider = self.create_provider(key=self.key, secret=self.secret)
        self.url = reverse(self.url_name, kwargs={'service': self.provider.name})


class OAuthRedirectTestCase(BaseViewTestCase):
    "Initial redirect for user to sign log in."

    url_name = 'allaccess-login'

    def test_oauth_1_redirect_url(self):
        "Redirect url for OAuth 1.0 provider."
        self.provider.request_token_url = self.get_random_url()
        self.provider.save()
        with patch('allaccess.clients.OAuthClient.get_request_token') as request_token:
            request_token.return_value = 'oauth_token=token&oauth_token_secret=secret'
            response = self.client.get(self.url)
            url = response['Location']
            scheme, netloc, path, params, query, fragment = urlparse(url)
            self.assertEqual('%s://%s%s' % (scheme, netloc, path), self.provider.authorization_url)

    def test_oauth_1_redirect_parameters(self):
        "Redirect parameters for OAuth 1.0 provider."
        self.provider.request_token_url = self.get_random_url()
        self.provider.save()
        with patch('allaccess.clients.OAuthClient.get_request_token') as request_token:
            request_token.return_value = 'oauth_token=token&oauth_token_secret=secret'
            response = self.client.get(self.url)
            url = response['Location']
            scheme, netloc, path, params, query, fragment = urlparse(url)
            query = parse_qs(query)
            self.assertEqual(query['oauth_token'][0], 'token')
            callback = reverse('allaccess-callback', kwargs={'service': self.provider.name})
            self.assertEqual(query['callback_url'][0], 'http://testserver' + callback)

    def test_oauth_2_redirect(self):
        "Redirect url for OAuth 2.0 provider."
        self.provider.request_token_url = ''
        self.provider.save()
        response = self.client.get(self.url)
        url = response['Location']
        scheme, netloc, path, params, query, fragment = urlparse(url)
        self.assertEqual('%s://%s%s' % (scheme, netloc, path), self.provider.authorization_url)

    def test_oauth_2_redirect(self):
        "Redirect parameters for OAuth 2.0 provider."
        self.provider.request_token_url = ''
        self.provider.save()
        response = self.client.get(self.url)
        url = response['Location']
        scheme, netloc, path, params, query, fragment = urlparse(url)
        query = parse_qs(query)
        callback = reverse('allaccess-callback', kwargs={'service': self.provider.name})
        self.assertEqual(query['redirect_uri'][0], 'http://testserver' + callback)
        self.assertEqual(query['response_type'][0], 'code')
        self.assertEqual(query['client_id'][0], self.provider.key)

    def test_unknown_provider(self):
        "Return a 404 if unknown provider name is given."
        self.provider.delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
