#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

import sys
sys.path.insert(0, './files/')

import pyrfid

setup(
    name            = 'pyrfid-dlr',
    version         = pyrfid.__version__,
    description     = 'Python written library for an 125kHz RFID reader',
    long_description= 'Fork of the PyRFID Project originally by Philipp Meisenberger.',
    author          = 'Alexander Tepe',
    author_email    = 'alexander.tepe@dlr.de',
    license         = 'D-FSL',
    package_dir     = {'': 'files'},
    packages        = ['pyrfid'],
    install_requires = ['pyserial']
)
