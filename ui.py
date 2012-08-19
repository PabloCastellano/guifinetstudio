#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ui.py - User Interface
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


from gi.repository import Gdk, Gtk

from pyGuifiAPI.error import GuifiApiError

from unsolclic import UnSolClic

from utils import *

import locale, gettext
gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
gettext.textdomain(APP_NAME)
locale.setlocale(locale.LC_ALL, '')
locale.bindtextdomain(APP_NAME, LOCALE_DIR)
_ = gettext.gettext


class UnsolclicDialog:
	def __init__(self, node):
		self.ui = Gtk.Builder()
		self.ui.set_translation_domain(APP_NAME)
		self.ui.add_from_file('ui/uscdialog.ui')
		self.ui.connect_signals(self)

		self.uscdialog = self.ui.get_object("uscdialog")
		self.uscdialog.set_title(_('Unsolclic for node ') + node.title)

		# Unsolclic instance
		self.usc = UnSolClic()
		
		self.node = node
		conf = self.usc.generate(node)

		self.usctextbuffer = self.ui.get_object('usctextbuffer')
		self.usctextbuffer.set_text(conf)
		
		self.uscdialog.show_all()
		
	def on_uscdialog_response(self, widget, response):
		if response == -12: #Auto-load to device
			print _('Autoload configuration')
			raise NotImplementedError
		elif response == -13: #Copy to clipboard
			print _('Copy usc to clipboard')
			#cb = Gtk.Clipboard()
			#cb.set_text(self.usctextbuffer.get_text(), -1)
			self.usctextbuffer.copy_clipboard(Gtk.Clipboard.get(Gdk.Atom.intern('0', True)))
			raise NotImplementedError
		elif response == -14: #Save to file
			raise NotImplementedError
		else:
			self.uscdialog.destroy()
	

class EditNodeDialog:
	def __init__(self, api, zones, zonecnmlp, allZones, coords=None):
		self.ui = Gtk.Builder()
		self.ui.set_translation_domain(APP_NAME)
		self.ui.add_from_file('ui/editnodedialog.ui')
		self.ui.connect_signals(self)

		self.guifiAPI = api
		
		self.editnodedialog = self.ui.get_object("editnodedialog")
		self.editnodeokbutton = self.ui.get_object("editnodeokbutton")
		self.nodecoordinatesentry = self.ui.get_object('nodecoordinatesentry')
		self.nodetitleentry = self.ui.get_object('nodetitleentry')		
		self.nodeinfotextview = self.ui.get_object('nodeinfotextview')
		self.nodenickentry = self.ui.get_object('nodenickentry')
		self.nodecontactentry = self.ui.get_object('nodecontactentry')
		self.nodezonecombobox = self.ui.get_object('nodezonecombobox')
		self.nodezonedescentry = self.ui.get_object('nodezonedescentry')
		self.nodeelevationentry = self.ui.get_object('nodeelevationentry')
		self.nodegraphscombobox = self.ui.get_object('nodegraphscombobox')
		self.takefromparentscheckbutton = self.ui.get_object('takefromparentscheckbutton')
		self.stablenodecheckbutton = self.ui.get_object('stablenodecheckbutton')
		self.entrycompletion1 = self.ui.get_object('entrycompletion1')
		self.nodeinfotextbuffer = self.ui.get_object('nodeinfotextbuffer')

		self.editnodedialog.set_title(_('Create new Guifi.net node'))
		self.editnodedialog.show_all()
		
		fillZonesComboBox(self.nodezonecombobox, zones)
		
		if allZones == []:
			label92 = self.ui.get_object('label92')
			label92.set_visible(False)
			entry19 = self.ui.get_object('entry19')
			entry19.set_visible(False)
		else:
			fillZonesEntryCompletion(self.entrycompletion1, allZones)

		if coords:
			self.nodecoordinatesentry.set_text(str(coords[0]) + ', ' + str(coords[1]))
			self.nodecoordinatesentry.set_sensitive(False)
			self.nodetitleentry.grab_focus()

	def on_takefromparentscheckbutton_toggled(self, widget, data=None):
		isActive = widget.get_active()
		self.nodegraphscombobox.set_sensitive(not isActive)

	def on_acceptxolncheckbutton_toggled(self, widget, data=None):
		isActive = widget.get_active()
		self.editnodeokbutton.set_sensitive(isActive)
		
	def editnodevalidation(self):
		# Checks: title, zone, lat, lon
		if self.nodetitleentry.get_text() == '':
			self.nodetitleentry.grab_focus()
			return False
		
		if not valid_email_address(self.nodecontactentry.get_text()):
			self.nodecontactentry.grab_focus()
			return False
			
		if self.nodecoordinatesentry.get_text() == '':
			self.nodecoordinatesentry.grab_focus()
			return False
		else:
			try:
				lat,lon = self.nodecoordinatesentry.get_text().split(',')
				if lat == '' or lon == '':
					self.nodecoordinatesentry.grab_focus()
					return False
				float(lat)
				float(lon)
			except ValueError:
				self.nodecoordinatesentry.grab_focus()
				return False
				
		if self.nodezonecombobox.get_active_iter() is None:
			self.nodezonecombobox.grab_focus()
			return False
		
		if not self.takefromparentscheckbutton.get_active() and self.nodegraphscombobox.get_active_iter() is None:
			return False
			
		# rest of value types
		try:
			if self.nodeelevationentry.get_text() != '':
				int(self.nodeelevationentry.get_text())
		except ValueError:
			self.nodeelevationentry.grab_focus()
			return False
			
		return True
		
	def on_editnodedialog_response(self, widget, response):
		if response == Gtk.ResponseType.ACCEPT:
			(start, end) = self.nodeinfotextbuffer.get_bounds()
			nodeinfotext = self.nodeinfotextview.get_buffer().get_text(start, end, True)
			
			if not self.editnodevalidation():
				print _("There's some invalid data")
				return
			
			lat,lon = self.nodecoordinatesentry.get_text().split(',')
			it = self.nodezonecombobox.get_active_iter()
			zid = self.nodezonecombobox.get_model().get_value(it, 0)
			if self.takefromparentscheckbutton.get_active():
				graphs = None
			else:
				it = self.nodegraphscombobox.get_active_iter()
				graphs = self.nodegraphscombobox.get_model().get_value(it, 0)
			
			stable = 'Yes' if self.stablenodecheckbutton.get_active() else 'No'

			res = CreateLocalOrRemoteMessageDialog(self.guifiAPI.getHost(), 'node', self.nodetitleentry.get_text())
				
			if res in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT):
				return
			
			try:
				node_id = self.guifiAPI.addNode(self.nodetitleentry.get_text(), zid, lat, lon, body=nodeinfotext,
							nick=self.nodenickentry.get_text(), zone_desc=self.nodezonedescentry.get_text(),
							notification=self.nodecontactentry.get_text(), elevation=self.nodeelevationentry.get_text(),
							stable=stable, graph_server=graphs, status='Planned')
			except GuifiApiError, e:
				ErrorResponseFromServerMessageDialog(e)
				return
			
			CreatedSuccessfullyOpenUrlMessageDialog('Node', self.guifiAPI.urlForNode(node_id), node_id)
				
		self.editnodedialog.destroy()


