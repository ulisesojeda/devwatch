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
`devwatch -t main`

* If no target is specified, the program will run the first target defined in the configuration file

===================
System requirements
===================
* Linux x64
* Python 3.X

===================
Python requirements
==================
* pyyaml

=========
Tested on
=========
* Ubuntu 20.04, 22.04
* Debian 11
* Centos 7

====
TODO
====
* Hot reload configuration file
* Unit tests
* FreeBSD/OpenBSD/NetBSD support
* MacOS support
