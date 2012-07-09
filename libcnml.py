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


class CNMLZone:
	def __init__(self, zid, parentid, aps=0, box=[], nclients=0, ndevices=0, nlinks=0, nservices=0, title=''):
		self.id = zid
		self.parentzone = parentid
		self.totalAPs = aps
		self.box = box
		self.totalClients = nclients
		self.totalDevices = ndevices
		self.totalLinks = nlinks
		self.totalServices = nservices
		self.title = title
		self.subzones = dict()
		self.nodes = dict()
	
	
	# @param z: CNMLZone
	def addSubzone(self, z):
		self.subzones[z.id] = z
	
	# @param z: CNMLNode
	def addNode(self, n):
		self.nodes[n.id] = n
	
	def getNodes(self):
		return self.nodes.values()
		
	def getSubzones(self):
		return self.subzones.values()
		
	# @param z: xml.dom.minidom.Element
	@staticmethod
	def parse(z):
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
#		nnodes = int(z.getAttribute('zone_nodes'))
#		nnodes is not useful --> len(nodes)				

		newzone = CNMLZone(zid, zparentid, nAPs, box, nclients, ndevices, nlinks, nservices, title)
		return newzone
		
		
class CNMLNode:
	def __init__(self, nid, title, lat, lon, nlinks, status):
		self.id = nid
		self.title = title
		self.latitude = lat
		self.longitude = lon
		self.totalLinks = nlinks
		self.status = status
		self.devices = dict()
		
	def getDevices(self):
		return self.devices.values()
		
	def addDevice(self, dev):
		self.devices[dev.id] = dev
		
	@staticmethod
	def parse(n):
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
		
		newnode = CNMLNode(nid, title, lat, lon, nlinks, status)		
		return newnode
		
		
class CNMLDevice:
	def __init__(self, did, name, firmware, status, title, dtype, parent):
		self.id = did
		self.name = name
		self.firmware = firmware
		self.status = status
		self.title = title
		self.type = dtype
		self.radios = dict()
		self.parentNode = parent
		
	def getRadios(self):
		return self.radios.values()
		
	def addRadio(self, radio):
		self.radios[radio.id] = radio
		
	@staticmethod
	def parse(d, parent):
		did = int(d.getAttribute("id"))
		name = d.getAttribute("name")
		firmware = d.getAttribute("firmware")
		status = d.getAttribute("status")
		status = Status.strToStatus(status)
		title = d.getAttribute("title")
		dtype = d.getAttribute("type")
		#nlinks = d.getAttribute('links') or 0
		#nlinks = int(nlinks)
		#por qué no tiene un atributo radios="2" en lugar de links="2"??
		
		newdevice = CNMLDevice(did, name, firmware, status, title, dtype, parent)
		return newdevice

	
	
class CNMLRadio:
	def __init__(self, rid, protocol, snmp_name, ssid, mode, gain, angle, channel, clients, parent):
		self.id = rid
		self.protocol = protocol
		self.snmp_name = snmp_name
		self.ssid = ssid
		self.mode = mode
		self.antenna_gain = gain
		self.antenna_angle = angle
		self.channel = channel
		self.clients_accepted = clients
		self.interfaces = dict()
		self.parentDevice = parent
		
	def getInterfaces(self):
		return self.interfaces.values()
	
	def addInterface(self, iface):
		self.interfaces[iface.id] = iface
	
	@staticmethod
	def parse(r, parent):
		#radio ids are 0, 1, 2...
		rid = int(r.getAttribute('id'))
		protocol = r.getAttribute('protocol')
		snmp_name = r.getAttribute('snmp_name')
		ssid = r.getAttribute('ssid')
		mode = r.getAttribute('mode')
		antenna_gain = r.getAttribute('antenna_gain')
		antenna_angle = r.getAttribute('antenna_angle')
		channel = r.getAttribute('channel') or 0 # ugly
		channel = int(channel)
		clients = r.getAttribute('clients_accepted') == 'Yes'
		
		#falta atributo interfaces="2"
		#sobra atributo device_id

		newradio = CNMLRadio(rid, protocol, snmp_name, ssid, mode, antenna_gain, antenna_angle, channel, clients, parent)
		return newradio
		
		
