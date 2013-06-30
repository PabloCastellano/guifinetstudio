#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# utils.py - Utils for Guifi.net Studio
# Copyright (C) 2012 Pablo Castellano <pablo@anche.no>
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

import re
import os

GUIFI_NET_WORLD_ZONE_ID = 3671
I18N_APP_NAME = 'guifinetstudio'
APP_NAME = I18N_APP_NAME
LOCALE_DIR = 'locale'

import gettext
gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
gettext.textdomain(APP_NAME)
_ = gettext.gettext

KMLDOM_ENABLED = False
try:
    import kmldom
    KMLDOM_ENABLED = True
except ImportError:
    print _('WARNING: python kmldom dependency was not found')
    print _('You need to install it in order to enable KML features')

########
re_email = re.compile("^.+@.+\..{2,4}$")
re_mac = re.compile("[0-9a-f]{2}([-:][0-9a-f]{2}){5}$")
re_ipv4 = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")


def valid_email_address(email):
    if isinstance(email, str):
        return re_email.match(email) is not None
    else:
        # list of email addresses separated by commas
        for e in email.split(','):
            if e == '':
                continue
            em = e.strip()
            if valid_email_address(em) is False:
                return False
        return True


def valid_mac_address(mac):
    return re_mac.match(mac.lower()) is not None


def valid_ipv4_address(ip):
    return re_ipv4.match(ip) is not None


def openUrl(url):
    print _('Opening in web browser:'), url
    systemstr = 'xdg-open %s' % url
    os.system(systemstr)


def CNML2KML(cnmlp, filename='mycnml.kml'):
    if not KMLDOM_ENABLED:
        print _('CNML2KML: function not available. kmldom module not found')
        return

    factory = kmldom.KmlFactory.GetFactory()
    doc = factory.CreateDocument()

    for node in cnmlp.getNodes():
        coordinates = factory.CreateCoordinates()
        coordinates.add_latlng(node.latitude, node.longitude)
        point = factory.CreatePoint()
        point.set_coordinates(coordinates)
        placemark = factory.CreatePlacemark()
        placemark.set_name(node.title)
        placemark.set_geometry(point)
        doc.add_feature(placemark)

    xml = kmldom.SerializePretty(doc)
    with open(filename, 'w') as kmlfp:
        kmlfp.write(xml)


# GtkTreeModelFilterVisibleFunc
# Case insensitive :)
def filterbyname_func(model, it, entry):
    haystack = model.get_value(it, 0).lower()
    needle = entry.get_text().lower()
    return needle in haystack
