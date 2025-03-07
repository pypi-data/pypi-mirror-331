#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name            = 'pyrfid-dlr',
    version         = "1.1",
    description     = 'Python written library for an 125kHz RFID reader',
    long_description= 'Fork of PyRFID library, originally by Philipp Meisenberger',
    author          = 'Alexander Tepe',
    author_email    = 'alexander.tepe@dlr.de',
    url             = 'https://github.com/philippmeisberger/pyrfid',
    license         = 'D-FSL',
    packages        = find_packages(),
    install_requires = [
        'setuptools',
        'pyserial'
    ]
)
