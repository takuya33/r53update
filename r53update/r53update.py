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
# See the License for the specific language governing permissions and
# limitations under the License.
# 
from boto.route53.connection import Route53Connection
from boto.route53.record import ResourceRecordSets
from botocore.session import Session
from pkg_resources import get_distribution

import sys
import argparse
import urllib2
import dns.resolver
import dns.exception
import logging
import logging.handlers
import netifaces
import exceptions

try:
	import argcomplete
	has_autocomplete = True
except:
	has_autocomplete = False

## 
# Application Framework
class App(object):
	class ArgumentParser(argparse.ArgumentParser):
		def error(self, message):
			self._print_message('[31merror: %s[0m\n\n' % message)
			self.print_help()
			sys.exit(2)

		def _print_message(self, message, file=None):
			if message:
				sys.stderr.write(message)

	class VersionAction(argparse.Action):
		def __init__(
			self, option_strings, version_callback,
			dest=argparse.SUPPRESS,
			default=argparse.SUPPRESS,
			help="show program's version number and exit"):

			super(App.VersionAction, self).__init__(
				option_strings=option_strings,
				dest=dest,
				default=default,
				nargs=0,
				help=help)

			self.__version_callback = version_callback
	
		def __call__(self, parser, namespace, values, option_string=None):
			self.__version_callback()
			sys.exit(0)

	def __init__(self, argv):
		self.__argv = argv
		self.logger = logging.getLogger(self.__argv[0])

	def _pre_init(self):
		self._parser = App.ArgumentParser()
		self._parser.add_argument('-v', '--version', action=App.VersionAction,
			version_callback=self.show_version, help='show version info')

	def _post_init(self, opts):
		pass

	def _init(self):
		self._pre_init()

		if has_autocomplete:
			# eval "$(register-python-argcomplete r53update)"
			# Ref) https://pypi.python.org/pypi/argcomplete
			argcomplete.autocomplete(self._parser)

		opts = self._parser.parse_args(self.__argv[1:])
		self._post_init(opts)

	def _run(self):
		pass

	def show_version(self):
		pass

	def show_usage(self):
		self._parser.print_help()

	def __call__(self):
		try:
			self._init()
			self._run()
		except Exception, e:
			print >>sys.stderr, "[31m%s[0m" % e
			sys.exit(1)

