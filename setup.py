#!/usr/bin/env python

from distutils.core import setup

setup(
    name='DevWatch',
    version='1.0',
    description='Speed up your coding by running command on every saved change',
    author='Ulises Ojeda',
    author_email='ulises.odysseus22@gmail.com',
    url='http://github.com/ulisesojeda/devwatch',
    packages=['devwatch'],
    install_requires=['yaml'],
    )
