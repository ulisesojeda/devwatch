#!/usr/bin/env python

from setuptools import setup

with open("README.rst", "r") as f:
    long_description = f.read()

setup(
   name='devwatch',
   version='0.0.5',
   author='Ulises Ojeda',
   url='https://github.com/ulisesojeda/devwatch',
   packages=['devwatch'],
   scripts=['bin/devwatch'],
   license='LICENSE',
   description='Speed up your coding by running a command on every saved change',
   long_description=long_description,
   long_description_content_type="text/plain",
   install_requires=[
       "pyyaml",
   ],
   python_requires='>=3.2',
)
