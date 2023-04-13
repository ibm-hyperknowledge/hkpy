###
# Copyright (c) 2019-present, IBM Research
# Licensed under The MIT License [see LICENSE for details]
###

import os

import setuptools
from setuptools import setup, find_packages


def find_recursive_packages(root):
    def _isdir(f):
        return os.path.isdir(f) and '__pycache__' not in f

    dirs = list(filter(_isdir, [os.path.join(root, f) for f in os.listdir(root)]))
    for dir_ in dirs:
        dirs += find_recursive_packages(dir_)
    
    return [dir_.replace('/', '.') for dir_ in dirs]


NAME = 'hkpy'
VERSION = open('./version.txt', 'r').read().strip()
URL = 'https://github.com/ibm-hyperknowledge/hkpy'
DESCRIPTION = 'A Python module to create software abstraction for accessing hyperknowledge graphs'
LONG_DESCRIPTION = None
AUTHOR = 'IBM Research Brazil'
AUTHOR_EMAIL = 'mmoreno@br.ibm.com'
KEYWORDS = 'Hyperknowlede, Knowledge Engineering'
REQUIRES_PYTHON = '>=3.6'
REQUIRED = [
    'requests',
    'pika',
    'Flask',
    'flask-cors',
    'PyJWT',
    'urllib3',
    'idna',
    'chardet',
    'certifi',
    'lark'
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
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    keywords=KEYWORDS,
    python_requires=REQUIRES_PYTHON,
    packages=setuptools.find_packages(),
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