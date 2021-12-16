#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from setuptools import find_packages, setup

sys.path.insert(0, 'src')
from atomicfileio import __version__

with open('README.md', 'rb') as readme_file:
    readme = readme_file.read().decode('utf-8')

requirements = []
test_requirements = ['pytest', 'pylama', 'six']
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
setup_requirements = ['pytest-runner'] if needs_pytest else []
extra_requirements = {'proxy': ['PySocks']}

if sys.version_info < (3, 0):
    raise RuntimeError('Python 3 is required')

setup(
    name='atomicfileio',
    version=__version__,
    description='Atomic overwrite of files',
    long_description=readme,
    author='Sam McKelvie',
    author_email='dev@mckelvie.org',
    url='http://mckelvie.org',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=requirements,
    license='MIT License v1.0',
    zip_safe=False,
    keywords='atomic file rename',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Operating System :: Linux',
        'Operating System :: POSIX',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: System :: Filesystems',
        'Topic :: Utilities',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    extras_require=extra_requirements,
    entry_points={
        'console_scripts': ['atomic-overwite=atomicfileio.cmd:main'],

    },
    scripts=[
      ],
)
