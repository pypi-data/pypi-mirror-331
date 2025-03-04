#!/usr/bin/env python

version="1.0"
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


here = os.path.abspath(os.path.dirname(__file__))

# Fix the encoding issue by explicitly specifying UTF-8
try:
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        README = f.read()
except UnicodeDecodeError:
    # Fallback in case README.md has encoding issues
    README = """
pynettool: A command line tool that displays information about the Internet connection of current system
version = 1.0
"""

setup(name='pynettool',
      version=version,
      description="pynettool: A command line tool that displays information about the Internet connection of current system",
      long_description=README,
      long_description_content_type='text/markdown',
      author='cycleuser',
      author_email='cycleuser@cycleuser.org',
      url='http://blog.cycleuser.org',
      packages=['pynettool'],
      install_requires=[ 
                        "speedtest-cli",
                        "tabulate",
                        "requests",
                        "distro"
                         ],
     )