class EditZoneDialog:
	def __init__(self, api, zones):
		self.ui = Gtk.Builder()
		self.ui.set_translation_domain(APP_NAME)
		self.ui.add_from_file('ui/editzonedialog.ui')
		self.ui.connect_signals(self)

		self.guifiAPI = api
		
		self.editzonedialog = self.ui.get_object('editzonedialog')
		self.zonetitleentry = self.ui.get_object('zonetitleentry')
		self.parentzonecombobox = self.ui.get_object('parentzonecombobox')
		self.zonenickentry = self.ui.get_object('zonenickentry')
		self.zonemodecombobox = self.ui.get_object('zonemodecombobox')
		self.zoneinfotextview = self.ui.get_object('zoneinfotextview')
		self.zoneinfotextbuffer = self.ui.get_object('zoneinfotextbuffer')
		self.ospfidentry = self.ui.get_object('ospfidentry')
		self.zonewebentry = self.ui.get_object('zonewebentry')
		self.zonecontactentry = self.ui.get_object('zonecontactentry')
		self.zonegraphscombobox = self.ui.get_object('zonegraphscombobox')
		self.zoneproxyscombobox = self.ui.get_object('zoneproxyscombobox')
		self.zonednsscombobox = self.ui.get_object('zonednsscombobox')
		self.zonentpscombobox = self.ui.get_object('zonentpscombobox')
		self.editzoneokbutton = self.ui.get_object('editzoneokbutton')
		
		self.editzonedialog.show_all()

		self.editzonedialog.set_title('Create new Guifi.net zone')
		fillZonesComboBox(self.parentzonecombobox, zones)


	def editzonevalidation(self):
		# Checks: title, master, minx, miny, maxx, maxy
		if self.zonetitleentry.get_text() == '':
			self.zonetitleentry.grab_focus()
			return False
		
		if not valid_email_address(self.zonecontactentry.get_text()):
			self.zonecontactentry.grab_focus()
			return False
							
		if self.parentzonecombobox.get_active_iter() is None:
			self.parentzonecombobox.grab_focus()
			return False
			
		# ...
		return True
		
		
	def on_editzonedialog_response(self, widget, response):
		if response == Gtk.ResponseType.ACCEPT:
			"""
			self.zonegraphscombobox
			self.zoneproxyscombobox
			self.zonednsscombobox
			self.zonentpscombobox
			"""
			
			(start, end) = self.zoneinfotextbuffer.get_bounds()
			zoneinfotext = self.zoneinfotextview.get_buffer().get_text(start, end, True)
			
			if not self.editzonevalidation():
				print _("There's some invalid data")
				return
			
			it = self.parentzonecombobox.get_active_iter()
			zid = self.parentzonecombobox.get_model().get_value(it, 0)
			
			it = self.zonemodecombobox.get_active_iter()
			zonemode = self.zonemodecombobox.get_model().get_value(it, 0)
			
			res = CreateLocalOrRemoteMessageDialog(self.guifiAPI.getHost(), 'zone', self.zonetitleentry.get_text())
			
			if res in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT):
				return
				
			try:
				zone_id = self.guifiAPI.addZone(self.zonetitleentry.get_text(), zid, 0, 0, 0, 0,
							nick=self.zonenickentry.get_text(), mode=zonemode, body=zoneinfotext, timezone='+01 2 2',
							graph_server=None, proxy_server=None, dns_servers=None,
							ntp_servers=None, ospf_zone=self.ospfidentry.get_text(), homepage=self.zonewebentry.get_text(),
							notification=self.zonecontactentry.get_text())
						
			except GuifiApiError, e:
				ErrorResponseFromServerMessageDialog(e)
				return
			
			CreatedSuccessfullyOpenUrlMessageDialog('Zone', self.guifiAPI.urlForZone(zone_id), zone_id)
				
		self.editzonedialog.destroy()


