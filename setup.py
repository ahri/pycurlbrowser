#!/usr/bin/env python
from distutils.core import setup

setup(
    name="pycurlbrowser",
    version='0.2.1',
    description="A minimal browser based on pycurl/lxml",
    long_description=open("README").read(),
    author="Adam Piper",
    author_email="adam@ahri.net",
    license="AGPLv3",
    url="https://github.com/ahri/pycurlbrowser",
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
