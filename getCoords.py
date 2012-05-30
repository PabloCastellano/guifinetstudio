#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# getCoords.py - 
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

def getCoords(filename):
	tree = MD.parse(filename)
	nodes = tree.getElementsByTagName("node")
	coords = []

	for i in nodes:
		c = (float(i.attributes["lat"].value), float(i.attributes["lon"].value))
		coords.append(c)
#		print c[0], c[1]

	return coords


def getCoords_with_name(filename):
	tree = MD.parse(filename)
	nodes = tree.getElementsByTagName("node")
	coords = []

	for i in nodes:
		c = (float(i.attributes["lat"].value), float(i.attributes["lon"].value), i.attributes["title"].value)
		coords.append(c)
#		print c[0], c[1], c[2]

	return coords


if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: %s <detail_file>" %(sys.argv[0])
		sys.exit(1)
	
#	coords = getCoords(sys.argv[1])
	coords = getCoords_with_name(sys.argv[1])