class EditDeviceDialog:
	def __init__(self, api, nodes):
		self.ui = Gtk.Builder()
		self.ui.set_translation_domain(APP_NAME)
		self.ui.add_from_file('ui/editdevicedialog.ui')
		self.ui.connect_signals(self)
		
		self.guifiAPI = api
		
		self.editdevicedialog = self.ui.get_object('editdevicedialog')
		self.editdevicenodecombobox = self.ui.get_object('editdevicenodecombobox')
		self.devtypecombobox = self.ui.get_object('devtypecombobox')
		self.devmacentry = self.ui.get_object('devmacentry')
		self.devnickentry = self.ui.get_object('devnickentry')
		self.devcontactentry = self.ui.get_object('devcontactentry')
		self.devcommententry = self.ui.get_object('devcommententry')
		self.devstatuscombobox = self.ui.get_object('devstatuscombobox')
		self.devgraphscombobox = self.ui.get_object('devgraphscombobox')
		self.editdeviceokbutton = self.ui.get_object('editdeviceokbutton')
		self.devmodelcombobox = self.ui.get_object('devmodelcombobox')
		self.devfirmwarecombobox = self.ui.get_object('devfirmwarecombobox')
		self.devdownloadcombobox = self.ui.get_object('devdownloadcombobox')
		self.devuploadcombobox = self.ui.get_object('devuploadcombobox')
		self.devmrtgcombobox = self.ui.get_object('devmrtgcombobox')
		self.devmrtg2combobox = self.ui.get_object('devmrtg2combobox')
		self.notebook3 = self.ui.get_object("notebook3")
		self.notebook3.set_show_tabs(False)

		self.editdevicedialog.show_all()
		
		self.editdevicedialog.set_title(_('Create new Guifi.net device'))
		fillNodesComboBox(self.editdevicenodecombobox, nodes)
		
	def editdevicevalidation(self):
		# Checks: title, zone, lat, lon
		if self.devmacentry.get_text() == '':
			self.devmacentry.grab_focus()
			return False
		
		if not valid_email_address(self.devcontactentry.get_text()):
			self.devcontactentry.grab_focus()
			return False
		
		return True
		
		
	def on_devtypecombobox_changed(self, widget, data=None):
		it = self.devtypecombobox.get_active_iter()
		rtype = self.devtypecombobox.get_model().get_value(it, 0)
		
		pages = {'radio':0, 'adsl':1, 'generic':2}
		if pages.has_key(rtype):
			self.notebook3.set_current_page(pages[rtype])
		else:
			self.notebook3.set_current_page(3)


	def on_editdevicedialog_response(self, widget, response):
		if response == Gtk.ResponseType.ACCEPT:
			"""
			self.devgraphscombobox
			"""
			
			if not self.editdevicevalidation():
				print _("There's some invalid data")
				return
			
			it = self.editdevicenodecombobox.get_active_iter()
			nid = self.editdevicenodecombobox.get_model().get_value(it, 0)
			
			it = self.devtypecombobox.get_active_iter()
			rtype = self.devtypecombobox.get_model().get_value(it, 0)
			
			it = self.devstatuscombobox.get_active_iter()
			rstatus = self.devstatuscombobox.get_model().get_value(it, 0)
			
			if rtype == 'radio':
				it = self.devmodelcombobox.get_active_iter()
				model = self.devmodelcombobox.get_model().get_value(it, 0)
			
				it = self.devfirmwarecombobox.get_active_iter()
				firmware = self.devfirmwarecombobox.get_model().get_value(it, 0)
				
				download = None
				upload = None
				mrtg = None
				
			elif rtype == 'adsl':
				model = None
				firmware = None
				
				it = self.devdownloadcombobox.get_active_iter()
				download = self.devdownloadcombobox.get_model().get_value(it, 0)
			
				it = self.devuploadcombobox.get_active_iter()
				upload = self.devuploadcombobox.get_model().get_value(it, 0)
			
				it = self.devmrtgcombobox.get_active_iter()
				mrtg = self.devmrtgcombobox.get_model().get_value(it, 0)
			
			elif rtype == 'generic':
				model = None
				firmware = None
				download = None
				upload = None
				
				it = self.devmrtg2combobox.get_active_iter()
				mrtg = self.devmrtg2combobox.get_model().get_value(it, 0)
				
			else:
				model = None
				firmware = None
				download = None
				upload = None
				mrtg = None
				
			res = CreateLocalOrRemoteMessageDialog(self.guifiAPI.getHost(), 'device', self.devnickentry.get_text())
			
			if res in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT):
				return
				
			try:
				device_id = self.guifiAPI.addDevice(nid, rtype, self.devmacentry.get_text(), 
								nick=self.devnickentry.get_text(), notification=self.devcontactentry.get_text(),
								comment=self.devcommententry.get_text(), status=rstatus, graph_server=None,
								model_id=model, firmware=firmware, download=download, upload=upload, mrtg_index=mrtg)

			except GuifiApiError, e:
				ErrorResponseFromServerMessageDialog(e)
				return
			
			CreatedSuccessfullyOpenUrlMessageDialog('Device', self.guifiAPI.urlForDevice(device_id), device_id)

		self.editdevicedialog.destroy()


