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
    Execute `main` target

`devwatch -f 'dir/**/*.txt' -c 'cat @'`
    Watch for changes on all `.txt` files inside `dir` and its subdirectories and execute `cat` on the modified file

`devwatch`
    Execute the first defined target

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

===========
Inspired by
===========
https://github.com/chrisjbillington/inotify_simple

====
TODO
====
* Replace pyyaml for stdlib library package
* Check for maximum number of files to watch
* Hot reload configuration file
* FreeBSD/OpenBSD/NetBSD support
* MacOS support
* Autocomplete
* Github actions
