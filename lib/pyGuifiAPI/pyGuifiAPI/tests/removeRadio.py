#!/usr/bin/env python
import sys
sys.path.append('..')

from guifiConfig import *
from api import *

if len(sys.argv) != 3:
	print 'Remove an existing radio'
	print 'Usage: %s <device_id> <radiodev_counter>' % sys.argv[0]
	sys.exit(1)

g = GuifiAPI(USERNAME, PASSWORD, secure=SECURE)
g.auth()

try:
	g.removeRadio(sys.argv[1], sys.argv[2])
except GuifiApiError, e:
	print e.reason
