Additional API Calls
====================================

django-all-access requests the user's access token and fetches their profile information
during the authentication process. If you want to make additional API calls on behalf
of the user it is easy to do and you have the full power of the 
`python-requests <http://docs.python-requests.org/>`_ library.


Getting the API
----------------------

You can access the API client through the ``AccountAccess.api_client`` property.
This will return either a ``OAuthClient`` or ``OAuth2Client`` based on the
provider. API requests can be made using either the ``request`` method. This takes
the HTTP method as the first parameter and the url as the second. An example for the
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
user. While this example is done in the callback you can access the this API client at
any time by querying the ``AccountAccess`` table. There is a catch in that the 
access token from the provider might have been revoked by the user or expired. 
You should refer to the provider's API documentation for information regarding 
available endpoints and the access token expiration.

The ``request`` method is a thin wrapper around the underlying ``python-requests``
library which sets up the appropriate authenication for OAuth 1.0 or OAuth 2.0. For
more information on additional hooks available you should refer to the `python-requests
documentation <http://docs.python-requests.org/en/latest/api/#requests.request>`_.
