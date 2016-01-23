#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings

SWAPPED = os.environ.get('SWAPPED', False)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'allaccess',
]

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=INSTALLED_APPS,
        MIDDLEWARE_CLASSES=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        AUTHENTICATION_BACKENDS=(
            'allaccess.backends.AuthorizedServiceBackend',
        ),
        SECRET_KEY='9a0e2569bccc45e49ba8e393233fc427',
        ROOT_URLCONF='allaccess.tests.urls',
        LOGIN_URL='/login/',
        LOGIN_REDIRECT_URL='/',
        USE_TZ=True,
    )


if SWAPPED:
    settings.INSTALLED_APPS.append('allaccess.tests.custom')
    settings.AUTH_USER_MODEL = 'custom.MyUser'

from django.test.utils import get_runner


def runtests():
    django.setup()
    apps = sys.argv[1:] or ['allaccess', ]
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(apps)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
