#!/usr/bin/env python3
# region Imports
import os
import sys
import pathlib
import setuptools

# endregion
# region Basic Information
here = os.path.abspath(os.path.dirname(__file__))

NAME = "ptmux"
AUTHOR = 'Miles Frantz'
EMAIL = 'frantzme@vt.edu'
DESCRIPTION = 'My short description for my project.'
GH_NAME = "franceme"
URL = f"https://github.com/{GH_NAME}/{NAME}"
long_description = pathlib.Path(f"{here}/README.md").read_text(encoding='utf-8')
REQUIRES_PYTHON = '>=3.8.0'
RELEASE = "?"
VERSION = "0.0.3"
# endregion
# region Setup

setuptools.setup(
	name=NAME,
	version=VERSION,
	description=DESCRIPTION,
	long_description=long_description,
	long_description_content_type='text/markdown',
	author=AUTHOR,
	author_email=EMAIL,
	command_options={
	},
	python_requires=REQUIRES_PYTHON,
	url=URL,
	packages=setuptools.find_packages(
		exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
	),
	entry_points={
	},
	install_requires=[
		"libtmux",
	],
	include_package_data=True,
	classifiers=[
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.8',
	],
)
# endregion
