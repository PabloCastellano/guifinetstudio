#!/usr/bin/env python
import sys
sys.path.append('..')

from api import *

#No authentication needed
g = GuifiAPI(secure=SECURE)

protocols = g.getProtocols()

print 'Total protocols:', len(protocols)
print 'Title\tDescription'
for protocol in protocols:
    print '%s\t%s' % (protocol['title'], protocol['description'])
