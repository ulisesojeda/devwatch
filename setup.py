#!/usr/bin/env python

from setuptools import setup

setup(
   name='DevWatch',
   version='0.1.0',
   author='Ulises Ojeda',
   author_email='ulises.odysseus22@gmail.com',
   packages=['devwatch'],
   scripts=['bin/devwatch'],
   license='LICENSE',
   description='Speed up your coding by running a command on every saved change',
   install_requires=[
       "pyyaml",
   ],
)
