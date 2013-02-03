#!/usr/bin/env python
import sys
sys.path.append('..')

from api import *

#No authentication needed
g = GuifiAPI()
manufacturers = g.getManufacturers(secure=SECURE)

print 'Total manufacturers:', len(manufacturers)
print 'ID\tName\tURL'
for manufacturer in manufacturers:
    print '%s\t%s\t%s' % (manufacturer['fid'], manufacturer['name'], manufacturer['url'])