##
# Application Implementation
class R53UpdateApp(App):
	##
	# Context
	class Context(object):
		def __init__(self, profile=''):
			self.session = Session()
			self.session.profile = profile
	
		def getR53Connection(self):
			return Route53Connection(
				self.session.get_scoped_config()['aws_access_key_id'],
				self.session.get_scoped_config()['aws_secret_access_key']
			)

	##
	# Argument Completer
	class ProfileCompleter(object):
		def __init__(self, parent):
			self.__parent = parent
		
		def __call__(self, prefix, **kwargs):
			profiles = self.__parent.ctx.session.available_profiles
			return (x for x in profiles if x.startswith(prefix))

	##
	# Netifaces Completer
	class NetifacesCompleter(object):
		def __init__(self, parent):
			self.__parent = parent

		def __call__(self, prefix, **kwargs):
			return (x for x in netifaces.interfaces() if x.startswith(prefix))

	# Resolver Completer
	class ResolverCompleter(object):
		def __init__(self, parent):
			self.__parent = parent

		def __call__(self, prefix, **kwargs):
			return (x for x in self.__parent._gipresolvers if x.startswith(prefix))

	##
	# Global IP Resolver
	class GlobalIP_Resolver(object):
		def __init__(self, app):
			self._app = app

		def resolveGlobalIP():
			raise NotImplementedError()

	class HTTP_GlobalIP_Resolver(GlobalIP_Resolver):
		def __init__(self, app, url):
			super(R53UpdateApp.HTTP_GlobalIP_Resolver, self).__init__(app)
			self._url = url

		def resolveGlobalIP(self):
			return urllib2.urlopen(self._url).read().rstrip()

	class DNS_GlobalIP_Resolver(GlobalIP_Resolver):
		def __init__(self, app, hostname, resolvername):
			super(R53UpdateApp.DNS_GlobalIP_Resolver, self).__init__(app)
			self._hostname = hostname
			self._resolvername = resolvername

		def resolveGlobalIP(self, ns=False):
			resolver = dns.resolver.Resolver()
			resolver.nameservers = self._app._opts.dns if ns else self.resolveGlobalIP(True)
			return map(lambda x: x.to_text(), resolver.query(self._resolvername if ns else self._hostname, 'A'))

	class NETIFACES_GlobalIP_Resolver(GlobalIP_Resolver):
		def __init__(self, app):
			super(R53UpdateApp.NETIFACES_GlobalIP_Resolver, self).__init__(app)

		def resolveGlobalIP(self):
			try:
				inet = netifaces.ifaddresses(self._app._opts.iface)[netifaces.AF_INET]
			except Exception as e:
				raise Exception("%s: no inet address found" % self._app._opts.iface)

			return map(lambda x: x['addr'], inet)

	def _pre_init(self):
		super(R53UpdateApp, self)._pre_init()
		self.ctx = R53UpdateApp.Context()
		
		# initialize logger
		self.logger.setLevel(logging.INFO)

		self._formatter = logging.Formatter(
			fmt='%(name)s[%(process)d]: %(asctime)s; [%(levelname)s] %(message)s',
			datefmt='%Y/%m/%d %p %I:%M:%S'
		)

		handler = logging.StreamHandler(sys.stderr)
		handler.setFormatter(self._formatter)
		self.logger.addHandler(handler)

		# create mapping of global ip resolvers
		self._gipresolvers = dict()
		self._gipresolvers['ifconfig.me'] = R53UpdateApp.HTTP_GlobalIP_Resolver(self, 'http://ifconfig.me/ip')
		self._gipresolvers['ipecho.net'] = R53UpdateApp.HTTP_GlobalIP_Resolver(self, 'http://ipecho.net/plain')
		self._gipresolvers['icanhazip.com'] = R53UpdateApp.HTTP_GlobalIP_Resolver(self, 'http://icanhazip.com')
		self._gipresolvers['opendns.com'] = R53UpdateApp.DNS_GlobalIP_Resolver(self, 'myip.opendns.com', 'resolver1.opendns.com')
		self._gipresolvers['localhost'] = R53UpdateApp.NETIFACES_GlobalIP_Resolver(self)

		# optional argument
		self._parser.add_argument('--profile', type=str, metavar='PROFILE', default='',
			help='プロファイル名').completer = R53UpdateApp.ProfileCompleter(self)
		self._parser.add_argument('--resolver', type=str, metavar='RESOLVER',
			default='opendns.com', help='グローバルIP 取得方法').completer = R53UpdateApp.ResolverCompleter(self)
		self._parser.add_argument('--iface', type=str, metavar='IFACE',
			help='インターフェイス名').completer = R53UpdateApp.NetifacesCompleter(self)
		self._parser.add_argument('--dns', nargs='+', type=str, metavar='DNS',
			default=['8.8.8.8', '8.8.4.4'], help='default: 8.8.8.8, 8.8.4.4')
		self._parser.add_argument('--ttl', type=int, metavar='TTL',
			default=300, help='default: 300')
		self._parser.add_argument('--dry', action='store_true')
		self._parser.add_argument('--force', action='store_true')
		self._parser.add_argument('--syslog', action='store_true')
		self._parser.add_argument('--debug', action='store_true')

		# positional argument
		self._parser.add_argument('host', type=str, metavar='HOST', help='ex) www')
		self._parser.add_argument('zone', type=str, metavar='ZONE', help='ex) fqdn.tld')

	def _post_init(self, opts):
		super(R53UpdateApp, self)._post_init(opts)
		self.ctx.session.profile = opts.profile
		self._opts = opts

		if opts.syslog:
			handler = logging.handlers.SysLogHandler(address='/dev/log')
			handler.setFormatter(self._formatter)
			self.logger.addHandler(handler)

		if opts.debug:
			self.logger.setLevel(logging.DEBUG)

		if opts.resolver == 'localhost' and not opts.iface:
			raise Exception("you must specify network interface with '--iface' option")

		if opts.iface:
			if opts.iface not in netifaces.interfaces():
				raise Exception("interface name '%s' not found" % opts.iface)
			self._opts.resolver = 'localhost'

	def __get_global_ip(self):
		self.logger.debug('resolving global ip adreess with \'%s\'', self._opts.resolver)
		gips = self._gipresolvers[self._opts.resolver].resolveGlobalIP()
		return gips if type(gips) is list else [gips]

	def __get_records_from_host(self, fqdn):
		resolver = dns.resolver.Resolver()
		resolver.nameservers = self._opts.dns
		results = []
	
		try:
			response = resolver.query(fqdn, 'A')
			results = map(lambda x: x.to_text(), response)
		except dns.resolver.NXDOMAIN:
			pass
		except dns.resolver.Timeout:
			raise
		except dns.exception.DNSException:
			raise
		
		return results

	##
	# Ref) https://gist.github.com/mariocesar/4142563
	def __update_r53_record(self, zone_name, host_name, gips):
		fqdn = '%s.%s' % (host_name, zone_name)

		conn = self.ctx.getR53Connection()
		zone = conn.get_zone(zone_name)

		if zone is None:
			raise Exception("zone '%s' not found" % zone_name)
		self.logger.debug('R53 zoneid: %s' % zone.id)

		changes = ResourceRecordSets(conn, zone.id, '')
		change = changes.add_change('UPSERT', fqdn, 'A', self._opts.ttl)

		for gip in gips:
			change.add_value(gip)

		changes.commit()

		self.logger.info('update A records of \'%s\' with \'%s\'' % (fqdn, gip))

	def _run(self):
		fqdn = '%s.%s' % (self._opts.host, self._opts.zone)
		self.logger.debug('fqdn: %s' % fqdn)

		gips = self.__get_global_ip()
		self.logger.debug('global ips: %s' % str(gips))

		arecs = self.__get_records_from_host(fqdn)
		self.logger.debug('current a records: %s' % str(arecs))

		if gips != arecs or self._opts.force:
			if not self._opts.dry:
				self.logger.debug('updating route53 zone info')
				self.__update_r53_record(
					self._opts.zone,
					self._opts.host,
					gips
				)
			else:
				self.logger.debug('updating route53 zone info (dry-run)')
		else:
			self.logger.debug('route53 zone info is up to date')

	def show_version(self):
		print >>sys.stderr, "Copyrights (c)2014 Takuya Sawada All rights reserved."
		print >>sys.stderr, "Route53Update Dynamic DNS Updater v%s" % get_distribution("r53update").version



def main():
	try:
		R53UpdateApp(sys.argv)()
	except Exception, e:
		print >>sys.stderr, "[31m%s[0m" % e
		sys.exit(1)

if __name__ == '__main__':
	main()
