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

# proc XML-Tree to Dict

class CNMLParser():
	def __init__(self, filename):
		self.filename = filename
		self.data = None

	#D[99]['name']
	#D[99]['lat']
	#D[99]['lon']
	#D[99]['ndevices'] // ndevices podria ser una lista con los ids
	#D[99]['devices']
	#D[99]['devices'][deviceid]
	#D[99]['devices'][deviceid]['status']
	#D[99]['devices'][deviceid]['firmware']
	def build(self, extracheck=True):
		tree = MD.parse(self.filename)
		nodes = tree.getElementsByTagName("node")
		cnmldict = dict()
		
		for i in nodes:
			nid = int(i.getAttribute("id"))
			lat = float(i.getAttribute("lat"))
			lon = float(i.getAttribute("lon"))
			title = i.getAttribute('title')
			ndevices = i.getAttribute('devices') or 0
			ndevices = int(ndevices)
			nlinks = i.getAttribute('links') or 0
			nlinks = int(nlinks)
			status = i.getAttribute('status')
			
			devicestree = i.getElementsByTagName("device")
			
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
					
			cnmldict[nid] = {'lat':lat, 'lon':lon, 'title':title, 'ndevices':ndevices, 'nlinks':nlinks, 'status':status}
			cnmldict[nid]['devices'] = devs

		self.data = cnmldict
	
	def getData(self):
		return self.data
	
	def getTitles(self):
		titles = []
		
		for n in self.data.values():
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
		sys.exit(1)
	
	cnmlp = CNMLParser('tests/detail.3')
	cnmlp.build()
	d = cnmlp.getData()

	print d
	print
	print d[26997]
	print d[26997]['ndevices']
	print d[26997]['devices']
	print d[26997]['devices'].keys()
	print cnmlp.getTitles()
