#!/usr/bin/env python
from distutils.core import setup

PACKAGE = "pycurlbrowser"
NAME = "pycurlbrowser"
DESCRIPTION = "A minimal browser based on pycurl/lxml"
AUTHOR = "Adam Piper"
AUTHOR_EMAIL = "adam@ahri.net"
URL = "https://github.com/ahri/pycurlbrowser"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="AGPLv2",
    url=URL,
    packages=["pycurlbrowser"],
    platforms='any',
    install_requires=[
        'pycurl>=7.18',
        'lxml>=2.3',
        'simplejson>=2.2.1',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False,
)
