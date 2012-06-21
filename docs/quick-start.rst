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


Provider Data
------------------------------------

django-all-access configures and stores the set of OAuth providers in the database.
An initial set of providers is loaded by data migrations. If you are using South
these will be loaded for you automatically.

To enable your users to authenticate with a particular provide you will need to add the
consumer key and consumer secret. The process of registering your application with
each provider will vary and you should refer to the provider's API documentation
for more information.

.. note::

    For those not using South, an initial set of providers is available by loading
    the ``allaccess_providers.json`` fixture. To do this you should simply run::

        python manage.py loaddata allaccess_providers.json