class EditRadioDialog:
	def __init__(self, api, cnmlp):
		self.ui = Gtk.Builder()
		self.ui.set_translation_domain(APP_NAME)
		self.ui.add_from_file('ui/editradiodialog.ui')
		self.ui.connect_signals(self)

		self.guifiAPI = api
		self.editradiodialog = self.ui.get_object('editradiodialog')
		self.editradionodecombobox = self.ui.get_object('editradionodecombobox')
		self.editradiodevicecombobox = self.ui.get_object('editradiodevicecombobox')
		self.radiomacentry = self.ui.get_object('radiomacentry')
		self.radioanglecombobox = self.ui.get_object('radioanglecombobox')
		self.radiomodecombobox = self.ui.get_object('radiomodecombobox')
		self.antennamodecombobox = self.ui.get_object('antennamodecombobox')
		self.radiossidentry = self.ui.get_object('radiossidentry')
		self.radioprotocolcombobox = self.ui.get_object('radioprotocolcombobox')
		self.radiochannelcombobox = self.ui.get_object('radiochannelcombobox')
		self.clientscheckbutton = self.ui.get_object('clientscheckbutton')
		self.gainspinbutton = self.ui.get_object('gainspinbutton')
		self.azimuthspinbutton = self.ui.get_object('azimuthspinbutton')
		self.notebook1 = self.ui.get_object('notebook1')
		self.notebook1.set_show_tabs(False)
				
		self.cnmlp = cnmlp
		
		self.editradiodialog.show_all()
		
		self.editradiodialog.set_title(_('Create new Guifi.net radio'))
		fillNodesComboBox(self.editradionodecombobox, cnmlp.getNodes())
		
	def editradiovalidation(self):
		if not valid_mac_address(self.radiomacentry.get_text()):
			self.radiomacentry.grab_focus()
			return False
		
		return True
		
	def on_editradiodialog_response(self, widget, response):
		if response == Gtk.ResponseType.ACCEPT:
			
			if not self.editradiovalidation():
				print _("There's some invalid data")
				return
			
			it = self.radiomodecombobox.get_active_iter()
			rmode = self.radiomodecombobox.get_model().get_value(it, 0)
			
			it = self.editradiodevicecombobox.get_active_iter()
			did = self.editradiodevicecombobox.get_model().get_value(it, 0)
			
			it = self.radioanglecombobox.get_active_iter()
			rangle = self.radioanglecombobox.get_model().get_value(it, 0)
			
			it = self.antennamodecombobox.get_active_iter()
			antenna_mode = self.antennamodecombobox.get_model().get_value(it, 0)
			
			rgain = self.gainspinbutton.get_value_as_int()
			razimuth = self.azimuthspinbutton.get_value_as_int()
		
			# ap, ad-hoc, faltarian clientrouted, wirelessclient... :?
			if rmode == 'ap':
				ssid = self.radiossidentry.get_text()
				
				it = self.radioprotocolcombobox.get_active_iter()
				protocol = self.radioprotocolcombobox.get_model().get_value(it, 0)
				
				it = self.radiochannelcombobox.get_active_iter()
				channel = self.radiochannelcombobox.get_model().get_value(it, 0)
				
				clients = 'Yes' if self.clientscheckbutton.get_active() else 'No'
			elif rmode == 'ad-hoc':
				ssid = self.radiossidentry.get_text()
				
				it = self.radioprotocolcombobox.get_active_iter()
				protocol = self.radioprotocolcombobox.get_model().get_value(it, 0)
				
				it = self.radiochannelcombobox.get_active_iter()
				channel = self.radiochannelcombobox.get_model().get_value(it, 0)
				
				clients = None
			else:
				print rmode
				raise NotImplementedError
		
			
			res = CreateLocalOrRemoteMessageDialog(self.guifiAPI.getHost(), 'radio')
			
			if res in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT):
				return
				
			try:
				(radiodev_counter, interfaces) = self.guifiAPI.addRadio(rmode, did, self.radiomacentry.get_text(), angle=rangle, gain=rgain, azimuth=razimuth, 
				amode=None, ssid=ssid, protocol=protocol, channel=channel, clients=clients)
				#amode=antenna_mode when the bug is fixed
			except GuifiApiError, e:
				ErrorResponseFromServerMessageDialog(e)
				return
			
			CreatedSuccessfullyOpenUrlMessageDialog('Radio', self.guifiAPI.urlForDevice(did), radiodev_counter, interfaces)
			
		self.editradiodialog.destroy()

	def on_editradionodecombobox_changed(self, widget, data=None):
		it = self.editradionodecombobox.get_active_iter()
		nid = self.editradionodecombobox.get_model().get_value(it, 0)

		fillDevicesComboBox(self.editradiodevicecombobox, self.cnmlp.getNode(nid).getDevices())


	def on_radiomodecombobox_changed(self, widget, data=None):
		it = self.radiomodecombobox.get_active_iter()
		mode = self.radiomodecombobox.get_model().get_value(it, 0)
		
		if mode == 'ap':
			self.notebook1.set_current_page(0)
			self.clientscheckbutton.show()
		elif mode == 'ad-hoc':
			self.notebook1.set_current_page(0)
			self.clientscheckbutton.hide()
		else:
			self.notebook1.set_current_page(1)


