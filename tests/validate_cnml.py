#!/usr/bin/env python
import sys
from lxml import etree
#from lxml import objectify

if len(sys.argv) not in (2,3):
	print 'Validate CNML'
	print 'Usage: %s <filename> [dtd file]' %sys.argv[0]
	sys.exit(1)

if len(sys.argv) != 3:
	dtdfile = 'cnml.dtd'
else:
	dtdfile = sys.argv[2]
	
with open(dtdfile, 'rb') as dtdfp:
	dtd = etree.DTD(dtdfp)

tree = etree.parse(sys.argv[1])
#cnmlfp = open(sys.argv[1], 'rb')
#tree = objectify.parse(cnmlfp)

print 'DTD validation:', dtd.validate(tree)

errors = dtd.error_log.filter_from_errors()
if len(errors) > 0:
	print '%d errors found:' %len(errors)
	print errors
