#!/usr/bin/env python
import sys
sys.path.append('..')

from guifiConfig import *
from api import *

if len(sys.argv) != 5:
    print('Create a new device')
    print('Usage: {} <device_from> <radio_from> <device_to> <radio_to>'.format(sys.argv[0]))
    sys.exit(1)

g = GuifiAPI(USERNAME, PASSWORD, secure=SECURE)
g.auth()

#  ./addLink.py 44011 0 19414 0
(lid, ipv4) = g.addLink(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))

# "responses":{"ipv4":{"ipv4_type":1,"ipv4":"10.228.172.36","netmask":"255.255.255.248"},"link_id":null}}

print('Interface id: {}'.format(lid))

for settings in ipv4[0].items():
    print('  {} - {}'.format(*settings))
