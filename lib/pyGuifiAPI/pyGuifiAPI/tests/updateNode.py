#!/usr/bin/env python
import sys
sys.path.append('..')

from guifiConfig import *
from api import *

if len(sys.argv) != 3:
    print('Update an existing node changing its title')
    print('Usage: {} <node_id> <new_title>'.format(sys.argv[0]))
    sys.exit(1)

g = GuifiAPI(USERNAME, PASSWORD, secure=SECURE)
g.auth()

try:
    g.updateNode(sys.argv[1], title=sys.argv[2])
except GuifiApiError as e:
    print(e.reason)
