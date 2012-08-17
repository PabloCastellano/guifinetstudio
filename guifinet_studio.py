#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# guifinet_studio.py - Explore your free network offline!
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


from gi.repository import GtkClutter, Clutter
GtkClutter.init([]) # Must be initialized before importing those:
from gi.repository import Gdk, Gtk
from gi.repository import GtkChamplain, Champlain

import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('lib')

from libcnml import CNMLParser, Status
import pyGuifiAPI
from pyGuifiAPI.error import GuifiApiError

from configmanager import GuifinetStudioConfig

from utils import *

from urllib2 import URLError

from ui import *

from datetime import datetime, timedelta

from champlainguifinet import GtkGuifinetMap

from calc import Calculator

import locale, gettext
gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
gettext.textdomain(APP_NAME)
locale.setlocale(locale.LC_ALL, '')
locale.bindtextdomain(APP_NAME, LOCALE_DIR)
_ = gettext.gettext


class GuifinetStudio:
	def __init__(self, cnmlFile=None):
		self.ui = Gtk.Builder()
		self.ui.set_translation_domain(APP_NAME)
		self.ui.add_from_file('ui/mainwindow.ui')
		self.ui.connect_signals(self)

		self.mainWindow = self.ui.get_object('mainWindow')
		self.listNodesWindow = self.ui.get_object('listNodesWindow')
		
		self.nodesList = self.ui.get_object("scrolledwindow1")
		self.treestore = self.ui.get_object("treestore1")
		self.treestore2 = self.ui.get_object("treestore2")
		self.treeview = self.ui.get_object("treeview1")
		self.treeview2 = self.ui.get_object("treeview2")
		self.treemodelfilter2 = self.ui.get_object('treemodelfilter2')
		searchentry = self.ui.get_object('searchentry')
		self.treemodelfilter2.set_visible_func(filterbyname_func, searchentry)
		self.statusbar = self.ui.get_object("statusbar1")
		self.actiongroup1 = self.ui.get_object("actiongroup1")
		self.menuitem6 = self.ui.get_object("menuitem6")

		self.notebook1 = self.ui.get_object("notebook1")
		self.notebook1.set_show_tabs(False)
		
		self.guifinetmap = GtkGuifinetMap(self)
		
		self.box1 = self.ui.get_object('box1')
		self.paned = self.ui.get_object("paned1")
		self.paned.pack2(self.guifinetmap, True, True)
		
		self.uimanager = Gtk.UIManager()
		self.uimanager.add_ui_from_file("guifinet_studio_menu.ui")
		self.uimanager.insert_action_group(self.actiongroup1)
		self.menu1 = self.uimanager.get_widget("/KeyPopup1")

		self.t6 = self.ui.get_object("treeviewcolumn6")
			
		self.mainWindow.show_all()

		# configuration
		self.configmanager = GuifinetStudioConfig()

		if not cnmlFile:
			# Load default zone cnml
			defaultzone = self.configmanager.getDefaultZone()
			if defaultzone is not None:
				ztype = self.configmanager.getDefaultZoneType()
				cnmlFile = self.configmanager.pathForCNMLCachedFile(defaultzone, ztype)
			else:
				# no default zone
				self.cnmlp = None
				msg = _('No default zone. Please choose one')
				print msg
				self.statusbar.push(0, msg)
				self.cnmlp = None
				self.cnmlFile = None
		
		if cnmlFile:
			# CNMLParser
			try:
				self.cnmlp = CNMLParser(cnmlFile)
				self.cnmlFile = cnmlFile
				self.statusbar.push(0, _('Loaded "%s" successfully') %self.cnmlFile)
				self.completaArbol()
				self.guifinetmap.paintMap(self.cnmlp.getNodes())
			except IOError:
				print _('Error loading CNML')
				self.statusbar.push(0, _('CNML file "%s" couldn\'t be loaded') %cnmlFile)
				self.cnmlp = None
				self.cnmlFile = None
		
			
		# Guifi.net API
		if self.configmanager.getUsername() is None or self.configmanager.getPassword() is None or self.configmanager.getHost() is None:
			print _('Some required data to initialize Guifi.net API is not available.')
			print _('Please check username, password and host in preferences')
		self.guifiAPI = pyGuifiAPI.GuifiAPI(self.configmanager.getUsername(), self.configmanager.getPassword(), self.configmanager.getHost(), secure=False)
		self.authAPI()
		
		# TODO: Generate an intermediary file for allZones instead of loading the cnml everytime
		self.allZones = []
		self.rebuildAllZones()

      
	def on_fullscreenmenuitem_toggled(self, widget, data=None):
		isActive = widget.get_active()

		if isActive:
			self.mainWindow.fullscreen()
		else:
			self.mainWindow.unfullscreen()


	def on_exportgmlimagemenuitem_activate(self, widget, data=None):
		print _('Export to GML')
		raise NotImplementedError
		
		
	def on_exportkmlimagemenuitem_activate(self, widget, data=None):
		dialog = Gtk.FileChooserDialog(_('Save KML file'), self.mainWindow,
				Gtk.FileChooserAction.SAVE,
				(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT))

		if dialog.run() == Gtk.ResponseType.ACCEPT:
			filename = dialog.get_filename()
			print filename
		
		dialog.destroy()
		
		print _('Export to KML')
		CNML2KML(self.cnmlp, filename)
		
		
	def rebuildAllZones(self):
		cnmlGWfile = self.configmanager.pathForCNMLCachedFile(GUIFI_NET_WORLD_ZONE_ID, 'zones')
		try:
			self.zonecnmlp = CNMLParser(cnmlGWfile)
			for z in self.zonecnmlp.getZones():
				self.allZones.append((z.id, z.title))
		except IOError:
			print _('Error loading cnml guifiworld zone:'), cnmlGWfile
			print _('Guifi.net Studio will run normally but note that some features are disabled')
			print _('To solve it, just download the Guifi.net World zones CNML going to Tools -> Update zones')
			
			message = _('Error loading Guifi.net World zone\n\n')
			message += _('Guifi.net Studio will run normally but note that some features are disabled\n')
			message += _('To solve it, just download the Guifi.net World zones CNML again\n')
			message += _('You can go to Tools -> Update zones')
			g = Gtk.MessageDialog(None, Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE, message)
			g.set_title(_('File not found: %s') %cnmlGWfile)
			res = g.run()
			g.destroy()
			self.statusbar.push(0, _('CNML file "%s" couldn\'t be loaded') %cnmlGWfile)
			self.zonecnmlp = None


	def on_calcimagemenuitem_activate(self, widget, data=None):
		Calculator()

		
	def on_searchentry_changed(self, widget, data=None):
		print widget, data
		print widget.get_text()
		
		nodesfilter = self.treeview2.get_model()
		nodesfilter.refilter()   
		return False
		
		
	def completaArbol(self):
		self.treestore.clear()
		self.treestore2.clear()
		# Add root zone
		parenttree = self.__addZoneToTree(self.cnmlp.rootzone, None)
		self.__addNodesFromZoneToTree(self.cnmlp.rootzone, parenttree)
		
		# Iter for every zone (except root) and adds them with nodes to the TreeView
		self.__completaArbol_recursive(self.cnmlp.rootzone, parenttree)
										
		self.treeview.expand_all()
		
		self.treestore.set_sort_column_id (5, Gtk.SortType.ASCENDING)
		self.treestore2.set_sort_column_id (0, Gtk.SortType.ASCENDING)
		self.statusbar.push(0, _('CNML loaded successfully'))


	# Recursive
	def __completaArbol_recursive(self, parentzid, parenttree):
		zones = self.cnmlp.getSubzonesFromZone(parentzid)
		
		for z in zones:
			tree = self.__addZoneToTree(z.id, parenttree)
			self.__addNodesFromZoneToTree(z.id, tree)
			self.__completaArbol_recursive(z.id, tree)
			
		
	def __addZoneToTree(self, zid, parentzone):
		
		# Given a list of node ids, counts how many of them are for each status (working, planned...)
		def countNodes(nodes):
			nodescount = dict()
			nodescount[Status.RESERVED] = 0
			nodescount[Status.PLANNED] = 0
			nodescount[Status.WORKING] = 0
			nodescount[Status.TESTING] = 0
			nodescount[Status.BUILDING] = 0
			nodescount[Status.DROPPED] = 0
			
			for n in nodes:
				nodescount[n.status] += 1
			
			return (nodescount[Status.PLANNED], nodescount[Status.WORKING], nodescount[Status.TESTING], nodescount[Status.BUILDING])

		zone = self.cnmlp.getZone(zid)
		nodes = zone.getNodes()
		
		col1 = "%s (%d)" %(zone.title, len(nodes))
		(nplanned, nworking, ntesting, nbuilding) = countNodes(nodes)

		# Add a new row for the zone
		row = (col1, str(nworking), str(nbuilding), str(ntesting), str(nplanned), None, None)
		tree = self.treestore.append(parentzone, row)
		return tree
		
		
	def create_new_node(self, coords):
		EditNodeDialog(self.guifiAPI, self.cnmlp.getZones(), self.zonecnmlp, self.allZones, coords)

	
	def __addNodesFromZoneToTree(self, zid, parentzone):
		nodes = self.cnmlp.getNodesFromZone(zid)
		for n in nodes:
			row = (None, None, None, None, None, n.title, n.id)
			self.treestore.append(parentzone, row)
			self.treestore2.append(None, (n.title, n.id))


	def on_action1_activate(self, action, data=None):
		NodeDialog()
	
	
	def on_action2_activate(self, action, data=None):
		# get node id
		sel = self.treeview.get_selection()
		(model, it) = sel.get_selected()
		nid = model.get_value(it, 6)

		Gtk.show_uri(None, self.guifiAPI.urlForNode(nid), Gtk.get_current_event_time())


	def on_action3_activate(self, action, data=None):
		self.notebook1.set_current_page(0)		

		# get node id
		sel = self.treeview.get_selection()
		(model, it) = sel.get_selected()
		nid = model.get_value(it, 6)
		
		lat = self.cnmlp.getNode(nid).latitude
		lon = self.cnmlp.getNode(nid).longitude	
	
		self.guifinetmap.getView().center_on(lat, lon)
		
	
	
	def on_action4_activate(self, action, data=None):
		# get node id
		sel = self.treeview.get_selection()
		(model, it) = sel.get_selected()
		nid = model.get_value(it, 6)
			
		# Varias interfaces - varios unsolclic
		# TODO: Ventana con la interfaz seleccionable que quieras generar
		devices = self.cnmlp.nodes[nid].devices
		
		if devices == {}:
			g = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, 
								_("Couldn't generate unsolclick.\nThe node doesn't have any device defined."))
			g.set_title(_('Error generating unsolclic'))
			g.run()
			g.destroy()
			return
		elif len(devices) > 1:
			g = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.WARNING, Gtk.ButtonsType.CLOSE, 
								_('Several devices in this node. Generating just the first one.'))
			g.set_title(_('Warning generating unsolclic'))
			g.run()
			g.destroy()
		
		node = self.cnmlp.nodes[nid]
		
		UnsolclicDialog(node)
		########
			
	
	def on_imagemenuitem2_activate(self, widget, data=None):
		dialog = Gtk.FileChooserDialog(_('Open CNML file'), self.mainWindow,
				Gtk.FileChooserAction.OPEN,
				(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))

		if dialog.run() == Gtk.ResponseType.ACCEPT:
			self.cnmlFile = dialog.get_filename()
			print self.cnmlFile
		
			try:
				self.cnmlp = CNMLParser(self.cnmlFile)
				# FIXME: only if necessary (there's a zone loaded already)
				self.on_imagemenuitem3_activate()
				self.completaArbol()
				self.guifinetmap.paintMap(self.cnmlp.getNodes())
			except IOError:
				self.statusbar.push(0, _('CNML file "%s" couldn\'t be loaded') %self.cnmlFile)
				self.cnmlFile = None
		
		dialog.destroy()
				
		
	def on_imagemenuitem3_activate(self, widget=None, data=None):
		self.treestore.clear()
		self.treestore2.clear()
		self.guifinetmap.reset()
		self.statusbar.push(0, _('Closed CNML file'))
		self.cnmlFile = None
		
		
	def gtk_main_quit(self, widget, data=None):
		Gtk.main_quit()
	
	
	def on_createnodemenuitem_activate(self, widget=None, data=None):
		EditNodeDialog(self.guifiAPI, self.cnmlp.getZones(), self.zonecnmlp, self.allZones)
	
	
	def on_createzonemenuitem_activate(self, widget, data=None):
		EditZoneDialog(self.guifiAPI, self.cnmlp.getZones())
		
	def on_createdevicemenuitem_activate(self, widget, data=None):
		EditDeviceDialog(self.guifiAPI, self.cnmlp.getNodes())
		
		
	def on_createradiomenuitem_activate(self, widget, data=None):
		EditRadioDialog(self.guifiAPI, self.cnmlp)
		
		
	def on_createinterfacemenuitem_activate(self, widget, data=None):
		EditInterfaceDialog()
	
	
	def on_createlinkmenuitem_activate(self, widget, data=None):
		EditLinkDialog(self.cnmlp.getNodes())

	
	def on_preferencesmenuitem_activate(self, widget, data=None):
		PreferencesDialog(self.configmanager, self.cnmlp.getZones(), self.zonecnmlp, self.allZones)
		
				
	def on_menuitem5_toggled(self, widget, data=None):
		isActive = widget.get_active()
		
		if isActive:
			self.statusbar.show()
		else:
			self.statusbar.hide()


	def on_menuitem6_toggled(self, widget, data=None):
		isActive = widget.get_active()
		
		if isActive:
			self.box1.show()
		else:
			self.box1.hide()

		
	def zoom_in(self, widget, data=None):
		self.view.zoom_in()
		
		
	def zoom_out(self, widget, data=None):
		self.view.zoom_out()
		

	def on_changezoneimagemenuitem_activate(self, widget, data=None):
		dialog = ChangeZoneDialog(self.configmanager, self.zonecnmlp)

		if dialog.run() == Gtk.ResponseType.ACCEPT:
			
			zid = dialog.getSelectedZone()
			filename = self.configmanager.pathForCNMLCachedFile(zid, 'detail')
		
			try:
				self.cnmlp = CNMLParser(filename)
				# FIXME: only if necessary (there's a zone loaded already)
				self.on_imagemenuitem3_activate()
				self.completaArbol()
				self.guifinetmap.paintMap(self.cnmlp.getNodes())
				self.cnmlFile = filename
			except IOError:
				self.statusbar.push(0, _('CNML file "%s" couldn\'t be loaded') %filename)
				self.cnmlFile = None
				
		dialog.destroy()
		
	def on_downloadcnmlmenuitem_activate(self, widget, data=None):
		CNMLDialog(self.configmanager, self.zonecnmlp, self.allZones, self.guifiAPI)
	
	
	def on_updatezonesmenuitem_activate(self, widget, data=None):
		try:
			fp = self.guifiAPI.downloadCNML(GUIFI_NET_WORLD_ZONE_ID, 'zones')
			filename = self.configmanager.pathForCNMLCachedFile(GUIFI_NET_WORLD_ZONE_ID, 'zones')
			with open(filename, 'w') as zonefile:
				zonefile.write(fp.read())
			print _('Zone saved successfully to'), filename
			self.rebuildAllZones()
		except URLError, e:
			print _('Error accessing to the Internets:'), str(e.reason)
			g = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, 
								_('Error accessing to the Internets:\n') + str(e.reason))
			g.set_title(_('Error downloading CNML'))
			g.run()
			g.destroy()
		

	def on_imagemenuitem10_activate(self, widget, data=None):
		dialog = Gtk.AboutDialog()
		dialog.set_program_name('Guifi·net Studio')
		dialog.set_version('v1.0')
		dialog.set_copyright('Copyright © 2011-2012 Pablo Castellano')
		dialog.set_comments(_('Grow your own Internets!'))
		dialog.set_website('http://lainconscienciadepablo.net')
		dialog.set_website_label(_("Author's blog"))
		dialog.set_license_type(Gtk.License.GPL_3_0)
	
		with open("AUTHORS") as f:
			authors_list = []
			for line in f.readlines():
				authors_list.append(line.strip())
			dialog.set_authors(authors_list)
		
		with open("COPYING") as f:
			dialog.set_license(f.read())
		
		dialog.run()
		dialog.destroy()
		

	def on_maptoolbutton_clicked(self, widget, data=None):
		self.notebook1.set_current_page(0)
		
		
	def on_nodestoolbutton_clicked(self, widget, data=None):
		self.notebook1.set_current_page(1)
		
		
	def on_servicestoolbutton_clicked(self, widget, data=None):
		self.notebook1.set_current_page(2)
		
		
	def on_button5_clicked(self, widget, data=None):
		self.box1.hide()
		self.menuitem6.set_active(False)

			
	def on_treeview1_button_release_event(self, widget, data=None):
		sel = widget.get_selection()
		(model, it) = sel.get_selected()

		if it is None: # treeview is clear
			return True
			
		col = widget.get_path_at_pos(int(data.x), int(data.y))[1]
		
		if data.button == 3: # Right button
			if col is self.t6 and model.get_value(it, 5) is not None: 
				#user clicked on a node
				self.menu1.popup(None, None, None, None, data.button, data.time)
	

	def on_treeview2_button_release_event(self, widget, data=None):
		sel = widget.get_selection()
		(model, it) = sel.get_selected()
		
		if it is None: # treeview is clear
			return True
		
		if data.button == 1: # Right button
			nid = model.get_value(it, 1)
			lat = float(self.cnmlp.getNode(nid).latitude)
			lon = float(self.cnmlp.getNode(nid).longitude)
			self.guifinetmap.getView().center_on(lat, lon)
			#self.view.go_to(lat, lon)
		
	
	def on_treeview2_key_press_event(self, widget, data=None):
		sel = widget.get_selection()
		(model, it) = sel.get_selected()
		
		if data.keyval == Gdk.KEY_space or data.keyval == Gdk.KEY_KP_Space	or data.keyval == Gdk.KEY_Return or data.keyval == Gdk.KEY_KP_Enter:
			nid = model.get_value(it, 1)
			lat = float(self.cnmlp.getNode(nid).latitude)
			lon = float(self.cnmlp.getNode(nid).longitude)
			self.view.center_on(lat, lon)
			#self.view.go_to(lat, lon)
			
			
	def on_showPointsButton_toggled(self, widget, data=None):
		self.guifinetmap.show_points(widget.get_active())
		
		
	def on_showLabelsButton_toggled(self, widget, data=None):
		self.guifinetmap.show_labels(widget.get_active())
	
	
	def on_showLinksButton_toggled(self, widget, data=None):
		raise NotImplementedError
	

	def on_showZonesButton_toggled(self, widget, data=None):
		raise NotImplementedError
		
		
	def on_treeviewcolumn6_clicked(self, action, data=None):
		#print action.get_sort_column_id()
		(column_id, sorttype) = self.treestore.get_sort_column_id()
		name = action.get_name()
		
		if sorttype == Gtk.SortType.ASCENDING:
			sorttype = Gtk.SortType.DESCENDING
		else:
			sorttype = Gtk.SortType.ASCENDING
			
		# 'treeview1, treeview2, treeview3, ..., treeview6
		column_id = int(name[-1]) -1
		
		self.treestore.set_sort_column_id (column_id, sorttype)

				
	def authAPI(self):
		tokendate = self.configmanager.getAuthTokenDate()

		now = datetime.now()
		yesterday = now - timedelta(1)
		
		if now-yesterday <= timedelta(1):
			# auth token is still valid (if it hasn't been requested by another application)
			authToken = self.configmanager.getAuthToken()
		else:
			authToken = None
		
		if authToken:
			print _('Reusing valid auth token:'), authToken
			self.guifiAPI.setAuthToken(authToken)
		else:
			print _('not valid token -> authenticating...')
			
			try:
				self.guifiAPI.auth()
				self.configmanager.setAuthToken(self.guifiAPI.getAuthToken())
				self.configmanager.setAuthTokenDate() #update with now()
				self.configmanager.save()
				self.statusbar.push(0, _('Logged into Guifi.net'))
			except URLError, e: # Not connected to the Internets
				self.statusbar.push(0, _("Couldn't login into Guifi.net: check your Internet connection"))
			except GuifiApiError, e:
				g = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, 
									_("Couldn't login into Guifi.net:\n") + e.reason)
				g.run()
				g.destroy()
		

		
if __name__ == "__main__":

	if len(sys.argv) > 1:
		main = GuifinetStudio(sys.argv[1])
	else:
		main = GuifinetStudio()

	Gtk.main()
