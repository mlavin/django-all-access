Customizing Redirects and Callbacks
====================================

django-all-access provides default views/urls for authentication. These are built
from Django's `class based views <https://docs.djangoproject.com/en/1.4/topics/class-based-views/>`_
making them easy to extend or override the default behavior in your project.


OAuthRedirect View
----------------------

The initial step for authenticating with any OAuth provider is redirecting the
user to the provider's website. The ``OAuthRedirect`` view extends from the
`RedirectView <https://docs.djangoproject.com/en/1.4/ref/class-based-views/#redirectview>`_
By default it is mapped to the ``allaccess-login`` url name. This view takes one
keyword argument from the url pattern ``provider`` which corresponds to the ``Provider.name``
for an enabled provider. If no enabled provider is found for the name then this view
will return a 404.

.. class:: OAuthRedirect()

    .. method:: get_redirect_url(**kwargs)

        This method is original defined by the RedirectView. The redirect url is
        constructed from the ``Provider.authorization_url`` along with the necessary
        parameters to match the OAuth specifications. You should not need to override
        this method in your application.

    .. method:: get_callback_url(provider)

        This returns the url which the remote provider should return the user after
        authentication. It is called by ``get_redirect_url`` to construct the appropriate
        redirect url. By default the reverses the ``allaccess-callback`` url name with
        the passed provider name.

        You may want to override this method in your application if you wish to have
        a custom callback for a given provider or a different callback for login vs
        registration or a different callback for an authenticated user associating a
        new provider with their account.


OAuthCallback View
----------------------

After the user has authenticated with the remote provider or denied access to your application
request, they are returned to callback specifed in the initial redirect. ``OAuthCallback``
defines the default behaviour on this callback. This view extends from the base
`View <https://docs.djangoproject.com/en/1.4/ref/class-based-views/#view>`_ class.
By default it is mapped to the ``allaccess-callback`` url name. Similar to the ``OAuthRedirect`` view, 
this view takes one keyword argument ``provider`` which corresponds to the ``Provider.name`` 
for an enabled provider. If no enabled provider is found for the name then this view will return a 404.

.. class:: OAuthCallback()

    .. method:: get_callback_url(provider)

        This returns the callback url specified in the initial redirect if it is
        different than the current ``request.path``. By default the callback url will be the same
        and this view will return ``None``. You will most likely not need to change this
        in your project.

    .. method:: get_error_redirect(provider, reason)
        
        Returns the url to send the user in the case of an authentication failure. The
        `reason` is a brief text description of the problem. By default this will return
        the user to the original login url as defined by the ``LOGIN_URL`` setting.

    .. method:: get_login_redirect(provider, user, access, new=False)

        You can use this to customize the url to send the user on a successful authentication.
        By default this will be the ``LOGIN_REDIRECT_URL`` setting. The ``new`` parameter
        is there to indicate if this was a newly created or a previously existing user.

    .. method:: get_or_create_user(provider, access, info)

        This method is used by ``handle_new_user`` to construct a new user with a 
        random username, no email and an unusable password. You may want to override 
        this user to complete more of their infomation or attempt to match them 
        to an existing user by either their username or email.

        ``handle_new_user`` will connect the user to the ``access`` record and 
        does not need to be handled here.

    .. method:: get_user_id(provider, info)

        This method should return the unique idenifier from the profile information. If
        the id cannot be determined this should return ``None``. The ``info`` parameter
        will be parsed JSON response from the user's profile. If the response wasn't
        JSON then it will be the plain text response. By default this looks for a key
        ``id`` in the JSON dictionary. This will work for a number of providers but
        will to be changed to fit more complex response structures.

    .. method:: handle_existing_user(provider, user, access, info)

        At this point the ``user`` has been authenticated via their ``access`` model
        with this provider but they have not been logged in. This method will login
        the user and redirect them to the url returned by ``get_login_redirect`` with
        ``new=False``.

        The user's profile info is passed to this method to allow for updating their
        data from their provider profile but this is not done by default.

    .. method:: handle_login_failure(provider, reason)

        In the case of a failure to fetch the user's access token, remote profile information
        or determine their id from that info this method will be called. It attachs a
        brief error message to the request via ``contrib.messages`` and redirects the
        user to the result of the ``get_error_redirect`` method. You should override 
        this function to add any additional logging or handling.

    .. method:: handle_new_user(provider, access, info)

        If the user could not be matched to an existing ``AccountAccess`` record for
        this provider or that record did not contain a user this method will be called.
        At this point the ``access`` record has already been saved but is not tied to
        a user. This will call ``get_or_create_user`` to construct a new user record. 
        The user is then logged in and redirected to the result of the ``get_login_redirect``
        call with ``new=True``.

        You may want to override this user to complete more of their infomation or
        attempt to match them to an existing user by either their username or email.
        You may want to override this to redirect them without creating a new user 
        in order to have them complete another registration form 
        (i.e. pick a username or provide an email if not returned by the provider).


Additional Accounts Example
----------------------------------

You may want to allow a user to associate their account on your website with multiple
providers. This example will show a basic outline of how you can customize these
views for that purpose.

First we will define a new callback which will associate the provider with the current
user rather than creating a new user. This view will also have to handle the case that
another user is associated with the new provider. For this the view will just return
an error.

.. code-block:: python

    from allaccess.views import OAuthCallback

    class AssociateCallback(OAuthCallback):

        def get_or_create_user(self, provider, access, info):
            return self.request.user

        def handle_existing_user(self, provider, user, access, info):
            if user != self.request.user:
                return self.handle_login_failure(provider, "Another user is associated with this account")
            # User was already associated with this account
            return super(AssociateCallback, self).handle_existing_user(provider, user, access, info)

This view will require authentication which is handled in the url pattern. There
are multiple methods for decorating class based views which are detailed in the
`Django docs <https://docs.djangoproject.com/en/1.4/topics/class-based-views/#decorating-class-based-views>`_.

Next we will need a redirect view to send the user to this callback. This view
will also require that the user already be authenticated which can be handled in
the url pattern.

.. code-block:: python

    from django.core.urlresolvers import reverse
    from allaccess.views import OAuthRedirect

    class AssociateRedirect(OAuthRedirect):

    def get_callback_url(self, provider):
        return reverse('associate-callback', kwargs={'provider': provider.name})

This assumes that we named the pattern for the above callback ``associate-callback``. An
example set of url patterns is given below.

.. code-block:: python

    from django.contrib.auth.decorators import login_required

    from .views import AssociateRedirect, AssociateCallback

    urlpatterns = patterns('',
        url(r'^associate/(?P<provider>(\w|-)+)/$', login_required(AssociateRedirect.as_view()), name='associate'),
        url(r'^associate-callback/(?P<provider>(\w|-)+)/$', login_required(AssociateCallback.as_view()), name='associate-callback'),
    )

That is the basic outline of how you would allow multiple account associations. This
could be further customized using the hooks described earlier.
