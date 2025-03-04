from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "1.0.9"
DESCRIPTION = "Scans file or folder to be scanned for containing Python 2 code."
LONG_DESCRIPTION = """
Checks for occurances of Python2 files in a given folder structure.
The program recursively traverses the folder structure, and if a .py file is encountered,
it is compiled with Python3.9.

Please make sure to have Python 3.9 installed, since this program specifically uses Python 3.9 to compile the files.
"""

# Setting up
setup(
    name="splupy2check",
    version=VERSION,
    entry_points={
        "console_scripts": ["splupy2check=splupy2check.splupy2check:scan_for_py"],
    },
    author="Sebastian Schimper",
    author_email="sebastianschimper@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=["argparse"],
    keywords=["python", "splunk", "python2", "scanning"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    license_files=("LICENSE",),
)
