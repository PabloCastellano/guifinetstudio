#!/usr/bin/env python
import sys
sys.path.append('..')

from api import *

#No authentication needed
g = GuifiAPI(secure=SECURE)

protocols = g.getProtocols()

print('Total protocols: {}'.format(len(protocols)))
print('Title\tDescription')
for protocol in protocols:
    print('{}\t{}'.format(protocol['title'], protocol['description']))
