django-all-access
===================

django-all-access is a reusable application for user registration and authentication
from OAuth 1.0 and OAuth 2.0 providers such as Twitter and Facebook.

The goal of this project is to make it easy to create your own workflows for
authenticating with these remote APIs. django-all-access will provide the simple
views with sane defaults along with hooks to override the default behavior.

.. image:: https://travis-ci.org/fdemmer/django-all-access.svg?branch=master
    :target: https://travis-ci.org/fdemmer/django-all-access

.. image:: https://codecov.io/gh/fdemmer/django-all-access/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/fdemmer/django-all-access

You can find a basic demo application running at http://django-all-access.mlavin.org/

Features
------------------------------------

- Sane and secure defaults for OAuth authentication
- Easy customization through class-based views
- Built on the amazing `requests <http://docs.python-requests.org/>`_ library


Installation
------------------------------------

It is easiest to install this fork of django-all-access from GitHub using pip:

.. code-block:: shell

    pip install git+https://github.com/fdemmer/django-all-access@v1.0.0#egg=django-all-access


django-all-access requires Python 3.5+ along with the following Python
packages (and will be automatically installed if necessary):

.. code-block:: text

    django>=2.0
    pycrypto>=2.4
    requests>=2.0
    requests_oauthlib>=0.4.2
    oauthlib>=0.6.2


Documentation
--------------------------------------

Additional documentation on using django-all-access is available on
`Read The Docs <http://readthedocs.org/docs/django-all-access/>`_.


License
--------------------------------------

django-all-access is released under the BSD License. See the
`LICENSE <https://github.com/fdemmer/django-all-access/blob/master/LICENSE>`_
file for more details.


Contributing
--------------------------------------

If you have questions about using django-all-access or want to follow updates about
the project you can join the `mailing list <http://groups.google.com/group/django-all-access>`_
through Google Groups.

If you think you've found a bug or are interested in contributing to this project
check out `django-all-access on Github <https://github.com/fdemmer/django-all-access>`_.
