#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# libcnml.py - CNML library 
# Copyright (C) 2012 Pablo Castellano <pablo@anche.no>
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

import xml.dom.minidom as MD
import sys

# Examples:
#self.nodes[99]['name']
#self.nodes[99]['lat']
#self.nodes[99]['lon']
#self.nodes[99]['ndevices'] // ndevices podria ser una lista con los ids
#self.nodes[99]['devices']
#self.nodes[99]['devices'][deviceid]
#self.nodes[99]['devices'][deviceid]['status']
#self.nodes[99]['devices'][deviceid]['firmware']


class Status:
	UNKNOWN = 0
	PLANNED = 1
	WORKING = 2
	TESTING = 3
	BUILDING = 4
	
	@staticmethod
	def strToStatus(status):
		st = Status.UNKNOWN
		
		if status.lower() == "planned":
			st = Status.PLANNED
		elif status.lower() == "working":
			st = Status.WORKING
		elif status.lower() == "testing":
			st = Status.TESTING
		elif status.lower() == "building":
			st = Status.BUILDING

		return st
	

class CNMLParser():
	def __init__(self, filename, lazy=False):
		self.filename = filename
		self.rootzone = 0
		
		self.nodes = None
		self.zones = None
		self.devices = None
		self.ifaces = None
		self.radios = None
		self.links = None
		
		if not lazy:
			self.load()
		else:
			self.loaded = False
	
	
	def load(self, extracheck=True):
		tree = MD.parse(self.filename)
	
		# --zones--
		zones = tree.getElementsByTagName("zone")
		self.zones = dict()
		self.nodes = dict()
		self.devices = dict()
		self.ifaces = dict()
		self.radios = dict()
		self.links = dict()
		
		self.rootzone = int(zones[0].getAttribute("id"))
		print 'parent zone:', self.rootzone
		print 'numero de zonas:', len(zones)
		
		for z in zones:
			zid = int(z.getAttribute("id"))
			try:
				zparentid = int(z.getAttribute("parent_id"))
			except:
				# guifi.net World doesn't have parent_id
				zparentid = None
			
			nAPs = z.getAttribute("access_points") or 0
			nAPs = int(nAPs)
			box = z.getAttribute("box").split(',')
			box = [box[:2], box[2:]]
			nclients = z.getAttribute("clients") or 0
			nclients = int(nclients)
			ndevices = z.getAttribute('devices') or 0
			ndevices = int(ndevices)
			nlinks = z.getAttribute('links') or 0
			nlinks = int(nlinks)
			nservices = z.getAttribute('services') or 0
			nservices = int(nservices)
			title = z.getAttribute('title')
