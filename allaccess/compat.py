"""Python and Django compatibility functions."""

try:  # pragma: no cover
    from google.appengine.ext import db
    APPENGINE = True
except ImportError:
    APPENGINE = False

try:  # pragma: no cover
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock
