Release History
====================================

Release and change history for django-all-access

v0.2.0 (TBD)
------------------------------------

Features
_________________

- OAuthRedirect view can now specify a callback url
- Context processor for adding enabled providers to the template context


Bug Fixes
_________________

- Fixed OAuth2Client to include ``grant_type`` paramater when requesting access token
- Fixed OAuth2Client to match current OAuth draft for access token response as well as legacy response from Facebook


Backwards Incompatible Changes
__________________________________

- Moving the construction on the callback from the client to the view changed the
signature of the client ``get_redirect_url``, ``get_redirect_args``, ``get_request_token``
(OAuth 1.0 only) and ``get_access_token`` to include the callback. These are largely
internal functions and likely will not impact existing applications.


v0.1.1 (2012-06-22)
------------------------------------

- Fixed bug with passing incorrect callback parameter for OAuth 1.0
- Additional documentation on configuring ``LOGIN_URL`` and ``LOGIN_REDIRECT_URL``
- Additional view tests
- Handled poor ``LOGIN_URL`` and ``LOGIN_REDIRECT_URL`` settings in view tests


v0.1.0 (2012-06-21)
------------------------------------

- Initial public release.
