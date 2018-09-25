#!/usr/bin/env python3
# coding=utf-8

from distutils.core import setup

setup(
	name='valarpy',
	version='1.0.0',
	description='Python connection code to Valar',
	author='Douglas Myers-Turnbull',
	url='https://github.com/kokellab/valarpy',
	packages=['valarpy'],
	test_suite='tests',
	classifiers=[
		"Development Status :: 4 - Beta",
		'Intended Audience :: Science/Research',
		'Natural Language :: English'
		'Operating System :: POSIX',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.5',
		'Topic :: Scientific/Engineering :: Bio-Informatics'
	]
)
