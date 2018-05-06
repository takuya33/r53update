#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# R53Update Dynamic DNS Updater
# (C)2014 Takuya Sawada All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
# 
from setuptools import setup

setup(
	name = 'r53update',
	version='0.6.0',
	description='R53Update Dynamic DNS Updater',
	author='Takuya Sawada',
	author_email='takuya@tuntunkun.com',
	url='https://github.com/tuntunkun/r53updaten',
	license='Apache License 2.0',
	packages = ['r53update'],
	install_requires = [
		'argparse2==0.5.0a1',
		'boto3==1.4.4',
		'dnspython==1.15.0',
		'netifaces==0.10.6'
	],
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Operating System :: POSIX',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Topic :: System :: Networking',
		'Topic :: Utilities'
	],
	entry_points = {
		'console_scripts': [
			'r53update=r53update:main'
		]
	}
)
