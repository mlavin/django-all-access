"Python and Django compatibility functions."
from __future__ import unicode_literals

# urllib
try:
    from urllib.parse import urlencode, parse_qs, urlparse
except ImportError:  # pragma: no cover
    # Python 2.X
    from urllib import urlencode
    from urlparse import parse_qs, urlparse

try:  # pragma: no cover
    from google.appengine.ext import db
    APPENGINE = True
except ImportError:
    APPENGINE = False


try:  # pragma: no cover
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock
