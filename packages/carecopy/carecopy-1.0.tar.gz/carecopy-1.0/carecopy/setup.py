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
carecopy: A simple file copy and comparison tool that allows to copy files and directories, compare files and directories, and estimate the time it will take to copy files.
version = 1.0
"""

setup(name='carecopy',
      version=version,
      description="carecopy: A simple file copy and comparison tool that allows to copy files and directories, compare files and directories, and estimate the time it will take to copy files.",
      long_description=README,
      long_description_content_type='text/markdown',
      author='cycleuser',
      author_email='cycleuser@cycleuser.org',
      url='http://blog.cycleuser.org',
      packages=['carecopy'],
      install_requires=[ 
                        "pyside6",
                         ],
     )