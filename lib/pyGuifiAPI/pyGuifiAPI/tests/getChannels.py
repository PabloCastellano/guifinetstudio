#!/usr/bin/env python
import sys
sys.path.append('..')

from api import *

if len(sys.argv) != 2:
    print('Usage: {} <protocol>'.format(sys.argv[0]))
    sys.exit(1)

#No authentication needed
g = GuifiAPI(secure=SECURE)
channels = g.getChannels(sys.argv[1])

print('Total channels: {}'.format(len(channels)))
print('Title\t\t\tDescription')
for channel in channels:
    print('{}\t\t\t{}'.format(channel['title'], channel['description']))