class CNMLInterface:
	def __init__(self, iid, ipv4, mask, mac, itype, parent):
		self.id = iid
		self.ipv4 = ipv4
		self.mask = mask
		self.mac = mac
		self.type = itype
		self.links = dict()
		self.parentRadio = parent
		
	def getLinks(self):
		return self.links.values()
		
	def addLink(self, link):
		self.links[link.id] = link
		
	@staticmethod
	def parse(i, parent):
		iid = int(i.getAttribute('id'))
		ipv4 = i.getAttribute('ipv4')
		mac = i.getAttribute('mac')
		#checkMac
		mask = i.getAttribute('mask')
		itype = i.getAttribute('type') #wLan/Lan
		
		newiface = CNMLInterface(iid, ipv4, mask, mac, itype, parent)
		
		return newiface
		

# Note that for two connected nodes there's just one link, that is,
# two different links (different linked dev/if/node) but same id
# Given a device link, how to difference which is the linked device, A or B?
class CNMLLink:
	def __init__(self, lid, status, ltype, ldid, liid, lnid, parent):
		self.id = lid
		self.status = status
		self.type = ltype
		#self.linked_device = {ldid:None}
		#self.linked_interface = {liid:None}
		#self.linked_node = {lnid:None}
		self.parentInterface = parent
		self.nodeA = lnid
		self.deviceA = ldid
		self.interfaceA = liid
		self.nodeB = None
		self.deviceB = None
		self.interfaceB = None
		
	def getLinkedNodes(self):
		return [self.nodeA, self.nodeB]
		
	def getLinkedDevices(self):
		return [self.deviceA, self.deviceB]
		
	def getLinkedInterfaces(self):
		return [self.interfaceA, self.interfaceB]
		
	def parseLinkB(self, l):
		self.nodeB = int(l.getAttribute('linked_node_id'))
		self.deviceB = int(l.getAttribute('linked_device_id'))
		self.interfaceB = int(l.getAttribute('linked_interface_id'))
		
	def setLinkedParameters(self, devs, ifaces, nodes):
		didA = self.deviceA
		iidA = self.interfaceA
		nidA = self.nodeA
		didB = self.deviceB
		iidB = self.interfaceB
		nidB = self.nodeB

		if self.nodeB is None:
			print "Couldn't find linked node (%d) in link %d. It may be defined in a different CNML zone." %(self.nodeA, self.id)
			return
			
		if devs.has_key(didA):
			self.deviceA = devs[didA]
		else:
			print 'Device id %d not found' %self.deviceA
		
		if devs.has_key(didB):
			self.deviceB = devs[didB]
		else:
			print 'Device id %d not found' %self.deviceB
		
		if ifaces.has_key(iidA):
			self.interfaceA = ifaces[iidA]
		else:
			print 'Interface id %d not found' %self.interfaceA
		
		if ifaces.has_key(iidB):
			self.interfaceB = ifaces[iidB]
		else:
			print 'Interface id %d not found' %self.interfaceB
		
		if nodes.has_key(nidA):
			self.nodeA = nodes[nidA]
		else:
			print 'Node id %d not found' %self.nodeA
		
		if nodes.has_key(nidB):
			self.nodeB = nodes[nidB]
		else:
			print 'Node id %d not found' %self.nodeB
		
	#check if the link id already exists
	@staticmethod
	def parse(l, parent):
		lid = int(l.getAttribute('id'))
		status = l.getAttribute('link_status')
		ltype = l.getAttribute('link_type')
		ldid = int(l.getAttribute('linked_device_id'))
		liid = int(l.getAttribute('linked_interface_id'))
		lnid = int(l.getAttribute('linked_node_id'))
		# Cambiar nombres:
		# link_status -> status
		# link_type -> type
		# linked_device_id -> device_id
		# linked_interface_id -> interface_id
		# linked_node_id -> node_id
							
		newlink = CNMLLink(lid, status, ltype, ldid, liid, lnid, parent)
		return newlink
		

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
		self.radios = None
		self.ifaces = None
		self.links = None
		
		if not lazy:
			self.load()
		else:
			self.loaded = False
	
	

	def getInterfaces(self):
		return self.ifaces.values()
		
	def getNodes(self):
		return self.nodes.values()
		
	def getZones(self):
		return self.zones.values()
		
	def getDevices(self):
		return self.devices.values()
	
	def getRadios(self):
		return self.radios.values()
	
	def getInterfaces(self):
		return self.ifaces.values()
		
	def getLinks(self):
		return self.links.values()
		
	def load(self, extracheck=True):
		tree = MD.parse(self.filename)
	
		# --zones--
		zones = tree.getElementsByTagName("zone")
		self.zones = dict()
		self.nodes = dict()
		self.devices = dict()
		self.radios = dict()
		self.ifaces = dict()
		self.links = dict()
		
		
		self.rootzone = int(zones[0].getAttribute("id"))
		
		for z in zones:
			zid = int(z.getAttribute("id"))
			newzone = CNMLZone.parse(z)
			self.zones[zid] = newzone
			zparentid = newzone.parentzone
			
			if zid != self.rootzone and zparentid != None:
				self.zones[zparentid].addSubzone(newzone)
		
		
		# --nodes--
		for n in tree.getElementsByTagName("node"):
			nid = int(n.getAttribute("id"))
			zid = int(n.parentNode.getAttribute('id'))
			newnode = CNMLNode.parse(n)
			self.nodes[nid] = newnode
			self.zones[zid].addNode(newnode)
					
			#assert n.parentNode.localName == u'zone'
			#assert(ndevices == len(devicestree))
			
			# --devices--			
			for d in n.getElementsByTagName("device"):
				did = int(d.getAttribute("id"))
				newdevice = CNMLDevice.parse(d, newnode)
				self.devices[did] = newdevice
				self.nodes[nid].addDevice(newdevice)
				
				# --radios--
				for r in d.getElementsByTagName("radio"):
					rid = int(r.getAttribute('id'))
					newradio = CNMLRadio.parse(r, newdevice)
					self.devices[did].addRadio(newradio)
					
					# --interfaces--
					for i in r.getElementsByTagName("interface"):
						iid = int(i.getAttribute('id'))
						newiface = CNMLInterface.parse(i, newradio)
						self.ifaces[iid] = newiface
						self.devices[did].radios[rid].addInterface(newiface)
						
						# --links--
						for l in i.getElementsByTagName("link"):
							lid = int(l.getAttribute('id'))
							
							if self.links.has_key(lid):
								self.links[lid].parseLinkB(l)
								self.ifaces[iid].addLink(self.links[lid])
							else:
								newlink = CNMLLink.parse(l, newiface)
								self.links[lid] = newlink
								self.ifaces[iid].addLink(newlink)
							

		# Replace None by true reference of nodes/devices/interfaces
		# Note that if they belong to a different zone they might not be defined in the CNML file
		for link in self.getLinks():
			link.setLinkedParameters(self.devices, self.ifaces, self.nodes)
		
		print 'Loaded OK'
		self.loaded = True
			
	
	def getNodesFromZone(self, zid):
		if not self.loaded:
			self.load()
		return self.zones[zid].nodes.values()
	
	
	def getSubzonesFromZone(self, zid):
		if not self.loaded:
			self.load()
		return self.zones[zid].subzones.values()
		
	def getInterface(self, iid):
		if not self.loaded:
			self.load()
		return self.ifaces[iid]
		
	def getNode(self, nid):
		if not self.loaded:
			self.load()
		return self.nodes[nid]
		
	def getZone(self, zid):
		if not self.loaded:
			self.load()
		return self.zones[zid]
		
	def getLink(self, lid):
		if not self.loaded:
			self.load()
		return self.links[lid]
		
	def getDevice(self, did):
		if not self.loaded:
			self.load()
		return self.devices[did]
		
	def getZonesNames(self):
		if not self.loaded:
			self.load()
		zones = []
		
		for z in self.getZones():
			zones.append(n['title'])
		
		return zones
		
		
	def getTitles(self):
		if not self.loaded:
			self.load()
		titles = []
		
		for n in self.getNodes():
			titles.append(n['title'])

		return titles


# <interface> cuelga de <device> WTF?!:
#	<device created="20101105 0125" firmware="AirOsv52" id="25621" name="AirMaxM2 Bullet/PwBrg/AirGrd/NanoBr" status="Working" title="MLGInvisibleRd1" type="radio" updated="20110724 0113">
#		<radio antenna_gain="8" device_id="25621" id="0" mode="client" protocol="802.11b" snmp_name="ath0" ssid="MlagaMLGnvsbltmpRd1CPE0">
#			<interface id="48981" ipv4="10.228.172.36" mac="00:15:6D:4E:AF:13" mask="255.255.255.224" type="Wan">
#				<link id="28692" link_status="Working" link_type="ap/client" linked_device_id="19414" linked_interface_id="19414" linked_node_id="26999"/>
#			</interface>
#		</radio>
#		<interface id="48981" ipv4="10.228.172.36" mac="00:15:6D:4E:AF:13" mask="255.255.255.224" type="Wan"/>
#	</device>
