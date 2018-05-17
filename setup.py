#!/usr/bin/env python
import os
import io
import re
import shutil
import sys
from setuptools import setup, find_packages

def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


readme = open('README.rst').read()

VERSION = find_version('datasets', '__init__.py')

requirements = [
    'scikit-image',
    'six',
    'torch'
]

setup(
    # Metadata
    name='CODHDatasets',
    version=VERSION,
    author='TAkauchi Planning Lab team',
    author_email='takauchikiken@gmail.com',
    url='https://github.com/TAkauchiPlanningLab/CODHDatasets',
    description='Pre-modern Japanese Texts datasets',
    long_description=readme,
    license='MIT',

    # Package info
    packages=find_packages(exclude=('test',)),

    zip_safe=True,
    install_requires=requirements,
)
