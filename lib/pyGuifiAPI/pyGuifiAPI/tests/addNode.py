#!/usr/bin/env python
import sys
sys.path.append('..')

from guifiConfig import *
from api import *

if len(sys.argv) != 2:
    print('Create a new node')
    print('Usage: {} <title>'.format(sys.argv[0]))
    sys.exit(1)

g = GuifiAPI(USERNAME, PASSWORD, secure=SECURE)
g.auth()

g.addNode(sys.argv[1], DEF_ZONE, DEF_LAT, DEF_LON)