#			nnodes = int(z.getAttribute('zone_nodes'))
#			nnodes is not useful --> len(nodes)				

			self.zones[zid] = {'parent':zparentid, 'aps':nAPs, 'box':box, 'nclients':nclients, 
							'ndevices':ndevices, 'nlinks':nlinks, 'nservices':nservices, 'title':title, 
							'subzones':[], 'nodes':[]}
			
			if zid != self.rootzone and zparentid != None:
				print zparentid, ' -- ', zid
				self.zones[zparentid]['subzones'].append(zid)
		
		
		# --nodes--
		nodes = tree.getElementsByTagName("node")
		
		for n in nodes:
			nid = int(n.getAttribute("id"))
			lat = float(n.getAttribute("lat"))
			lon = float(n.getAttribute("lon"))
			title = n.getAttribute('title')
			#ndevices = n.getAttribute('devices') or 0
			#ndevices = int(ndevices)
			nlinks = n.getAttribute('links') or 0
			nlinks = int(nlinks)
			status = n.getAttribute('status')
			status = Status.strToStatus(status)
			
			self.nodes[nid] = {'lat':lat, 'lon':lon, 'title':title, 'nlinks':nlinks, 'status':status, 'devices':[]}
			
			zid = int(n.parentNode.getAttribute('id'))
			self.zones[zid]['nodes'].append(nid)
			
			# devices							
			devicestree = n.getElementsByTagName("device")
			#assert(ndevices == len(devicestree))			
			assert n.parentNode.localName == u'zone'
			devs = dict()
			
			for d in devicestree:
				did = int(d.getAttribute("id"))
				firmware = d.getAttribute("firmware")
				name = d.getAttribute("name")
				status = d.getAttribute("status")
				status = Status.strToStatus(status)
				title = d.getAttribute("title")
				dtype = d.getAttribute("type")
				#nlinks = d.getAttribute('links') or 0
				#nlinks = int(nlinks)
				#por qué no tiene un atributo radios="2" en lugar de links="2"??
				
				self.devices[did] = {'firmware':firmware, 'name':name, 'status':status, 'title':title, 'type':dtype, 'radios':[]}
				
				self.nodes[nid]['devices'].append(did)
				
				# radios
				radiostree = d.getElementsByTagName("radio")
				radios = dict()
				for r in radiostree:
					#print r
					rid = r.getAttribute('id')
					protocol = r.getAttribute('protocol')
					snmp_name = r.getAttribute('snmp_name')
					ssid = r.getAttribute('ssid')
					mode = r.getAttribute('mode')
					antenna_gain = r.getAttribute('antenna_gain')
					antenna_angle = r.getAttribute('antenna_angle')
					#falta atributo interfaces="2"
					#sobra atributo device_id
					
					self.radios[rid] = {'protocol':protocol, 'snmp_name':snmp_name, 'ssid':ssid, 'mode':mode, 
										'antenna_gain':antenna_gain, 'antenna_angle':antenna_angle, 'interfaces':[]}
					
					self.devices[did]['radios'].append(rid)
					
					# interfaces
					ifaces = dict()
					ifacestree = r.getElementsByTagName("interface")
					for i in ifacestree:
						#print i
						iid = i.getAttribute('id')
						ipv4 = i.getAttribute('ipv4')
						mac = i.getAttribute('mac')
						#checkMac
						mask = i.getAttribute('mask')
						itype = i.getAttribute('type') #wLan/Lan
						
						self.ifaces[iid] = {'ipv4':ipv4, 'mac':mac, 'mask':mask, 'type':itype, 'links':[]}
						
						self.radios[rid]['interfaces'].append(iid)
						
						# links
						links = dict()
						linkstree = i.getElementsByTagName("link")
						
						for l in linkstree:
						#	print l
							lid = l.getAttribute('id')
							lstatus = l.getAttribute('link_status')
							ltype = l.getAttribute('link_type')
							ldid = l.getAttribute('linked_device_id')
							liid = l.getAttribute('linked_interface_id')
							lnid = l.getAttribute('linked_node_id')
							# Cambiar nombres:
							# link_status -> status
							# link_type -> type
							# linked_device_id -> device_id
							# linked_interface_id -> interface_id
							# linked_node_id -> node_id							
														
							self.links[lid] = {'status':lstatus, 'type':ltype, 'linked_device':ldid, 'linked_iface':liid, 'linked_node':lnid}
							
							self.ifaces[iid]['links'].append(lid)
							

		self.loaded = True
		
		
	def getNodesFromZone(zid):
		nodes = []
		return nodes
		
		
	def getData(self):
		if not self.loaded:
			self.load()
		return self.nodes
	
	
	def getNode(nid):
		if not self.loaded:
			self.load()
		return self.nodes[nid]
		
		
	def getZone(zid):
		if not self.loaded:
			self.load()
		return self.zones[zid]
		
		
	def getZonesNames(self):
		if not self.loaded:
			self.load()
		zones = []
		
		for z in self.zones.values():
			zones.append(n['title'])
		
		return zones
		
		
	def getTitles(self):
		if not self.loaded:
			self.load()
		titles = []
		
		for n in self.nodes.values():
			titles.append(n['title'])

		return titles


if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: %s <detail_file>" %(sys.argv[0])
		filename = 'tests/detail.3'
	#	sys.exit(1)
	else:
		filename = sys.argv[1]

	cnmlp = CNMLParser(filename)
	d = cnmlp.nodes

	print d
	print
	print d[26997]
	print d[26997]['ndevices']
	print d[26997]['devices']
	print d[26997]['devices'].keys()
	print cnmlp.getTitles()
