#!/usr/bin/env python
import sys
sys.path.append('..')

from guifiConfig import *
from api import *

if len(sys.argv) != 3:
    print 'Create a new radio'
    print 'Usage: %s <device_id> <mode>' % sys.argv[0]
    print 'Mode: ap, ad-hoc...'
    sys.exit(1)

if sys.argv[2] not in ('ap', 'ad-hoc'):
    print 'Invalid mode:', sys.argv[1]
    sys.exit(1)

g = GuifiAPI(USERNAME, PASSWORD, secure=SECURE)
g.auth()

# NanoStation2 and AirOSv30
(rid, interfaces) = g.addRadio(sys.argv[2], sys.argv[1], '12:12:12:12:12:13', angle=0, gain=21, azimuth=0, amode=None, ssid='mySSID', protocol='802.11b', channel=0, clients='Yes')

print 'Radio id:', rid
for iface in interfaces:
    for ifaceitems in iface.items():
        if isinstance(ifaceitems[1], list):
            for ips in ifaceitems[1]:
                for ipv4 in ips.items():
                    print '  %s - %s' % ipv4
        else:
            print '%s - %s' % ifaceitems
