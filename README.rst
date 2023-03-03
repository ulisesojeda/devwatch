********
DevWatch
********

Speed up your coding by running your program, test suite, linter, etc on every saved changes. 

============
Installation
============
1. pip install devwatch
2. Create `.devwatchrc.yml` on your project directory or home folder

   `.devwatchrc.yml` example:
   main:
       files: main.py
       command: python main.py
   tests:
       files: tests/
       command: pytest @
   flake:
       files: main.py
       command: flake8 test.py

   * Define targets (`main`, `tests` and `flake` in this example)
   * For every target define:
     ** `files`: File or directory to watch
     ** `command`: Command to execute when a file change is detected
   * When watching on directories like on target `tests`, you can use `@` to reference the
     modified file. In that example, when file `tests/foo.py` is amended `pytest tests/foo.py`
     will be execute

   * Warning: if no files exists for the target, the program will exit. 
===========
Basic usage
===========
``devwatch -t main``

* If no target is specified, the program will run the first target defined in the configurationfile

===================
System requirements
===================
* Unix-like system
* Python 3.X

===================
Python requirements
==================
* yaml >= ?

=========
Tested on
=========
* Ubuntu 20.04, 22.04 x64
* Debian 11 x64
* Centos 7 x84
* Arch ?
* Alpine ?
* Gentoo ?
* RHL ?
* Void ?
* Kali ?
* Fedora ?

====
TODO
====
* Hot reload configuration file
* Unit tests
* Create PyPi package
* FreeBSD/OpenBSD/NetBSD support
* MacOS support
