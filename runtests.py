#!/usr/bin/env python
import sys

from django.conf import settings


if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'allaccess',
        ),
        AUTHENTICATION_BACKENDS=(
            'allaccess.backends.AuthorizedServiceBackend',
        ),
        SITE_ID=1,
        SECRET_KEY='9a0e2569bccc45e49ba8e393233fc427',
        ROOT_URLCONF='allaccess.tests.urls',
    )


from django.test.utils import get_runner


def runtests():
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(['allaccess', ])
    sys.exit(failures)


if __name__ == '__main__':
    runtests()

