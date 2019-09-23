#!/usr/bin/env python3
# coding=utf-8

from distutils.core import setup
from valarpy import valarpy_version

setup(
	name='valarpy',
	version=valarpy_version,
	description='Python connection code to Valar',
	author='Douglas Myers-Turnbull',
	url='https://github.com/kokellab/valarpy',
	packages=['valarpy'],
	test_suite='tests',
	classifiers=[
		"Development Status :: 5 - Production",
		'Intended Audience :: Science/Research',
		'Natural Language :: English'
		'Operating System :: POSIX',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.7',
		'Topic :: Scientific/Engineering :: Bio-Informatics'
	]
)
d