#!/usr/bin/env python
import sys
sys.path.append('..')

from api import *

if len(sys.argv) != 2:
    print 'Usage: %s <protocol>' % sys.argv[0]
    sys.exit(1)

#No authentication needed
g = GuifiAPI(secure=SECURE)
channels = g.getChannels(sys.argv[1])

print 'Total channels:', len(channels)
print 'Title\t\t\tDescription'
for channel in channels:
    print '%s\t\t\t%s' % (channel['title'], channel['description'])
