#!/usr/bin/env python

# MIT License

# Copyright (c) 2019 IBM Hyperlinked Knowledge Graph

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
from setuptools import setup, find_packages

def find_recursive_packages(root):
    def _isdir(f):
        return os.path.isdir(f) and '__pycache__' not in f

    dirs = list(filter(_isdir, [os.path.join(root, f) for f in os.listdir(root)]))
    for dir_ in dirs:
        dirs += find_recursive_packages(dir_)
    
    return [dir_.replace('/', '.') for dir_ in dirs]
    
NAME = 'hkpy'
VERSION = open('version.txt', 'r').read().strip()
URL = 'https://github.ibm.com/hyperknowledge-wg/HKpy'
DESCRIPTION = 'A Python module to create software abstraction for accessing hyperknowledge graphs'
LONG_DESCRIPTION = None
AUTHOR = 'IBM Research Brazil'
AUTHOR_EMAIL = 'mmoreno@br.ibm.com'
KEYWORDS = 'Hyperknowlede, Knowledge Engineering'
REQUIRES_PYTHON = '>=3.6'
REQUIRED = [
    'requests'
]

try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    LONG_DESCRIPTION = DESCRIPTION

setup(
    name=NAME,
    version=VERSION,
    url=URL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    keywords=KEYWORDS,
    python_requires=REQUIRES_PYTHON,
    packages=find_recursive_packages('hkpy'),
    include_package_data=True,
    install_requires=REQUIRED,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ]
)