"Base test class and helper methods for writing tests."
from __future__ import unicode_literals

import random
import string

from django.contrib.auth.models import User
from django.test import TestCase

from allaccess.models import AccountAccess


class AllAccessTestCase(TestCase):
    "Common base test class."

    def get_random_string(self, length=10):
        return ''.join(random.choice(string.ascii_letters) for x in xrange(length))

    def get_random_email(self, domain='example.com'):
        local = self.get_random_string()
        return '{0}@{1}'.format(local, domain)

    def create_user(self, **kwargs):
        "Create a test User"
        defaults = {
            'username': self.get_random_string(),
            'password': self.get_random_string(),
            'email': self.get_random_email()
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)

    def create_access(self, **kwargs):
        "Create a test remote AccountAccess"
        defaults = {
            'service': self.get_random_string(),
            'identifier': self.get_random_string(),
        }
        defaults.update(kwargs)
        return AccountAccess.objects.create(**defaults)
