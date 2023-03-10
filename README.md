# DevWatch

Speed up your coding by running your program, test suite, linter, etc on every saved changes. 


## Installation

```
$ pip install devwatch
```

## System requirements
* Linux >= 2.6.13
* Python >= 3.2

## Basic usage

### Execute **python main.py** when **main.py** is modified
  ```
  $ devwatch -f 'main.py' -c 'python main.py'
  ```

### Watch for changes on all **.txt** files inside **dir** and its subdirectories and execute **cat** on the modified file
  ```
  $ devwatch -f 'dir/**/*.txt' -c 'cat @'
  ```

### Execute **main** target
```
$ devwatch -t main
```

### Execute the first defined target
```
$ devwatch
```

## Configuration file

Create **.devwatchrc.yml** on your project directory or home folder

### Example configuration file

```yml
   main:
       files: main.py
       command: python main.py    
   tests:
       files: tests/
       command: pytest @
   flake:
       files: main.py
       command: flake8 test.py
```

   * Define targets (**main**, **tests** and **flake** in this example)
   * For every target define:
     * **files**: File or directory to watch

     * **command**: Command to execute when a file change is detected
   * When watching on directories like on target **tests**, you can use **@** to reference the
     modified file. In that example, when file **tests/foo.py** is amended **pytest tests/foo.py**
     will be execute

   * Warning: if no files exists for the target, the program will exit. 

## Tested on
* Ubuntu 20.04, 22.04 x64
* Debian 11 x64
* Centos 7 x84

## TODO
* Hot reload configuration file
* FreeBSD/OpenBSD/NetBSD support
* MacOS support
