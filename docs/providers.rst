Configuring Providers
====================================

django-all-access configures and stores the set of OAuth providers in the database.
To enable your users to authenticate with a particular provide you will need to add 
the OAuth API urls as well as your application's consumer key and consumer secret. 
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


OAuth 1.0 Providers
------------------------------------

OAuth 1.0 Protocol is defined by `RFC 5849 <http://tools.ietf.org/html/rfc5849>`_. 
It is sometimes referred to as 3-Legged OAuth due to the number of requests 
between the provider and consumer.

To enable an OAuth provider you should add a ``Provider`` record with the necessary
``request_token_url``, ``authorization_url`` and ``access_token_url`` as defined
by the protocol. The provider's API documentation should detail these for you. You
will also need to define a ``profile_url`` which is the API endpoint for requesting
the currently authenticated user's profile information. You will also need to
register for a key/secret pair from the provider.

This protocol implemented by a number of providers. These providers
include Twitter, Netflix, Yahoo, Linkedin, Flickr, Bitbucket and Dropbox.
Additional providers can be found on the 
`OAuth.net Wiki <http://wiki.oauth.net/w/page/12238551/ServiceProviders>`_.


Twitter Example
------------------------------------

Twitter is a popular social website which provides a REST API with OAuth 1.0
authentication. If you wanted to enable Twitter authentication on your website
using django-all-access you would create the following ``Provider`` record.
::
    name: twitter
    request_token_url: https://api.twitter.com/oauth/request_token
    authorization_url: https://api.twitter.com/oauth/authenticate
    access_token_url: https://api.twitter.com/oauth/access_token
    profile_url: https://twitter.com/account/verify_credentials.json

After adding your consumer key and secret to this record you should now be able
to authenticate with Twitter by visiting ``/accounts/login/twitter/``.
You can find more information on the Twitter API on their `developer site <https://dev.twitter.com/docs>`.


OAuth 2.0 Providers
------------------------------------

Unlike OAuth 1.0, OAuth 2.0 is only a `working draft <http://tools.ietf.org/html/draft-ietf-oauth-v2-28>`
and not an official standard. In many ways it is much simpler than its predecessor.
It is often referred to as 2-Legged OAuth because it removes the need for the
request token step.

To enable an OAuth provider you should add a ``Provider`` record with the necessary
``authorization_url`` and ``access_token_url`` as defined by the protocol. 
The provider's API documentation should detail these for you. You
will also need to define a ``profile_url`` which is the API endpoint for requesting
the currently authenticated user's profile information. You will also need to
register for a key/secret pair from the provider.

Providers which implement the OAuth 2.0 protocol include Facebook, Google,
FourSquare, Meetup, Github and Yammer.


Facebook Example
------------------------------------

Facebook is a large social network which provides a REST API with OAuth 2.0
authentication. The below ``Provider`` record will enable Facebook authentication.
::
    name: facebook
    authorization_url: https://www.facebook.com/dialog/oauth
    access_token_url: https://graph.facebook.com/oauth/access_token
    profile_url: https://graph.facebook.com/me

As you can see the ``request_token_url`` is not included because it is not needed.
After adding your consumer key and secret to this record you should now be able
to authenticate with Facebook by visiting ``/accounts/login/facebook/``.
Facebook also has a `developer site <http://developers.facebook.com/docs/>`_
for additional information on using their API.
