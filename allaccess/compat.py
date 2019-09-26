"""Python, Django and environment compatibility functions."""

try:  # pragma: no cover
    from google.appengine.ext import db
    APPENGINE = True
except ImportError:
    APPENGINE = False
