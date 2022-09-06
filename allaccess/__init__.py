"""
django-all-access is a reusable application for user registration and authentication
from OAuth 1.0 and OAuth 2.0 providers such as Twitter and Facebook.
"""
import logging

__version__ = '1.3.2'

default_app_config = 'allaccess.apps.AllAccessConfig'


class NullHandler(logging.Handler):
    """No-op logging handler."""

    def emit(self, record):
        pass


# Configure null handler to prevent "No handlers could be found..." errors
logging.getLogger('allaccess').addHandler(NullHandler())
