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

from gi.repository import Gtk
from utils import APP_NAME, LOCALE_DIR, GUIFI_NET_WORLD_ZONE_ID
import logging
import os
import re
import sys

sys.path.append('lib')
sys.path.append('lib/libcnml')
from libcnml import CNMLParser
from configmanager import GuifinetStudioConfig
from ui import ChangeZoneDialog, fill_nodes_treeview

import gettext
gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
gettext.textdomain(APP_NAME)
_ = gettext.gettext

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
logger.addHandler(ch)


class UnsolclicUI:

    def __init__(self, cnmlp=None):
        self.cnmlp = cnmlp
        self.usc = UnSolClic()
        self.configmanager = GuifinetStudioConfig()
        self.zonecnmlp = None

        self.ui = Gtk.Builder()
        self.ui.add_from_file('ui/unsolclic.ui')
        self.ui.connect_signals(self)
        self.filestreeview = self.ui.get_object("filestreeview")
        self.nodestreeview = self.ui.get_object("nodestreeview")
        self.treestore1 = self.ui.get_object("treestore1")
        self.treestore2 = self.ui.get_object("treestore2")
        self.statusbar = self.ui.get_object("statusbar")
        self.closecnmlmenuitem = self.ui.get_object('closecnmlmenuitem')
        self.filesnotebook = self.ui.get_object('filesnotebook')
        self.nodesnotebook = self.ui.get_object('nodesnotebook')
        self.templatesmenuitem = self.ui.get_object('templatesmenuitem')
        self.uscwindow = self.ui.get_object('unsolclicwindow')
        self.uscwindow.show_all()

        self.statusbar.push(0, _('Loaded %s unsolclic templates') % len(self.usc.templates))
        if cnmlp:
            zid = self.cnmlp.rootzone
            self.change_title(zid)
            self.closecnmlmenuitem.set_sensitive(True)
            fill_nodes_treeview(cnmlp, self.nodestreeview, zid, recursive=True)

        # TODO: Fill menubar with templates
        self.menu_fill_templates()

    def menu_fill_templates(self):
        menu = Gtk.Menu()
        for template in self.usc.templates:
            item = Gtk.MenuItem.new_with_label(template.name)
            menu.add(item)
#            menu.attach(item, 0, 1, 0, 1)
        menu.show_all()
        self.templatesmenuitem.set_submenu(menu)

    def change_title(self, zid):
        ztitle = self.cnmlp.getZone(zid).title
        self.uscwindow.set_title(_('Unsolclic GUI') + ' [zone id %d - %s]' % (zid, ztitle))

    def _create_tab(self, usc):
        w = Gtk.ScrolledWindow()
        tv = Gtk.TextView()
        buf = tv.get_buffer()
        buf.set_text(usc, len(usc))
        w.add(tv)
        w.show_all()
        return w

    def add_tab(self, title, did, usc):
        w = self._create_tab(usc)
        label = '%s-%s' % (title, str(did))
        self.filesnotebook.append_page(w, Gtk.Label(label))
        self.filesnotebook.next_page()

    def generate(self, nid, template=None):
        try:
            node = self.cnmlp.getNode(nid)
        except KeyError:
            print 'Node id not found'
            sys.exit(1)
        print 'Generating unsolclic for %s (id: %d)' % (node.title, nid)
        uscdevs = self.usc.generate(node, template)

        self.filesnotebook.remove_page(0)
        self.nodesnotebook.set_current_page(1)
        # Add item (node title)
        parent = self.treestore1.append(None, (node.title, node.title))
        for did, usc in uscdevs:
            # Add subitems (generated filenames)
            self.treestore1.append(parent, (str(did), str(did)))
            self.add_tab(node.title, str(did), usc)

        self.filestreeview.expand_all()
        self.nodestreeview.expand_all()

    def on_aboutmenuitem_activate(self, widget, data=None):
        raise NotImplementedError

    def reset(self):
        self.treestore2.clear()

    def on_changezoneimagemenuitem_activate(self, widget, data=None):
        if not self.zonecnmlp:
            cnmlGWfile = self.configmanager.pathForCNMLCachedFile(GUIFI_NET_WORLD_ZONE_ID, 'zones')
            try:
                self.zonecnmlp = CNMLParser(cnmlGWfile)
            except IOError:
                print _('Error loading cnml guifiworld zone:'), cnmlGWfile
                print _('Guifi.net Studio will run normally but note that some features are disabled')

        dialog = ChangeZoneDialog(self.configmanager, self.zonecnmlp)
        if dialog.run() == Gtk.ResponseType.ACCEPT:
            zid = dialog.getSelectedZone()
            if zid:
                filename = self.configmanager.pathForCNMLCachedFile(zid, 'detail')

                try:
                    self.cnmlp = CNMLParser(filename)
                    self.change_title(zid)
                    self.reset()
                    fill_nodes_treeview(self.cnmlp, self.nodestreeview, zid, recursive=True)

                except IOError:
                    self.statusbar.push(0, _('CNML file "%s" couldn\'t be loaded') % filename)
                    self.cnmlp = None

