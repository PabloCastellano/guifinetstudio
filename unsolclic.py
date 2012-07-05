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
	
	NANOSTATION2 = 0
	NANOSTATION_LOCO2 = 1
	NANOSTATION5 = 2
	NANOSTATION_LOCO5 = 3
	#"AirMaxM2 Bullet/PwBrg/AirGrd/NanoBr"
	
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
		

	def generateContextAirOSv30(self, node, deviceid):
		device = node.devices[deviceid]
		
		assert len(device.radios) <= 1
			
		for radio in device.getRadios():
			assert len(radio.interfaces) <= 1
				
			for iface in radio.getInterfaces():
				assert len(iface.links) <= 1
					
				ipv4_ip = iface.ipv4			##
				ipv4_netmask = iface.mask		##
				
				for link in iface.getLinks():
					remote_if = link.interfaceB
					print remote_if
					remote_radio = remote_if.parentRadio
					print remote_radio
					
					ssid = remote_radio.ssid
					gateway = remote_if.ipv4
		
		print device.name
		if device.name == 'NanoStation2':
			(net_mode, rate_max, txpower, ack, ext_antenna, mcastrate) = ('b', '11M', '6', '45', 'disabled', '11')
		elif device.name == 'NanoStation5':
			(net_mode, rate_max, txpower, ack, ext_antenna, mcastrate) = ('a', '54M', '6', '25', 'disabled', '54')
		elif device.name == 'NanoStation Loco2':
			(net_mode, rate_max, txpower, ack, ext_antenna, mcastrate) = ('b', '11M', '6', '44', 'enabled', '11')
		elif device.name == 'NanoStation Loco5':
			(net_mode, rate_max, txpower, ack, ext_antenna, mcastrate) = ('a', '54M', '6', '25', 'disabled', '54')
		else:
			# 'AirMaxM2 Bullet/PwBrg/AirGrd/NanoBr'
			(net_mode, rate_max, txpower, ack, ext_antenna, mcastrate) = ('a', '54M', '6', '25', 'disabled', '54')
			#raise NotImplementedError
		
		radio1txpower = '6'
		dev = {'nick':device.title}
		node_nick = node.title
		radio_rx = radio_tx = 2 #antenna_mode is not available in CNML, what is this for?
		
		# -- AirOsv30 --
		# zone_primary_dns, zone_secondary_dns
		context = {'wireless1ssid':ssid, 'ipv4_ip':ipv4_ip, 'ipv4_netmask':ipv4_netmask,
				'wangateway':gateway, 'zone_primary_dns':'', 'zone_secondary_dns':'',
				'dev':dev, 'node_nick':node_nick, 'radio1txpower':radio1txpower, 'net_mode':net_mode,
				'rate_max':rate_max, 'ack':ack, 'ext_antenna':ext_antenna, 'mcastrate':mcastrate,
				'radio_rx':radio_rx, 'radio_tx':radio_tx
				}
		
		return context
	
	
	def generateContext(self, node, deviceid, template_name):
		
		if template_name in ('AirOsv30',):
			context = self.generateContextAirOSv30(node, deviceid)
		else:
			raise NotImplementedError
		
		return context
	
	
	# En el cnml
	# en Nanostation clientes <radio ssid="MlagaMLGnvsbltmpRd1CPE0"> no se usa
	# solo se usa el ssid de la antena a la que se conecta.
	def generate(self, node):
		
		for dev in node.getDevices():
			
			if dev.type != 'radio': # server, ...
				continue
				
			print 'Firmware:', dev.firmware
			if dev.firmware in ('AirOsv3.6+','AirOsv52'):
				template_name = 'AirOsv30'
			else:
				#if dev.firmware not in self.getSupportedDevices():
				raise NotImplementedError
				
			t = self.env.get_template(template_name)
			
			context = self.generateContext(node, dev.id, template_name)
		#if device.name = NANOSTATION2...
		#elif device.name= NANONSTATION_LOCO5...
		
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

