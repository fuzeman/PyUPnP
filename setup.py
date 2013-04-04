#!/usr/bin/env python

# PyUPnP - Simple Python UPnP device library built in Twisted
# Copyright (C) 2013  Dean Gardiner <gardiner91@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

    packages=['pyupnp', 'pyupnp.services', 'pyupnp.services.microsoft'],
    requires=['twisted', 'requests', 'SOAPpy'],

    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking'
    ]
)