#                active = self.cnmlp is not None
#                self.closecnmlmenuitem.set_sensitive(active)
#                self.enable_api_menuitems(active)

        dialog.destroy()

    def on_opencnmlmenuitem_activate(self, widget, data=None):
        dialog = Gtk.FileChooserDialog(_('Open CNML file'), self.uscwindow,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))

        if dialog.run() == Gtk.ResponseType.ACCEPT:
            filename = dialog.get_filename()
            try:
                self.cnmlp = CNMLParser(filename)
                self.closecnmlmenuitem.set_sensitive(True)
                zid = self.cnmlp.rootzone
                self.change_title(zid)
                self.reset()
                fill_nodes_treeview(cnmlp, self.nodestreeview, zid, recursive=True)
                self.statusbar.push(0, _('Loaded CNML file'))
                self.closecnmlmenuitem.set_sensitive(True)
            except IOError:
                self.statusbar.push(0, _('CNML file "%s" couldn\'t be loaded') % filename)
                self.cnmlp = None

        dialog.destroy()

    def on_closecnmlmenuitem_activate(self, widget=None, data=None):
        self.statusbar.push(0, _('Closed CNML file'))
        self.uscwindow.set_title(_('Unsolclic GUI'))
        self.closecnmlmenuitem.set_sensitive(False)
        self.reset()
        self.cnmlp = None
#        self.add_tab()

    def gtk_main_quit(self, widget, data=None):
        Gtk.main_quit()


class UscTemplate:
    def __init__(self, template, name, desc, model, last_update, version):
        self.template = template
        self.name = name
        self.description = desc
        self.model = model
        self.last_update = last_update
        self.version = version

    @staticmethod
    def fromMetadata(source, name, template):
        end_idx = source.find('#}')
        if end_idx == -1:
            raise Exception
        metadata = source[:end_idx + 2]
        assert metadata[:23] == '{#\n Unsolclic template\n'
        logger.debug(metadata)
        data = {}
        for d in metadata.split('\n')[2:-1]:
            logger.debug(d)
            m = re.search('^ (Description|Model|Devices|Last update|Version): (.*)$', d)
            if m is None:
                print 'WARNING: Invalid attribute.', d
                #raise KeyError
                continue
            data[m.group(1)] = m.group(2)

        return UscTemplate(template, name, data['Description'], data['Model'],
                           data['Last update'], data['Version'])

    def __repr__(self):
        r = '<USC %s>' % self.name
        return r


