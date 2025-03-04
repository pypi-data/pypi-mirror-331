# Splunk Python 2 Checker

Checks for occurances of Python2 files in a given folder structure.
The program recursively traverses the folder structure, and if a .py file is encountered,
it is compiled with Python3.9.

Please make sure to have Python 3.9 installed, since this program specifically uses Python 3.9 to compile the files.

## Installation

```console
pip install splupy2check
```

## Usage

```console
splupy2check [-h] [-o OUTPUT] [-v] input
```

```console
positional arguments:
  input                 File or folder to be scanned for containing Python 2 code.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Stores program output in a file.
  -v, --version         Prints the version.
```