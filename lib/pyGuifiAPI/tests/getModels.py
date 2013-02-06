#!/usr/bin/env python
import sys
sys.path.append('..')

from api import *

if len(sys.argv) != 2:
    print 'Usage: %s [model]\n' % sys.argv[0]
    model = None
else:
    model = sys.argv[1]

#No authentication needed
g = GuifiAPI(secure=SECURE)

models = g.getModels(model)

print 'Total models:', len(models)
print 'Model\t\t\t\t\tSupported\tType\tModel ID\tFirmware ID'
for m in models:
    print '%s\t\t\t\t\t%s\t%s\t%s\t%s' % (m['model'], m['supported'], m['type'], m['mid'], m['fid'])
