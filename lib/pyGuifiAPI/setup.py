#!/usr/bin/env python

from distutils.core import setup

VERSION = '1.0'

setup(
    name='pyGuifiAPI',
    version=VERSION,
    description="A Python interface for guifi.net API",
    author='Pablo Castellano',
    author_email='pablo@anche.no',
    packages=['pyGuifiAPI'],
    include_package_data=True,
    zip_safe=False,
)
