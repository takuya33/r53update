#!/bin/env python
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
# See the License for the specific language governing permissions and
# limitations under the License.
# 
from r53update import R53UpdateApp
import dns.resolver
import netifaces
import unittest
import random
import mock
import io

class TestMethod(unittest.TestCase):
	def randomIP(self):
		return u'%d.%d.%d.%d' % tuple(int(random.random()*255) for _ in range(4))

	def test_HTTP_Method(self):
		IPADDR = self.randomIP()
		SERVER = u'http://ifconfig.me/'

		with mock.patch('six.moves.urllib.request.urlopen', return_value=io.StringIO(IPADDR)) as urlopen:
			method = R53UpdateApp.HTTP_GlobalIP_DetectionMethod(None, SERVER)
			self.assertEqual(method.resolveGlobalIP(), IPADDR)
			urlopen.assert_called_once_with(SERVER)

	def test_DNS_Method(self):
		RETVAL = [ self.randomIP() for _ in range(4) ]

		app = mock.MagicMock()
		app._opts.dns = ['8.8.8.8', '8.8.4.4']

		with mock.patch.object(dns.resolver.Resolver, 'query', return_value=RETVAL) as query:
			method = R53UpdateApp.DNS_GlobalIP_DetectionMethod(app, 'myip.opendns.com', 'resolver1.opendns.com')
			self.assertListEqual(method.resolveGlobalIP(), RETVAL)
			query.has_calls(['resolver1.opendns.com', 'myip.opendns.com'])

	def test_NETIFACES_Method(self):
		RETVAL = {
			netifaces.AF_INET: [
				{
					'addr': self.randomIP(),
					'netmask': self.randomIP(),
					'broadcast': self.randomIP()
				} for _ in range(4)
			]
		}

		app = mock.MagicMock()
		app._opts.iface = 'eth0'

		with mock.patch('netifaces.ifaddresses', return_value=RETVAL) as ifaddresses:
			method = R53UpdateApp.NETIFACES_GlobalIP_DetectionMethod(app)
			self.assertListEqual(method.resolveGlobalIP(), [x['addr'] for x in RETVAL[netifaces.AF_INET]])
			ifaddresses.assert_called_once_with(app._opts.iface)
