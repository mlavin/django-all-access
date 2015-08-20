Additional API Calls
====================================

django-all-access requests the user's access token and fetches their profile information
during the authentication process. If you want to make additional API calls on behalf
of the user, it is easy to do and you have the full power of the
`python-requests <http://docs.python-requests.org/>`_ library.


Getting the API
----------------------

You can access the API client through the ``AccountAccess.api_client`` property.
This will return either a :py:class:`OAuthClient` or :py:class:`OAuth2Client` based on the
provider. API requests can be made using either the :py:meth:`BaseOAuthClient.request` method. This takes
the HTTP method as the first parameter and the URL as the second. An example for the
Twitter API is given below:

.. code-block:: python

    from allaccess.views import OAuthCallback

    class NewTweetCallback(OAuthCallback):

        def get_login_redirect(self, provider, user, access, new=False):
            "Send a tweet for new Twitter users."
            if new and provider.name == 'twitter':
                api = access.api_client
                url = 'https://api.twitter.com/1/statuses/update.json'
                data = {'status': 'I just joined an awesome new site!'}
                response = api.request('post', url, data=data)
                # Check for errors in the response?
            return super(NewTweetCallback, self).get_login_redirect(provider, user, access, new)

This assumes that you have requested sufficient permissions to tweet on behalf of the
user. While this example is done in the callback, you can access the API client at
any time by querying the ``AccountAccess`` table. There is a catch in that the 
access token from the provider might have been revoked by the user or expired. 
You should refer to the provider's API documentation for information regarding 
available endpoints and the access token expiration.

The :py:meth:`BaseOAuthClient.request` method is a thin wrapper around the underlying
``python-requests`` library which sets up the appropriate authenication for OAuth 1.0 or OAuth 2.0. For
more information on additional hooks available, you should refer to the `python-requests
documentation <http://docs.python-requests.org/en/latest/api/#requests.request>`_.


API Client
----------------------

The :py:class:`OAuthClient` or :py:class:`OAuth2Client` classes define methods centered around OAuth
specifications and the authentication and registration workflow. The common methods
are defined in a :py:class:`BaseOAuthClient`. If you are going to extend the client for
a particular provider, it is recommended that you extend the appropriate OAuth 1.0 or
2.0 client rather than the :py:class:`BaseOAuthClient`.

.. class:: BaseOAuthClient()

    .. method:: __init__(provider, token='')

        The client classes are created with an associated provider model record.
        The provider is used to provide the necessary URL (request token, access
        token, profile URL) information to the client.

    .. method:: get_access_token(request, callback=None)

        Used to fetch the access token from the callback URL. Unless you are
        familiar with the OAuth specifications, it is not recommended that you
        override this method.

    .. method:: get_profile_info(raw_token)

        Fetches and parses the profile information from the provider's profile
        URL. This assumes that the response is JSON. If not, you may need to
        override this method.

    .. method:: get_redirect_args(request, callback)

        Builds the necessary query string parameters for the initial redirect
        based on the OAuth specification. Additional parameters are better added
        using :py:meth:`OAuthRedirect.get_additional_parameters`. Unless you are
        familiar with the OAuth specifications, it is not recommended that you
        override this method.

    .. method:: get_redirect_url(request, callback)

        Builds the appropriate OAuth callback URL based on the provider information
        and the result of :py:meth:`BaseOAuthClient.get_redirect_args`. Unless you are familiar with the 
        OAuth specifications, it is not recommended that you override this method.

    .. method:: parse_raw_token(raw_token)

        Parses the token (key, secret) information from the raw token response.

    .. method:: request(method, url, **kwargs)

        A thin wrapper around ``python-requests``, this also sets up the appropriate
        authentication headers/parameters.

    .. attribute:: session_key

        Returns a key for storing information in the user's session. For OAuth 1.0
        this would be used to store the request token information. For OAuth 2.0
        this is used for enforcing the ``state`` parameter.

Beyond the methods above, the :py:class:`OAuthClient` also defines the below methods.

.. class:: OAuthClient()

    .. method:: get_request_token(request, callback)

        Retrieves the request token prior to the initial redirect to the provider. This
        is stored in the session using the :py:attr:`BaseOAuthClient.session_key` which is unique per provider.
        Unless you are familiar with the OAuth 1.0 specification, it is not recommended that you
        override this method.


:py:class:`OAuth2Client` extends :py:class:`BaseOAuthClient` to include these additional methods.

.. class:: OAuth2Client()

    .. method:: check_application_state(request, callback)

        On the callback this method is called to enforce the use of the ``state`` parameter.
        The use of ``state`` is optional in the OAuth 2.0 spec but it is recommended
        and enforced by default by django-all-access. If you do not want to enforce
        the use of ``state``, you should override :py:meth:`OAuth2Client.get_application_state` and
        leave this method alone.

    .. method:: get_application_state(request, callback)

        Prior to the redirect, this method is used to generate a random ``state`` parameter
        which is stored in the session based on the :py:attr:`BaseOAuthClient.session_key`. By default it
        generates a secure random 32 character string. If you wish to make it longer
        you can override this method. If you do not want to enforce the ``state``
        parameter or the provider you are using does not allow it, you can override
        this to return ``None``.
