#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# distances.py - Script to calculate distances between nodes
# Copyright (C) 2013 Pablo Castellano <pablo@anche.no>
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

from geopy import distance
import os
import sys
#os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('lib')
sys.path.append('lib/libcnml')

from libcnml import CNMLParser

from math import *


#Horizontal Bearing
def calcBearing(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dLon = lon2 - lon1
    y = sin(dLon) * cos(lat2)
    x = cos(lat1) * sin(lat2) \
        - sin(lat1) * cos(lat2) * cos(dLon)
    return degrees(atan2(y, x))


if __name__ == '__main__':
    print 'Calculate distances and azimuth from one node to the rest of nodes in the same zone'
    print 'Usage: %s [nid] [filename.cnml]' % sys.argv[0]
    print

    filename = os.path.expanduser('~/.cache/guifinetstudio/detail/26494.cnml')
    nid = 33968  # MLGInvisible
    if len(sys.argv) == 3:
        nid, filename = sys.argv[1:2]

    # Parse CNML file
    cnmlp = CNMLParser(filename)
    from_node = cnmlp.getNode(nid)
    from_coord = (from_node.latitude, from_node.longitude)
    nodes = cnmlp.getNodes()
    distances = []
    nodes.remove(from_node)

    # Calculate distance to every node in the same zone
    for to_node in nodes:
        to_coord = (to_node.latitude, to_node.longitude)
        dist = distance.VincentyDistance(from_coord, to_coord)
        bearing = calcBearing(from_node.latitude, from_node.longitude, to_node.latitude, to_node.longitude)
        distances.append((dist.km, from_node.title, to_node.title, bearing))

    # Sort by distance
    for d in sorted(distances):
        if d[0] >= 1:
            dist_metric = '%.3f Km' % d[0]
        else:
            dist_metric = '%d m' % (d[0] * 1000)
        print '%s -> %s: %s (Az: %.2f)' % (d[1], d[2], dist_metric, d[3])
