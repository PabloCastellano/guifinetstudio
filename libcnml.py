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
		
class CNMLParser():
	def __init__(self, filename, lazy=False):
		self.filename = filename
		self.nodes = None
		self.zones = None
		self.parentzone = 0
		
		if not lazy:
			self.load()
		else:
			self.loaded = False
	
	
	def load(self, extracheck=True):
		tree = MD.parse(self.filename)
	
		# --zones--
		zones = tree.getElementsByTagName("zone")
		self.zones = dict()
		
		self.parentzone = int(zones[0].getAttribute("id"))
		print 'parent zone:', self.parentzone
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
			nnodes = int(z.getAttribute('zone_nodes'))
				
			self.zones[zid] = {'parent':zparentid, 'aps':nAPs, 'box':box, 'nclients':nclients, 
							'ndevices':ndevices, 'nlinks':nlinks, 'nservices':nservices, 'title':title, 
							'nnodes':nnodes, 'subzones':[], 'nodes':[]}
			
			if zid != self.parentzone and zparentid != None:
				print zparentid, ' -- ', zid
				self.zones[zparentid]['subzones'].append(zid)
		
		
		# --nodes--
		nodes = tree.getElementsByTagName("node")
		self.nodes = dict()
		
		for n in nodes:
			nid = int(n.getAttribute("id"))
			lat = float(n.getAttribute("lat"))
			lon = float(n.getAttribute("lon"))
			title = n.getAttribute('title')
			ndevices = n.getAttribute('devices') or 0
			ndevices = int(ndevices)
			nlinks = n.getAttribute('links') or 0
			nlinks = int(nlinks)
			status = n.getAttribute('status')
			
			devicestree = n.getElementsByTagName("device")
			
			if extracheck:
				assert(ndevices == len(devicestree))
			
			devs = dict()
			for d in devicestree:
				did = int(d.getAttribute("id"))
				firmware = d.getAttribute("firmware")
				name = d.getAttribute("name")
				status = d.getAttribute("status")
				title = d.getAttribute("title")
				dtype = d.getAttribute("type")
				
				devs[did] = {'firmware':firmware, 'name':name, 'status':status, 'title':title, 'type':dtype}
					
			self.nodes[nid] = {'lat':lat, 'lon':lon, 'title':title, 'ndevices':ndevices, 'nlinks':nlinks, 'status':status}
			self.nodes[nid]['devices'] = devs

			assert n.parentNode.localName == u'zone'
			zid = int(n.parentNode.getAttribute('id'))
			self.zones[zid]['nodes'].append(nid)
				
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
	
	
def getCoords(filename):
	tree = MD.parse(filename)
	nodes = tree.getElementsByTagName("node")
	coords = []

	for i in nodes:
		c = (float(i.getAttribute("lat")), float(i.getAttribute("lon")))
		coords.append(c)
#		print c[0], c[1]

	return coords


def getCoords_with_name(filename):
	tree = MD.parse(filename)
	nodes = tree.getElementsByTagName("node")
	coords = []

	for i in nodes:
		c = (float(i.getAttribute("lat")), float(i.getAttribute("lon")), i.getAttribute('title'))
		coords.append(c)
#		print c[0], c[1], c[2]

	return coords


if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: %s <detail_file>" %(sys.argv[0])
		filename = 'tests/detail.3'
	#	sys.exit(1)
	else:
		filename = sys.argv[1]

	cnmlp = CNMLParser(filename)
	d = cnmlp.getData()

	print d
	print
	print d[26997]
	print d[26997]['ndevices']
	print d[26997]['devices']
	print d[26997]['devices'].keys()
	print cnmlp.getTitles()