class UnSolClic:
    templates = []

    NANOSTATION2 = 0
    NANOSTATION_LOCO2 = 1
    NANOSTATION5 = 2
    NANOSTATION_LOCO5 = 3
    #"AirMaxM2 Bullet/PwBrg/AirGrd/NanoBr"

    def __init__(self):
        templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unsolclic')
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path), extensions=['jinja2.ext.i18n'])

        self.validate_templates()
        logger.info(_('Unsolclic loaded %d templates') % len(self.templates))

    def validate_templates(self):
        for template_name in self.env.list_templates():
            source = self.env.loader.get_source(self.env, template_name)[0]
            logger.debug('Validating %s...' % template_name,)
            try:
                t = self.env.get_template(template_name)
                usct = UscTemplate.fromMetadata(source, template_name, t)
                self.templates.append(usct)
                logger.debug('OK')
            except TemplateSyntaxError, e:
                logger.debug('FAILED reading template')
            except Exception, e:
                print e
                logger.debug('FAILED')

    def get_supported_devices(self):
        # return self.env.list_templates()
        return [t.name for t in self.templates]

    def generate_context_airos30(self, node, deviceid):
        device = node.devices[deviceid]
        assert len(device.radios) <= 1

        for radio in device.getRadios():
            assert len(radio.interfaces) <= 1

            for iface in radio.getInterfaces():
                assert len(iface.links) <= 1

                ##
                ipv4_ip = iface.ipv4
                ipv4_netmask = iface.mask
                ##

                for link in iface.getLinks():
                    remote_if = link.interfaceB
                    if remote_if.ipv4 == ipv4_ip:
                        remote_if = link.interfaceA

                    gateway = remote_if.ipv4

                    remote_radio = remote_if.parentRadio
                    ssid = remote_radio.ssid

        if device.name == 'NanoStation2':
            (net_mode, rate_max, txpower, ack, ext_antenna, mcastrate) = ('b', '11M', '6', '45', 'disabled', '11')
        elif device.name == 'NanoStation5':
            (net_mode, rate_max, txpower, ack, ext_antenna, mcastrate) = ('a', '54M', '6', '25', 'disabled', '54')
        elif device.name == 'NanoStation Loco2':
            (net_mode, rate_max, txpower, ack, ext_antenna, mcastrate) = ('b', '11M', '6', '44', 'enabled', '11')
        elif device.name == 'NanoStation Loco5':
            (net_mode, rate_max, txpower, ack, ext_antenna, mcastrate) = ('a', '54M', '6', '25', 'disabled', '54')
        else:
            # 'AirMaxM2 Bullet/PwBrg/AirGrd/NanoBr'
            (net_mode, rate_max, txpower, ack, ext_antenna, mcastrate) = ('a', '54M', '6', '25', 'disabled', '54')
            #raise NotImplementedError

        radio1txpower = '6'
        dev = {'nick': device.title}
        node_nick = node.title
        radio_rx = radio_tx = 2  # antenna_mode is not available in CNML, what is this for?

        # -- AirOsv30 --
        # zone_primary_dns, zone_secondary_dns
        context = {'wireless1ssid': ssid, 'ipv4_ip': ipv4_ip, 'ipv4_netmask': ipv4_netmask,
                   'wangateway': gateway, 'zone_primary_dns': '', 'zone_secondary_dns': '',
                   'dev': dev, 'node_nick': node_nick, 'radio1txpower': radio1txpower, 'net_mode': net_mode,
                   'rate_max': rate_max, 'ack': ack, 'ext_antenna': ext_antenna, 'mcastrate': mcastrate,
                   'radio_rx': radio_rx, 'radio_tx': radio_tx
                   }

        return context

    # Unify different template variable names
    def generate_context(self, node, deviceid, template_name):
        if template_name in ('AirOsv30', 'AirOsv30_sorted'):
            context = self.generate_context_airos30(node, deviceid)
        else:
            raise NotImplementedError

        return context

    def generate_from_dev(self, template_name=None):
        raise NotImplementedError

    def generate_from_context(self, template_name, context):
        t = self.env.get_template(template_name)
        r = t.render(context)
        # print r
        return r

    def guess_template(self, firmware):
        if firmware in ('AirOsv3.6+', 'AirOsv52'):
            template_name = 'AirOsv30'
        else:
            #if dev.firmware not in self.get_supported_devices():
            raise NotImplementedError
        return template_name

    # En el cnml
    # en Nanostation clientes <radio ssid="MlagaMLGnvsbltmpRd1CPE0"> no se usa
    # solo se usa el ssid de la antena a la que se conecta.
    def generate(self, node, template_name=None):
        radiodevs = filter(lambda d: d.type == 'radio', node.getDevices())

        if len(radiodevs) < len(node.getDevices()):
            # server, ...
            print 'Node %d contains %d devices (but only %d of them are radios)' % (node.id, len(node.getDevices()), len(radiodevs))
        else:
            print 'Node %d contains %d devices (and all of them are radios)' % (node.id, len(radiodevs))

        for device in node.getDevices():
            mark = '(*)' if device.type == 'radio' else ''
            print '-- %s %s' % (device.title, mark)

        uscdevs = []

        for n, dev in enumerate(radiodevs):
            print 'Firmware: %s' % dev.firmware
            print 'Template:',
            if not template_name:
                template_name = self.guess_template(dev.firmware)
                print '%s (autoguess)' % template_name
            else:
                print template_name
            print

            t = self.env.get_template(template_name)

            context = self.generate_context(node, dev.id, template_name)
            uscdevs.append((dev.id, t.render(context)))

        return uscdevs


