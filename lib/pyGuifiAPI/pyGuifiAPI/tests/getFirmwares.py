#!/usr/bin/env python
import sys
sys.path.append('..')

from api import *

#No authentication needed
g = GuifiAPI()
firmwares = g.getFirmwares(secure=SECURE)

print 'Total firmwares:', len(firmwares)
print 'Title\t\t\tDescription'
for firmware in firmwares:
    print '%s\t\t\t%s' % (firmware['title'], firmware['description'])
