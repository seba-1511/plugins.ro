#!/usr/bin/env python

from setuptools import (
        setup,
        find_packages,
        )

VERSION = '0.0.1'

setup(
        name='randopt_plugins',
        packages=find_packages(),
        version=VERSION,
        description='Various plugins for randopt',
        author='Seb Arnold',
        author_email='smr.arnold@gmail.com',
        url = 'https://github.com/seba-1511/randopt',
        download_url = 'https://github.com/seba-1511/randopt_plugins/archive/0.0.1.zip',
        license='License :: OSI Approved :: Apache Software License',
        classifiers=[],
        scripts=[],
        install_requires=open('requirements.txt', 'r').read().split('\n'),
)
