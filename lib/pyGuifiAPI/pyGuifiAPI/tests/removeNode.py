#!/usr/bin/env python
import sys
sys.path.append('..')

from guifiConfig import *
from api import *

if len(sys.argv) != 2:
    print('Remove an existing node')
    print('Usage: {} <node_id>'.format(sys.argv[0]))
    sys.exit(1)

g = GuifiAPI(USERNAME, PASSWORD, secure=SECURE)
g.auth()

try:
    g.removeNode(sys.argv[1])
except GuifiApiError as e:
    print(e.reason)
