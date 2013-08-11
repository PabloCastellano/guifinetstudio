#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# unsolclic.py - Un Sol Clic feature to generate device configurations
# Copyright (C) 2011-2012 Pablo Castellano <pablo@anche.no>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

try:
    import jinja2
    from jinja2.exceptions import TemplateSyntaxError
except ImportError:
    raise

from utils import APP_NAME, LOCALE_DIR, GUIFI_NET_WORLD_ZONE_ID
import argparse
import logging
import sys

sys.path.append('lib')
sys.path.append('lib/libcnml')
from libcnml import CNMLParser
from unsolclic import UscTemplate, UnSolClic
from configmanager import GuifinetStudioConfig

import gettext
gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
gettext.textdomain(APP_NAME)
_ = gettext.gettext

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
logger.addHandler(ch)


class UnsolclicCLI:
    def __init__(self, cnmlp=None):
        self.cnmlp = cnmlp
        self.usc = UnSolClic()

        if cnmlp:
            zid = self.cnmlp.rootzone
            ztitle = self.cnmlp.getZone(zid).title
            print 'Loaded zone %s (id: %d)' % (ztitle, zid)

    def generate(self, nid, template=None):
        try:
            node = self.cnmlp.getNode(nid)
        except KeyError:
            print 'Node id not found'
            sys.exit(1)
        print 'Generating unsolclic for %s (id: %d)' % (node.title, nid)
        usc = self.usc.generate(node, template)
        return usc


if __name__ == '__main__':
    # FIXME: Carriage returns are not shown! :-(
    examples = """Examples:
%s -l
%s -u 33968 -c ~/.cache/guifinetstudio/detail/26494.cnml
""" % (sys.argv[0], sys.argv[0])

    parser = argparse.ArgumentParser(description=_('Unsolclic command line interface'),
                                     epilog=examples)
    parser.add_argument('--version', action='version', version='FIXME')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    group1 = parser.add_argument_group('Main operation mode')
    mgroup = group1.add_mutually_exclusive_group(required=True)
    mgroup.add_argument('-l', '--list', action='store_true', help='Print list of templates available')
    mgroup.add_argument('-u', metavar='node_id', dest='nid', type=int, help='Node ID to generate unsolclic')
    group2 = parser.add_argument_group('Operation modifiers')
    mgroup = group2.add_mutually_exclusive_group()
    mgroup.add_argument('-c', metavar='cnml_file', dest='cnml', help='Use this CNML file')
    mgroup.add_argument('-z', metavar='zone_id', type=int, dest='zone', help='Use this CNML file zone id')
    group2.add_argument('-o', metavar='filename', dest='output', help='Write output to this filename')
    group2.add_argument('-t', metavar='template_id or name', dest='template', help='Use this template to generate unsolclic')
    args = parser.parse_args()

    """
    print '       template = template_id or template_name'
    print '       If cnml_file is not specified, it will load by default Guifi.net world zone'
    """

    if args.list:
        w = UnsolclicCLI(None)
        for t in enumerate(w.usc.templates):
            print '%d. %s' % (t[0], t[1].name)
            if args.verbose:
                print '\tDescription:', t[1].description
                print '\tModel:', t[1].model
                print '\tLast update:', t[1].last_update
                print '\tVersion:', t[1].version
                print ''
        sys.exit(1)

    config = GuifinetStudioConfig()
    if args.cnml:
        cnmlp = CNMLParser(args.cnml)
    else:
        #path = config.pathForCNMLCachedFile(GUIFI_NET_WORLD_ZONE_ID)
        if args.zone:
            path = config.pathForCNMLCachedFile(args.zone, 'detail')
        else:
            path = config.pathForCNMLCachedFile(26494, 'detail')
        cnmlp = CNMLParser(path)

    w = UnsolclicCLI(cnmlp)

    #nid = 33968 # La Invisible
    #template = 'AirOsv30_sorted'
    if args.template and args.template.isdigit():
        template_name = w.usc.templates[int(args.template)].name
    else:
        template_name = args.template
    uscdevs = w.generate(args.nid, template_name)
    #uscdevs = w.generate(nid)

    for did, usc in uscdevs:
        if args.output:
            myoutput_file = "%s-%d" % (args.output, did)
            with open(myoutput_file, 'w') as fp:
                fp.write(usc)
                print 'Written file', myoutput_file
        else:
            print '----- BEGIN USC template for device %d -----' % did
            print usc
            print '----- END USC template for device %d -----' % did
