Getting Started
====================================

Below are the basic steps need to get django-all-access integrated into your
Django project.


Configure Settings
------------------------------------

You need to include ``allaccess`` to your installed apps as well as include an
additional authentication backend in your project settings. django-all-access requires
``django.contrib.auth``, ``django.contrib.sessions`` and ``django.contrib.messages`` 
which are enabled in Django by default. ``django.contrib.admin`` is recommended 
for managing the set of providers but is not required.

.. code-block:: python

    INSTALLED_APPS = (
        # Required contrib apps
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.messages',
        # Optional
        'django.contrib.admin',
        # Other installed apps would go here
        'allaccess',
    )

    AUTHENTICATION_BACKENDS = (
        # Default backend
        'django.contrib.auth.backends.ModelBackend',
        # Additional backend
        'allaccess.backends.AuthorizedServiceBackend',
    )

Note that ``AUTHENTICATION_BACKENDS`` is not included in the default settings
created by ``startproject``. If you want to continue to use the default
username/password based authentication should be be sure to include
``django.contrib.auth.backends.ModelBackend`` in this setting.


Configure Urls
------------------------------------

To use the default redirect and callback views you should include them in
your root url configuration.

.. code-block:: python

    urlpatterns = patterns('',
        # Other url patterns would go here
        url(r'^accounts/', include('allaccess.urls')),
    )

This makes the login url for a particular provider ``/accounts/login/<provider>/``
such as ``/accounts/login/twitter/`` or ``/accounts/login/facebook/``. Once the user 
has authenticated with the remote provider the will be sent back to
``/accounts/callback/<provider>/`` such as ``/accounts/callback/twitter/`` 
or ``/accounts/callback/facebook/``.


Create Database Tables
------------------------------------

You'll need to create the necessary database tables for storing ad sections and
placements. This is done with the ``syncdb`` management command built into Django::

    python manage.py syncdb

django-all-access uses `South <http://south.aeracode.org/>`_ to handle database migrations. 
If you are also using South then you should run ``migrate`` instead::

    python manage.py migrate allaccess


Next Steps
------------------------------------

At this point your project is configured to use the default django-all-access
authentication but no providers have been added. Continue reading to learn how
to add providers for your project.
