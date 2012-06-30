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
		print
		
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
		r = t.render(context)
		#print r
		return r
		
	def generate(self, model, data):
		if model not in self.getSupportedDevices():
			raise NotImplementedError
		t = self.env.get_template(model)
		
		print "1:", data

	
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
		
		r = t.render(context)
		
		# print r
		return r

# --- DD-guifi ---
# dev.nick
# ipv4.ipv4
# ipv4.netmask
# ipv4.netstart
# zone_primary_dns
# zone_secondary_dns
# zone_ternary_dns
# txpwr
# antena_mode
# zone_primary_ntp
# dev.radios[0][''channel'']
# guifi_to_7bits(dev.radios[0][''ssid''])
# {{ _self.guifi_unsolclic_ospf(dev, zone, ospfzone,interfaceWlanLan) }}
# {{ _self.guifi_unsolclic_dhcp(dev, interfaceWlanLan) }}
# {{ _self.guifi_unsolclic_wds_vars(dev) }}
# {{ dev.radios[0].ssid }}
# gateway
# filter
# {{ _self.guifi_unsolclic_vlan_vars(dev, rc_startup) }}
# {{ _self.guifi_unsolclic_startup(dev, version, rc_startup) }}
# ipv4Addr
# dev.variable.firmware
# aIf
# interfaceWlanLan.ipv4[0].ipv4
# ipv4.netid
# ipv4.maskbits
# link.interface.mac
# link.interface.ipv4.host_name
# link.interface.ipv4.ipv4
# link.interface.ipv4.netmask 
# count
#  dhcp_start
# link.interface.device_id }}-{{ hostname
# ifcount
# key
# wds_str
# dev.id
# rc_startup

# --- RouterOS4.0 ---
# host_name, ipv4, disabled, iname, netid, maskbits, ospf_name, firmware_name
# dev.id, dev.nick, firmware_description, zone_id, zone_primary_dns, zone_secondary_dns
# zone_primary_ntp, zone_secondary_ntp, snmp_contact, node_name
# dev.logserver, dev.radios[0].ipv4, dev.radios[0].ipv4, radio.radiodev_counter, radio.ssid
# radio.mode, radio.channel, radio.antenna_gain, channel, antena_mode
# interface.interface_type, radio_id, disabled, link.interface.ipv4.host_name
# ipv4.ipv4, ipv4.maskbits, ipv4.netid, ipv4.broadcast, link.interface.ipv4.host_name, disabled, link.interface.ipv4.host_name
# link.routing
# _self.ospf_interface(''wds_'' ~ link.interface.ipv4.host_name , ipv4.netid , ipv4.maskbits , ospf_name , ospf_zone, ospf_id, ''no'') }}
# {{ _self.bgp_peer(link.device_id, link.interface.ipv4.host_name, link.interface.ipv4.ipv4, ''yes'') }}
# radio.id, rmac, ospf_routerid, ospf_routerid

# --- RouterOS5.0 ---

