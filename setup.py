import pathlib

from setuptools import find_packages, setup


def read_file(filename):
    """Read a file into a string"""
    try:
        return (pathlib.Path(__file__).parent / filename).read_text()
    except FileNotFoundError:
        return ''


setup(
    name='django-all-access',
    version=__import__('allaccess').__version__,
    author='Mark Lavin',
    author_email='markdlavin@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/fdemmer/django-all-access',
    license='BSD',
    description=' '.join(__import__('allaccess').__doc__.splitlines()).strip(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    long_description=read_file('README.rst'),
    install_requires=(
        'pycryptodome>=3.9',
        'requests>=2.0',
        'requests_oauthlib>=0.4.2',
        'oauthlib>=0.6.2',
    ),
    test_suite="runtests.runtests",
    zip_safe=False,
)