class EditInterfaceDialog:
	def __init__(self):
		self.ui = Gtk.Builder()
		self.ui.set_translation_domain(APP_NAME)
		self.ui.add_from_file('ui/editinterfacedialog.ui')
		self.ui.connect_signals(self)

		self.editinterfacedialog = self.ui.get_object('editinterfacedialog')
		
		self.editinterfacedialog.show_all()

		self.editinterfacedialog.set_title(_('Create new Guifi.net interface'))


	def on_editinterfacedialog_response(self, widget, response):
		if response == Gtk.ResponseType.ACCEPT:
			
			"""
			if not self.editinterfacevalidation():
				print "There's some invalid data"
				return
			"""
			
			it = self.editifacedevcombobox.get_active_iter()
			did = self.editifacedevcombobox.get_model().get_value(it, 0)
			
			it = self.editifaceradiocombobox.get_active_iter()
			rid = self.editifaceradiocombobox.get_model().get_value(it, 0)
			
			res = CreateLocalOrRemoteMessageDialog(self.guifiAPI.getHost(), 'interface')
			
			if res in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT):
				return
				
			try:
				(iid, ipv4) = self.guifiAPI.addInterface(did, rid)
						
			except GuifiApiError, e:
				ErrorResponseFromServerMessageDialog(e)
				return
			
			CreatedSuccessfullyOpenUrlMessageDialog('Interface', self.guifiAPI.urlForDevice(did), iid, ipv4)
				
		self.editinterfacedialog.destroy()


