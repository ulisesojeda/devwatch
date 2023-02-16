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

===========
Basic usage
===========
``devwatch -t main``

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
* Ubuntu x86_64
* Debian ?
* Centos ?
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
* Allow to define several files separated by space
* Allow to define several files by glob expansion
* Hot reload configuration file
* Unit tests
* Create PyPi package
* Install as a separated script to be run as `devwatch`
* FreeBSD/OpenBSD/NetBSD support
* MacOS support
