#!/usr/bin/env python3
# coding=utf-8

import re
import sys

from setuptools import find_packages, setup

if sys.version_info[:3] < (3, 4):
	sys.exit("gmusicapi-wrapper does not support this version of Python.")

# From http://stackoverflow.com/a/7071358/1231454
version_file = "gmusicapi_scripts/__init__.py"
version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"

version_file_contents = open(version_file).read()
match = re.search(version_re, version_file_contents, re.M)

if match:
    version = match.group(1)
else:
    raise RuntimeError("Could not find version in '{}'".format(version_file))

setup(
	name='gmusicapi_scripts',
	version=version,
	description='A collection of scripts using gmusicapi-wrapper and gmusicapi.',
	url='https://github.com/thebigmunch/gmusicapi-scripts',
	license='MIT',
	author='thebigmunch',
	author_email='mail@thebigmunch.me',

	keywords=[],
	classifiers=[
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
	],

	install_requires=[
		'gmusicapi-wrapper >= 0.4.0',
		'docopt-unicode'
	],

	packages=find_packages(),
	entry_points={
		'console_scripts': [
			'gmdelete=gmusicapi_scripts.gmdelete:main',
			'gmdownload=gmusicapi_scripts.gmdownload:main',
			'gmsearch=gmusicapi_scripts.gmsearch:main',
			'gmsync=gmusicapi_scripts.gmsync:main',
			'gmupload=gmusicapi_scripts.gmupload:main'
		]
	},
)
