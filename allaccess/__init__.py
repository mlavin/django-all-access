"""
django-all-access is a reusable application for user registration and authentication
from OAuth 1.0 and OAuth 2.0 providers such as Twitter and Facebook.
"""


__version__ = '0.9.0'


default_app_config = 'allaccess.apps.AllAccessConfig'


import logging


class NullHandler(logging.Handler):
    "No-op logging handler."

    def emit(self, record):
        pass

# Configure null handler to prevent "No handlers could be found..." errors
logging.getLogger('allaccess').addHandler(NullHandler())