class EditLinkDialog:
	def __init__(self, nodes):
		self.ui = Gtk.Builder()
		self.ui.set_translation_domain(APP_NAME)
		self.ui.add_from_file('ui/editlinkdialog.ui')
		self.ui.connect_signals(self)

		self.editlinkdialog = self.ui.get_object('editlinkdialog')
		self.editlinknode1combobox = self.ui.get_object('editlinknode1combobox')
		self.editlinknode2combobox = self.ui.get_object('editlinknode2combobox')

		self.editlinkdialog.show_all()

		self.editlinkdialog.set_title(_('Create new Guifi.net link'))
		fillNodesComboBox(self.editlinknode1combobox, nodes)
		fillNodesComboBox(self.editlinknode2combobox, nodes)


	def on_editlinkdialog_response(self, widget, response):
		if response == Gtk.ResponseType.ACCEPT:
			
			"""
			if not self.editlinkvalidation():
				print "There's some invalid data"
				return
			"""
			
			it = self.editlinknode1combobox.get_active_iter()
			nid1 = self.editlinknode1combobox.get_model().get_value(it, 0)
			
			it = self.editlinknode2combobox.get_active_iter()
			nid2 = self.editlinknode2combobox.get_model().get_value(it, 0)
			
			it = self.editlinkdev1combobox.get_active_iter()
			dev1 = self.editlinkdev1combobox.get_model().get_value(it, 0)
			
			it = self.editlinkdev2combobox.get_active_iter()
			dev2 = self.editlinkdev2combobox.get_model().get_value(it, 0)
			
			it = self.editlinkradio1combobox.get_active_iter()
			radio1 = self.editlinkradio1combobox.get_model().get_value(it, 0)
			
			it = self.editlinkradio2combobox.get_active_iter()
			radio2 = self.editlinkradio2combobox.get_model().get_value(it, 0)
			
			ipv4 = self.editlinkipv4entry.get_text()
			
			it = self.editlinkstatuscombobox.get_active_iter()
			status = self.editlinkstatuscombobox.get_model().get_value(it, 0)
			
			res = CreateLocalOrRemoteMessageDialog(self.guifiAPI.getHost(), 'link')
			
			if res in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT):
				return
				
			try:
				(lid, ipv4) = self.guifiAPI.addLink(dev1, radio1, dev2, radio2, ipv4=ipv4, status=status)
						
			except GuifiApiError, e:
				ErrorResponseFromServerMessageDialog(e)
				return
			
			CreatedSuccessfullyOpenUrlMessageDialog('Link', self.guifiAPI.urlForDevice(dev1), lid, ipv4)
				
		self.editlinkdialog.destroy()
		
		
		
class CNMLDialog:
	def __init__(self, configmanager, zonecnmlp, allZones, guifiAPI):
		self.ui = Gtk.Builder()
		self.ui.set_translation_domain(APP_NAME)
		self.ui.add_from_file('ui/cnmldialog.ui')
		self.ui.connect_signals(self)

		self.zonecnmlp = zonecnmlp
		self.configmanager = configmanager
		self.guifiAPI = guifiAPI
		self.cnmldialog = self.ui.get_object('cnmldialog')
		self.treeview4 = self.ui.get_object('treeview4')
		self.entrycompletion1 = self.ui.get_object('entrycompletion1')
		
		self.cnmldialog.show_all()

		if zonecnmlp:
			fillAvailableCNMLModel(self.configmanager, self.treeview4.get_model(), self.zonecnmlp)
			fillZonesEntryCompletion(self.entrycompletion1, allZones)
		else:
			# allZones == []
			print _("Error: there's no guifi.net world zones cnml")
			message = _("Guifi.net World zones CNML file couldn't be found\n\nYou have to download it first by going to Tools -> Update zones")
			g = Gtk.MessageDialog(None, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, message)
			g.set_title(_('File not found'))
			g.run()
			g.destroy()
			self.cnmldialog.destroy()
			
	
	def on_downloadbutton_clicked(self, widget, data=None):
		zid = findZoneIdInEntryCompletion(self.entrycompletion1)
		
		if zid is None:
			return False
			
		print _('Downloading zone:'), zid
		
		ctype = 'detail'
		fp = self.guifiAPI.downloadCNML(zid, ctype)
		filename = self.configmanager.pathForCNMLCachedFile(zid, ctype)
		with open(filename, 'w') as zonefile:
			zonefile.write(fp.read())
		print _('CNML (%s) saved successfully to') %ctype, filename
		
		#Reload
		fillAvailableCNMLModel(self.configmanager, self.treeview4.get_model(), self.zonecnmlp)
		
	def on_cnmldialog_response(self, widget, response):
		self.cnmldialog.destroy()

	
