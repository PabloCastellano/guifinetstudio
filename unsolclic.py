#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# unsolclic.py - Un Sol Clic feature to generate device configurations
# Copyright (C) 2011-2012 Pablo Castellano <pablo@anche.no>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import jinja2

class UnSolClic:
	def __init__(self):
		self.env = jinja2.Environment(loader=jinja2.FileSystemLoader('unsolclic'))
		self.test1()

		print 'Supported devices:'
		print '\n'.join(self.getSupportedDevices())

	def getSupportedDevices(self):
		return self.env.list_templates()

	def test1(self):
		#Templates stuff
		# jinja2
		# {{ wireless1ssid }}
		# {{ ipv4_ip }}
		# {{ ipv4_netmask }}
		# {{ wangateway }}
		# {{ zone_primary_dns }}
		# {{ zone_secondary_dns }}
		# {{ dev.nick }}
		# {{ node_nick }}
		# {{ radio1txpower }}
		context = {'wireless1ssid':'myessid', 'ipv4_ip':'192.168.33.33', \
			   'ipv4_netmask':'255.0', 'wangateway':'gateee', \
			   'zone_primary_dns':'dns1', 'zone_secondary_dns':'dns2', \
			   'dev':{'nick':'mYnick'}, 'node_nick':'nicker',
			   'radio1txpower':'8W'
			   }
		t = self.env.get_template('AirOsv30')
		print t.render(context)

