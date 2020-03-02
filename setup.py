import os
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup(
    name='django3-all-access',
    version=__import__('allaccess').__version__,
    author='Storm',
    author_email='storm@g.globo',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/stormers/django-all-access',
    license='BSD',
    description=' '.join(__import__('allaccess').__doc__.splitlines()).strip(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'Framework :: Django :: 3.0',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    long_description=read_file('README.rst'),
    install_requires=(
        'pycrypto>=2.4',
        'requests>=2.0',
        'requests_oauthlib>=0.4.2',
        'oauthlib>=0.6.2',
    ),
    tests_require=('mock>=0.8', ),
    test_suite="runtests.runtests",
    zip_safe=False,
)