class PreferencesDialog:
	def __init__(self, configmanager, zonecnmlp, allZones):
		self.ui = Gtk.Builder()
		self.ui.set_translation_domain(APP_NAME)
		self.ui.add_from_file('ui/preferencesdialog.ui')
		self.ui.connect_signals(self)

		self.configmanager = configmanager
		
		self.preferencesdialog = self.ui.get_object('preferencesdialog')
		self.userentry = self.ui.get_object('userentry')
		self.passwordentry = self.ui.get_object('passwordentry')
		self.defaultzoneentry = self.ui.get_object('defaultzoneentry')
		self.entrycompletion2 = self.ui.get_object('entrycompletion2')
		self.usekeyringbutton = self.ui.get_object('usekeyringbutton')
		self.entrycompletion2 = self.ui.get_object('entrycompletion2')
		self.contactentry = self.ui.get_object('contactentry')
		self.hostentry = self.ui.get_object('hostentry')
		
		self.preferencesdialog.show_all()

		self.userentry.set_text(self.configmanager.getUsername())
		self.passwordentry.set_text(self.configmanager.getPassword())
		self.contactentry.set_text(self.configmanager.getContact())
		self.hostentry.set_text(self.configmanager.getHost())
		
		if allZones == []:
			self.defaultzoneentry.set_sensitive(False)
			label39 = self.ui.get_object('label39')
			label39.set_sensitive(False)
		else:
			fillZonesEntryCompletion(self.entrycompletion2, allZones)
		
		if zonecnmlp:
			defaultZoneTitle = zonecnmlp.getZone(self.configmanager.getDefaultZone()).title
			self.entrycompletion2.get_entry().set_text(defaultZoneTitle)
		else:
			print _("Error: there's no Guifi.net world zones CNML")
		
		
	def on_preferencesdialog_response(self, widget, response):
		if response == Gtk.ResponseType.ACCEPT:
			self.configmanager.setUsername(self.userentry.get_text())
			self.configmanager.setPassword(self.passwordentry.get_text())
			self.configmanager.setContact(self.contactentry.get_text())
			
			# How can I get the GtkTreeIter from the "active item" in GtkEntry/GtkEntryCompletion?
			# Otherwise: loop :-S		
			zid = findZoneIdInEntryCompletion(self.entrycompletion2)
			
			if zid:
				self.configmanager.setDefaultZone(zid)
				
			self.configmanager.save()
			
		self.preferencesdialog.destroy()


class NodeDialog:
	def __init__(self):
		self.ui = Gtk.Builder()
		self.ui.set_translation_domain(APP_NAME)
		self.ui.add_from_file('ui/nodedialog.ui')
		self.ui.connect_signals(self)

		self.nodedialog = self.ui.get_object("nodedialog")
		self.nodedialog.set_title(_('Information about node'))
		self.nodedialog.show_all()
		
		
	def on_nodedialog_response(self, widget, response):
		self.nodedialog.destroy()
		

class ChangeZoneDialog:
	def __init__(self, configmanager, zonecnmlp):
		self.ui = Gtk.Builder()
		self.ui.set_translation_domain(APP_NAME)
		self.ui.add_from_file('ui/changezonedialog.ui')
		self.ui.connect_signals(self)

		self.okbutton = self.ui.get_object('okbutton')
		self.changezonedialog = self.ui.get_object('changezonedialog')
		self.zonescombobox = self.ui.get_object('zonescombobox')
	
		model = self.zonescombobox.get_model()
		fillAvailableCNMLModel2(configmanager, model, zonecnmlp)
		
		defaultzone = configmanager.getDefaultZone()
		# FIXME: It's not defaultzone but current zone being displayed
		if defaultzone is not None:
			it = model.get_iter_first()
			n = 0
			while it:
				zid = model.get_value(it, 0)
				if zid == defaultzone:
					self.zonescombobox.set_active(n)
					break
				it = model.iter_next(it)
				n += 1
					
#		self.changezonedialog.show_all()
		
	def run(self):
		return self.changezonedialog.run()
		
		
	def getSelectedZone(self):
		it = self.zonescombobox.get_active_iter()
		zid = self.zonescombobox.get_model().get_value(it, 0)
		return zid
		
		
	def destroy(self):
		self.changezonedialog.destroy()
		
###################################################
#self.cnmlp.getNodes()
def fillNodesComboBox(combobox, nodes):
	model = combobox.get_model()
	model.clear()
	model.set_sort_column_id (1, Gtk.SortType.ASCENDING)
	
	# zoneid - title
	for n in nodes:
		model.append((n.id, n.title))
			
		
# self.cnmlp.getZones()
def fillZonesComboBox(combobox, zones):
	# zoneid - title
	model = combobox.get_model()
	model.clear()
	model.set_sort_column_id (1, Gtk.SortType.ASCENDING)
	model.append((0, '-- '+_('Most recently used')+' --'))
		
	n = 0
	for z in zones:
		n +=1
		model.append((z.id, z.title))
	combobox.set_active(n)


