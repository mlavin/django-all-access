Configuring Providers
====================================

django-all-access configures and stores the set of OAuth providers in the database.
To enable your users to authenticate with a particular provider, you will need to add
the OAuth API URLs as well as your application's consumer key and consumer secret.
The process of registering your application with each provider will vary and
you should refer to the provider's API documentation for more information.

.. note::

    While the consumer key/secret pairs are stored in the database
    as opposed to putting them in the settings file, they are encrypted using the
    `AES specification <http://en.wikipedia.org/wiki/Advanced_Encryption_Standard>`_.
    Since this is a symmetric-key encryption the key/secret pairs can still be read
    if the encryption key is compromised. In this case django-all-access uses a
    key based on the standard ``SECRET_KEY`` setting. You should take care to keep
    this setting secret as its name would imply.


Common Providers
------------------------------------

To get you started, there is an initial fixture of commonly used providers. This includes
the URLs needed for Facebook, Twitter, Google, Microsoft Live, Github and Bitbucket. Once you've
added ``allaccess`` to your ``INSTALLED_APP`` and created the tables with ``migrate``,
you can load this fixture via::

    python manage.py loaddata common_providers.json

This does not include the consumer id/key or secret which will still need to be added
to the records. The below examples will help you understand what these values mean
and how they would be populated for additional providers you might want to use.


OAuth 1.0 Providers
------------------------------------

OAuth 1.0 Protocol is defined by `RFC 5849 <http://tools.ietf.org/html/rfc5849>`_.
It is sometimes referred to as 3-Legged OAuth due to the number of requests
between the provider and consumer.

To enable an OAuth provider, you should add a ``Provider`` record with the necessary
``request_token_url``, ``authorization_url`` and ``access_token_url`` as defined
by the protocol. The provider's API documentation should detail these for you. You
will also need to define a ``profile_url`` which is the API endpoint for requesting
the currently authenticated user's profile information. You will also need to
register for a key/secret pair from the provider.

This protocol is implemented by a number of providers. These providers
include Twitter, Netflix, Yahoo, Linkedin, Flickr, Bitbucket, and Dropbox.
Additional providers can be found on the 
`OAuth.net Wiki <http://wiki.oauth.net/w/page/12238551/ServiceProviders>`_.


Twitter Example
------------------------------------

Twitter is a popular social website which provides a REST API with OAuth 1.0
authentication. If you wanted to enable Twitter authentication on your website
using django-all-access, you would create the following ``Provider`` record::

    name: twitter
    request_token_url: https://api.twitter.com/oauth/request_token
    authorization_url: https://api.twitter.com/oauth/authenticate
    access_token_url: https://api.twitter.com/oauth/access_token
    profile_url: https://api.twitter.com/1.1/account/verify_credentials.json

After adding your consumer key and secret to this record you should now be able
to authenticate with Twitter by visiting ``/accounts/login/twitter/``.
You can find more information on the Twitter API on their `developer site <https://dev.twitter.com/docs>`_.


OAuth 2.0 Providers
------------------------------------

Unlike OAuth 1.0, OAuth 2.0 is only a `working draft <http://tools.ietf.org/html/draft-ietf-oauth-v2-28>`_
and not an official standard. In many ways it is much simpler than its predecessor.
It is often referred to as 2-Legged OAuth because it removes the need for the
request token step.

To enable an OAuth provider, you should add a ``Provider`` record with the necessary
``authorization_url`` and ``access_token_url`` as defined by the protocol. 
The provider's API documentation should detail these for you. You
will also need to define a ``profile_url`` which is the API endpoint for requesting
the currently authenticated user's profile information. You will also need to
register for a key/secret pair from the provider.

Providers which implement the OAuth 2.0 protocol include Facebook, Google,
FourSquare, Meetup, Github, and Yammer.


Facebook Example
------------------------------------

Facebook is a large social network which provides a REST API with OAuth 2.0
authentication. The below ``Provider`` record will enable Facebook authentication::

    name: facebook
    authorization_url: https://www.facebook.com/v2.8/dialog/oauth
    access_token_url: https://graph.facebook.com/v2.8/oauth/access_token
    profile_url: https://graph.facebook.com/v2.8/me

As you can see, the ``request_token_url`` is not included because it is not needed.
After adding your consumer key and secret to this record you should now be able
to authenticate with Facebook by visiting ``/accounts/login/facebook/``.
Facebook also has `developer docs <http://developers.facebook.com/docs/>`_
for additional information on using their API.

.. note::

    Facebook began using the version number in the URL as part of their 2.0 API.
    Since then very little has changed with regard to the OAuth flow but the
    version number is now required. The latest version of the API might not
    match the documentation here. For the most up to date info on the Facebook
    API you should consult their API docs.