if __name__ == '__main__':
    print _('Unsolclic GUI')
    print 'Usage: %s [cnml_file]' % sys.argv[0]
    print '       %s <cnml_file> <node_id>' % sys.argv[0]

    if len(sys.argv) in (2, 3):
        cnmlp = CNMLParser(sys.argv[1])
    else:
        cnmlp = None

    w = UnsolclicUI(cnmlp)
    w.uscwindow.connect('destroy', Gtk.main_quit)

    if len(sys.argv) == 3:
        nid = int(sys.argv[2])
        w.generate(nid)

    Gtk.main()


# --- DD-guifi ---
# dev.nick
# ipv4.ipv4
# ipv4.netmask
# ipv4.netstart
# zone_primary_dns
# zone_secondary_dns
# zone_ternary_dns
# txpwr
# antena_mode
# zone_primary_ntp
# dev.radios[0][''channel'']
# guifi_to_7bits(dev.radios[0][''ssid''])
# {{ _self.guifi_unsolclic_ospf(dev, zone, ospfzone,interfaceWlanLan) }}
# {{ _self.guifi_unsolclic_dhcp(dev, interfaceWlanLan) }}
# {{ _self.guifi_unsolclic_wds_vars(dev) }}
# {{ dev.radios[0].ssid }}
# gateway
# filter
# {{ _self.guifi_unsolclic_vlan_vars(dev, rc_startup) }}
# {{ _self.guifi_unsolclic_startup(dev, version, rc_startup) }}
# ipv4Addr
# dev.variable.firmware
# aIf
# interfaceWlanLan.ipv4[0].ipv4
# ipv4.netid
# ipv4.maskbits
# link.interface.mac
# link.interface.ipv4.host_name
# link.interface.ipv4.ipv4
# link.interface.ipv4.netmask
# count
#  dhcp_start
# link.interface.device_id }}-{{ hostname
# ifcount
# key
# wds_str
# dev.id
# rc_startup

# --- RouterOS4.0 ---
# host_name, ipv4, disabled, iname, netid, maskbits, ospf_name, firmware_name
# dev.id, dev.nick, firmware_description, zone_id, zone_primary_dns, zone_secondary_dns
# zone_primary_ntp, zone_secondary_ntp, snmp_contact, node_name
# dev.logserver, dev.radios[0].ipv4, dev.radios[0].ipv4, radio.radiodev_counter, radio.ssid
# radio.mode, radio.channel, radio.antenna_gain, channel, antena_mode
# interface.interface_type, radio_id, disabled, link.interface.ipv4.host_name
# ipv4.ipv4, ipv4.maskbits, ipv4.netid, ipv4.broadcast, link.interface.ipv4.host_name, disabled, link.interface.ipv4.host_name
# link.routing
# _self.ospf_interface(''wds_'' ~ link.interface.ipv4.host_name , ipv4.netid , ipv4.maskbits , ospf_name , ospf_zone, ospf_id, ''no'') }}
# {{ _self.bgp_peer(link.device_id, link.interface.ipv4.host_name, link.interface.ipv4.ipv4, ''yes'') }}
# radio.id, rmac, ospf_routerid, ospf_routerid

# --- RouterOS5.0 ---
