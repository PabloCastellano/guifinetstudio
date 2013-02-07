#!/usr/bin/env python

from distutils.core import setup

VERSION = '0.7'

setup(
    name='pyGuifiAPI',
    version=VERSION,
    description="A Python interface for the Guifi.net API",
    long_description=open('README.txt').read(),
    author='Pablo Castellano',
    author_email='pablo@anche.no',
    packages=['pyGuifiAPI'],
    package_data={'': ['tests/*']},
    license='GPLv3+',
    data_files=[('', ['LICENSE.txt'])],
    include_package_data=True,
    zip_safe=False,
)
