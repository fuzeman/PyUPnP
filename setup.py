#!/usr/bin/env python

import setuptools
from distutils.core import setup

__author__ = 'Dean Gardiner'

setup(
    name='PyUPnP',
    version=__import__('pyupnp').__version__,
    description='Simple Python UPnP device library built in Twisted',
    author='Dean Gardiner',
    author_email='gardiner91@gmail.com',
    url='http://github.com/fuzeman/PyUPnP',
    packages=['pyupnp'], requires=['twisted', 'requests', 'SOAPpy'],
)