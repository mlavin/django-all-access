#!/usr/bin/env python
import os
import sys

from django.conf import settings

SWAPPED = os.environ.get('SWAPPED', False)

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.admin',
            'south',
            'allaccess',
        ],
        AUTHENTICATION_BACKENDS=(
            'allaccess.backends.AuthorizedServiceBackend',
        ),
        SITE_ID=1,
        SECRET_KEY='9a0e2569bccc45e49ba8e393233fc427',
        ROOT_URLCONF='allaccess.tests.urls',
        LOGIN_URL='/login/',
        LOGIN_REDIRECT_URL='/',
        USE_TZ=True,
        SOUTH_TESTS_MIGRATE=True,
    )


if SWAPPED:
    settings.INSTALLED_APPS.append('allaccess.tests.custom')
    settings.AUTH_USER_MODEL = 'custom.MyUser'

from django import VERSION
from django.test.utils import get_runner
from south.management.commands import patch_for_test_db_setup


def runtests():
    patch_for_test_db_setup()
    apps = sys.argv[1:] or ['allaccess', ]
    if SWAPPED and VERSION[0] == 1 and VERSION[1] < 6:
        apps.append('custom')
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(apps)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()

