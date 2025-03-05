#!/usr/bin/python

from setuptools import setup, find_packages
PACKAGE = "tclients_sdk"
DESCRIPTION = "cloud client"
VERSION = '1.0.2'

def readme():
    with open('README.md', encoding='utf-8') as f:
        content = f.read()
    return content

setup_args = {
    'version': VERSION,
    'description': DESCRIPTION,
    'license': "Apache License 2.0",
    'packages': find_packages(exclude=["tests*"]),
    'long_description': readme(),
    'long_description_content_type': 'text/markdown',
    'platforms': 'any',
    'install_requires': ["requests>=2.16.0","snapshot-photo"],
    'classifiers': (
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development',
    )
}

setup(name='tclients-sdk', **setup_args)
