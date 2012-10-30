import sys
sys.path.append('lib')
from utils import CNML2KML
from libcnml import CNMLParser

if len(sys.argv) != 3:
	print "CNML2KML"
	print "Usage: %s <IN_cnml_file> <OUT_kml_file>" %sys.argv[0]
	sys.exit(-1)

cnmlp = CNMLParser(sys.argv[1])
CNML2KML(cnmlp, sys.argv[2])
