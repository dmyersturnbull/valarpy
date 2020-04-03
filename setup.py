#!/usr/bin/env python3
# coding=utf-8

from pathlib import Path
from distutils.core import setup
from valarpy import valarpy_version

readme = Path('README.md').read_text(encoding='utf8')

setup(
	name='valarpy',
	version=valarpy_version,
	description='Python connection code to Valar',
	long_description=readme,
	long_description_content_type='text/markdown',
	author='Douglas Myers-Turnbull',
	maintainer='Douglas Myers-Turnbull',
	url='https://github.com/kokellab/valarpy',
	entry_points={'console_scripts': ['valarpy = valarpy.Valar:main']},
	packages=['valarpy'],
	test_suite='tests',
	zip_safe=False,
	classifiers=[
		"Development Status :: 5 - Production",
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'Natural Language :: English'
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Topic :: Scientific/Engineering :: Bio-Informatics',
		'Topic :: Scientific/Engineering :: Chemistry',
		'Topic :: Database',
		'Typing :: Typed'
	]
)

