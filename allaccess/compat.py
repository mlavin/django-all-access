"Python and Django compatibility functions."
from __future__ import unicode_literals

from django.conf import settings


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


try:
    from django.utils.crypto import get_random_string
except ImportError: # pragma: no cover
    # Backport implementation from Django 1.4
    import hashlib
    import random
    import string
    import time
    try:
        random = random.SystemRandom()
        using_sysrandom = True
    except NotImplementedError:
        import warnings
        warnings.warn('A secure pseudo-random number generator is not available '
                      'on your system. Falling back to Mersenne Twister.')
        using_sysrandom = False

    def get_random_string(length=12, allowed_chars=string.ascii_letters + string.digits):
        "Returns a securely generated random string."
        if not using_sysrandom:
            # Re-seed random
            bytes = b"{0}{1}{2}".format(random.getstate(), time.time(), settings.SECRET_KEY)
            random.seed(hashlib.sha256(bytes).digest())
        return ''.join([random.choice(allowed_chars) for i in range(length)])


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

# Vendored six
try:
    from django.utils import six
except:
    from requests.packages.urllib3.packages import six