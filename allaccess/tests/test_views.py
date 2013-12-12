"Redirect and callback view tests."
from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse

from mock import patch, Mock

from .base import AllAccessTestCase, AccountAccess, get_user_model, skipIfCustomUser
from ..compat import urlparse, parse_qs


class BaseViewTestCase(AllAccessTestCase):
    "Common view test functionality."

    urls = 'allaccess.tests.urls'
    url_name = None

    def setUp(self):
        self.consumer_key = self.get_random_string()
        self.consumer_secret = self.get_random_string()
        self.provider = self.create_provider(consumer_key=self.consumer_key, consumer_secret=self.consumer_secret)
        self.url = reverse(self.url_name, kwargs={'provider': self.provider.name})
        # Replace exsiting settings
        self.LOGIN_URL = settings.LOGIN_URL
        self.LOGIN_REDIRECT_URL = settings.LOGIN_REDIRECT_URL
        settings.LOGIN_URL = '/login/'
        settings.LOGIN_REDIRECT_URL = '/'

    def tearDown(self):
        # Restore settings
        settings.LOGIN_URL = self.LOGIN_URL
        settings.LOGIN_REDIRECT_URL = self.LOGIN_REDIRECT_URL


class OAuthRedirectTestCase(BaseViewTestCase):
    "Initial redirect for user to sign log in with OAuth 1.0 provider."

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
            callback = reverse('allaccess-callback', kwargs={'provider': self.provider.name})
            self.assertEqual(query['oauth_callback'][0], 'http://testserver' + callback)

    def test_oauth_2_redirect_url(self):
        "Redirect url for OAuth 2.0 provider."
        self.provider.request_token_url = ''
        self.provider.save()
        response = self.client.get(self.url)
        url = response['Location']
        scheme, netloc, path, params, query, fragment = urlparse(url)
        self.assertEqual('%s://%s%s' % (scheme, netloc, path), self.provider.authorization_url)

    def test_oauth_2_redirect_parameters(self):
        "Redirect parameters for OAuth 2.0 provider."
        self.provider.request_token_url = ''
        self.provider.save()
        response = self.client.get(self.url)
        url = response['Location']
        scheme, netloc, path, params, query, fragment = urlparse(url)
        query = parse_qs(query)
        callback = reverse('allaccess-callback', kwargs={'provider': self.provider.name})
        self.assertEqual(query['redirect_uri'][0], 'http://testserver' + callback)
        self.assertEqual(query['response_type'][0], 'code')
        self.assertEqual(query['client_id'][0], self.provider.consumer_key)
        # State should be stored in the session and passed to the provider
        key = 'allaccess-{0}-request-state'.format(self.provider.name)
        state = self.client.session[key]
        self.assertEqual(query['state'][0], state)

    def test_unknown_provider(self):
        "Return a 404 if unknown provider name is given."
        self.provider.delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_disabled_provider(self):
        "Return a 404 if provider does not have key/secret set."
        self.provider.consumer_key = None
        self.provider.consumer_secret = None
        self.provider.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)


class OAuthCallbackTestCase(BaseViewTestCase):
    "Callback after user has authenticated with OAuth provider."

    url_name = 'allaccess-callback'

    def setUp(self):
        super(OAuthCallbackTestCase, self).setUp()
        # Patch OAuth client
        self.patched_get_client = patch('allaccess.views.get_client')
        self.get_client = self.patched_get_client.start()
        self.mock_client = Mock()
        self.get_client.return_value = self.mock_client

    def tearDown(self):
        super(OAuthCallbackTestCase, self).tearDown()
        self.patched_get_client.stop()

    def test_unknown_provider(self):
        "Return a 404 if unknown provider name is given."
        self.provider.delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_disabled_provider(self):
        "Return a 404 if provider does not have key/secret set."
        self.provider.consumer_key = None
        self.provider.consumer_secret = None
        self.provider.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_failed_access_token(self):
        "Handle bad response when fetching access token."
        self.mock_client.get_access_token.return_value = None
        response = self.client.get(self.url)
        # Errors redirect to LOGIN_URL by default
        self.assertRedirects(response, settings.LOGIN_URL)

    def test_failed_user_profile(self):
        "Handle bad response when fetching user info."
        self.mock_client.get_access_token.return_value = 'token'
        self.mock_client.get_profile_info.return_value = None
        response = self.client.get(self.url)
        # Errors redirect to LOGIN_URL by default
        self.assertRedirects(response, settings.LOGIN_URL)

    def test_failed_user_id(self):
        "Handle bad response when parsing user id from info."
        self.mock_client.get_access_token.return_value = 'token'
        self.mock_client.get_profile_info.return_value = {}
        response = self.client.get(self.url)
        # Errors redirect to LOGIN_URL by default
        self.assertRedirects(response, settings.LOGIN_URL)

    def _test_create_new_user(self):
        "Base test case for both swapped and non-swapped user."
        User = get_user_model()
        User.objects.all().delete()
        self.mock_client.get_access_token.return_value = 'token'
        self.mock_client.get_profile_info.return_value = {'id': 100}
        self.client.get(self.url)
        access = AccountAccess.objects.get(
            provider=self.provider, identifier=100
        )
        self.assertEqual(access.access_token, 'token')
        self.assertTrue(access.user, "User should be created.")
        self.assertFalse(access.user.has_usable_password(), "User created without password.")

    @skipIfCustomUser
    def test_create_new_user(self):
        "Create a new user and associate them with the provider."
        self._test_create_new_user()

    def _test_existing_user(self):
        "Base test case for both swapped and non-swapped user."
        User = get_user_model()
        user = self.create_user()
        access = self.create_access(user=user, provider=self.provider)
        user_count = User.objects.all().count()
        access_count = AccountAccess.objects.all().count()
        self.mock_client.get_access_token.return_value = 'token'
        self.mock_client.get_profile_info.return_value = {'id': access.identifier}
        self.client.get(self.url)
        self.assertEqual(User.objects.all().count(), user_count, "No users created.")
        self.assertEqual(AccountAccess.objects.all().count(), access_count, "No access records created.")
        # Refresh from DB
        access = AccountAccess.objects.get(pk=access.pk)
        self.assertEqual(access.access_token, 'token')

    @skipIfCustomUser
    def test_existing_user(self):
        "Authenticate existing user and update their access token."
        self._test_existing_user()

    def _test_authentication_redirect(self):
        "Base test case for both swapped and non-swapped user."
        self.mock_client.get_access_token.return_value = 'token'
        self.mock_client.get_profile_info.return_value = {'id': 100}
        response = self.client.get(self.url)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)

    @skipIfCustomUser
    def test_authentication_redirect(self):
        "Post-authentication redirect to LOGIN_REDIRECT_URL."
        self._test_authentication_redirect()
