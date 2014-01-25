"Python and Django compatibility functions."
from __future__ import unicode_literals

from django.conf import settings


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


try:
    from django.contrib.auth import get_user_model
except ImportError: # pragma: no cover
    # Django < 1.5
    from django.contrib.auth.models import User
    User.USERNAME_FIELD = 'username'
    get_user_model = lambda: User


# urllib
try:
    from urllib.parse import urlencode, parse_qs, urlparse
except ImportError: # pragma: no cover
    # Python 2.X
    from urllib import urlencode
    from urlparse import parse_qs, urlparse


try:
    from django.utils.encoding import force_text, smart_bytes, force_bytes
except ImportError: # pragma: no cover
    from django.utils.encoding import force_unicode as force_text
    from django.utils.encoding import smart_str as smart_bytes
    try:
        from django.utils.encoding import force_str as force_bytes
    except ImportError:
        # This didn't get back-ported to 1.4.X
        force_bytes = smart_bytes


try: # pragma: no cover
    from google.appengine.ext import db
    APPENGINE = True
except ImportError:
    APPENGINE = False
