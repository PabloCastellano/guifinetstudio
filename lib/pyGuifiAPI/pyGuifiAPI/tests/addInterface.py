#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

from guifiConfig import *
from api import *

if len(sys.argv) != 3:
    print('Create a new interface')
    print('Usage: {} <device_id> <radio>'.format(sys.argv[0]))
    sys.exit(1)

g = GuifiAPI(USERNAME, PASSWORD, secure=SECURE)
g.auth()

"""
L'API només suporta afegir interfícies de ràdio sense fils per poder afegir rangs d'adreces IP per clients.

En cas que la ràdio funcioni en mode client no es podran afegir més interfícies.

Queda per implementar el suport de les connexions per cable.
"""

(iid, ipv4) = g.addInterface(int(sys.argv[1]), int(sys.argv[2]))

print('Interface id: {}'.format(iid))

for settings in ipv4[0].items():
    print('  {} - {}'.format(*settings))
