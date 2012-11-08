"Python and Django compatibility functions."
from __future__ import unicode_literals

from django.conf import settings


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