# node.getDevices()
def fillDevicesComboBox(combobox, devices):
	# We only want radios
	model = combobox.get_model()
	model.clear()
	model.set_sort_column_id (1, Gtk.SortType.ASCENDING)
	
	for dev in devices:
		print dev.title, dev.type
		if dev.type == 'radio':
			model.append((dev.id, dev.title))
		
		
#self.cnmlp.getZones()
# allZones
def fillZonesEntryCompletion(entrycompletion, allZones):
	model = entrycompletion.get_model()
	model.clear()
		
	for z in allZones:
		model.append((z[0], z[1]))


def fillAvailableCNMLModel(configmanager, model, zonecnmlp):
	cnmls = dict()
	model.clear()
	
	for d in ['nodes', 'zones', 'detail']:
		directory = os.path.join(configmanager.CACHE_DIR, d)
		filelist = os.listdir(directory)
		for f in filelist:
			zid, ext = f.split('.')
			zid = int(zid)
			if ext == 'cnml':
				if not cnmls.has_key(zid):
					cnmls[zid] = dict()
					cnmls[zid]['nodes'] = False
					cnmls[zid]['zones'] = False
					cnmls[zid]['detail'] = False
				cnmls[zid][d] = True
	
	for zid in cnmls:
		model.append((zid, zonecnmlp.getZone(zid).title, cnmls[zid]['nodes'], cnmls[zid]['zones'], cnmls[zid]['detail']))


def fillAvailableCNMLModel2(configmanager, model, zonecnmlp):
	
	directory = os.path.join(configmanager.CACHE_DIR, 'detail')
	filelist = os.listdir(directory)
	for f in filelist:
		zid, ext = f.split('.')
		zid = int(zid)
		if ext == 'cnml':
			model.append((zid, zonecnmlp.getZone(zid).title))


def	ErrorResponseFromServerMessageDialog(e):
	errormessage = _('Error %d: %s\n\nError message:\n%s') %(e.code, e.reason, e.extra)
	g = Gtk.MessageDialog(None, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, errormessage)
	g.set_title(_('Response from server'))
	g.run()
	g.destroy()
	

def CreateLocalOrRemoteMessageDialog(host, what, title=None):
	# Messagebox (internet / local / cancelar)
	if what in ('radio', 'interface', 'link'):
		message = _('You are about to create a new %s.\nPlease choose where you want to create it') %what
	else:
		message = _('You are about to create the %s named "%s".\nPlease choose where you want to create it') %(what, title)
		
	g = Gtk.MessageDialog(None, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.CANCEL, message)
	g.set_title('Confirmation')
	g.add_button('Create locally\n(CNML)', -12)
	g.add_button('Create remotely\n(%s)' %host, -13)
	res = g.run()
	g.destroy()
	return res


def CreatedSuccessfullyOpenUrlMessageDialog(what, url, id, extra=None):
	if what in ('Interface', 'Link'):
		# ipv4 = extra
		message = _('%s successfully created with id %d\n\nInformation:\n') %(what,id)

		for settings in extra[0].items():
			message += '  %s: %s\n' %settings
			print '%s - %s' %settings
		
		message += _('\nYou can view it in the following url:\n%s') %url

	elif what == 'Radio':
		# interfaces = extra 
		message = _('Radio successfully created with id %d\n\nInformation:\n') %id

		for iface in extra:
			for ifaceitems in iface.items():
				if isinstance(ifaceitems[1], list):
					for ips in ifaceitems[1]:
						for ipv4 in ips.items():
							message += '    %s: %s\n' %ipv4
							print '  %s - %s' %ipv4
				else:
					message += '  %s: %s\n' %ifaceitems
					print '%s - %s' %ifaceitems
		
		message += _('\nYou can view it in the following url:\n%s') %url
			
	else:
		message = _('%s succesfully created with id %d\n\nYou can view it in the following url:\n%s') %(what, id, url)
		
	g = Gtk.MessageDialog(None, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.INFO, Gtk.ButtonsType.CLOSE, message)
	g.add_button(_('Open in web browser'), -12)
	g.set_title(_('Response from server'))
	res = g.run()
	g.destroy()
	
	if res != Gtk.ResponseType.CLOSE:
		openUrl(url)


# temporary method until I find a better way to do it
def findZoneIdInEntryCompletion(entrycompletion):
	model = entrycompletion.get_model()
	it = model.get_iter_first()
	
	title = entrycompletion.get_entry().get_text()
	
	while it:
		zone = model.get_value(it, 1)
		if zone.lower() == title.lower():
			break
		it = model.iter_next(it)
	
	if it is None:
		print _('ERROR: Zone title not found!')
		return None
	else:
		pass
		# - msgbox showing problem
		# - dont change
		# ...
		
	zid = model.get_value(it, 0)
	return zid
