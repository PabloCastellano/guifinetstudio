#!/usr/bin/env python
import sys
sys.path.append('..')

from api import *

#No authentication needed
g = GuifiAPI()
firmwares = g.getFirmwares(secure=SECURE)

print('Total firmwares: {}'.format(len(firmwares)))
print('Title\t\t\tDescription')
for firmware in firmwares:
    print('{}\t\t\t{}'.format(firmware['title'], firmware['description']))
