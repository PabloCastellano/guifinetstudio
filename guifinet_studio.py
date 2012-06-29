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
from gi.repository import Gtk, GtkChamplain, Champlain

import jinja2

import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from libcnml import CNMLParser, Status
from unsolclic import UnSolClic

class GuifinetStudio:
	def __init__(self, cnmlFile="tests/detail.3"):
		self.currentView = 0
		self.cnmlFile = cnmlFile
		self.points_layer = None
		self.labels_layer = None
		
		# Unsolclic instance
		self.usc = UnSolClic()

		# UI Widgets
		self.ui = Gtk.Builder()
		self.ui.add_from_file("guifinet_studio.ui")
		self.ui.connect_signals(self)

		self.mainWindow = self.ui.get_object("mainWindow")
		self.listNodesWindow = self.ui.get_object("listNodesWindow")
		
		self.nodesList = self.ui.get_object("scrolledwindow1")
		self.treestore = self.ui.get_object("treestore1")
		self.treeview = self.ui.get_object("treeview1")
		self.statusbar = self.ui.get_object("statusbar1")
		self.actiongroup1 = self.ui.get_object("actiongroup1")

		self.embedBox = self.ui.get_object("embedBox")
		self.notebook1 = self.ui.get_object("notebook1")
		
		self.embed = GtkChamplain.Embed()
		self.embed.set_size_request(640, 480)
		
		self.view = self.embed.get_view()
		self.view.set_reactive(True)
		self.view.set_kinetic_mode(True)
		self.view.set_zoom_level(13)
		self.view.center_on(36.72341, -4.42428)
        
		scale = Champlain.Scale()
		scale.connect_view(self.view)
		self.view.bin_layout_add(scale, Clutter.BinAlignment.START, Clutter.BinAlignment.END)

		self.embedBox.pack_start(self.embed, True, True, 0)
		self.embedBox.reorder_child(self.embed, 0)
				
		self.uimanager = Gtk.UIManager()
		self.uimanager.add_ui_from_file("guifinet_studio_menu.ui")
		self.uimanager.insert_action_group(self.actiongroup1)
		self.menu = self.uimanager.get_widget("/KeyPopup")

		self.t6 = self.ui.get_object("treeviewcolumn6")
		self.nodedialog = self.ui.get_object("nodeDialog")
		self.uscdialog = self.ui.get_object("uscdialog")
		self.usctextbuffer = self.ui.get_object("usctextbuffer")
		
		self.opendialog = self.ui.get_object("filechooserdialog1")
		self.opendialog.set_action(Gtk.FileChooserAction.OPEN)
		
		self.about_ui = self.ui.get_object("aboutdialog1")

		with open("COPYING") as f:
			self.about_ui.set_license(f.read())

		try:
			self.cnmlp = CNMLParser(self.cnmlFile)
			self.completaArbol()
			self.completaMapa()
		except IOError:
			self.statusbar.push(0, "CNML file \"%s\" couldn't be loaded" %self.cnmlFile)
			self.cnmlFile = None

		self.mainWindow.show_all()


	def add_node_point(self, layer, lat, lon, size=12):
		p = Champlain.Point.new()
		p.set_location(lat, lon)
		p.set_size(size)
		layer.add_marker(p)
	
	def add_node_label(self, layer, lat, lon, nombre):
		p = Champlain.Label.new()
		p.set_text(nombre)
		color = Clutter.Color.new(0, 0, 0, 255)
		p.set_text_color(color)
		p.set_location(lat, lon)
		p.set_draw_background(False)
		layer.add_marker(p)

	def completaMapa(self):
		self.points_layer = Champlain.MarkerLayer()
		self.points_layer.set_selection_mode(Champlain.SelectionMode.SINGLE)
		self.labels_layer = Champlain.MarkerLayer()

		data = self.cnmlp.getData()

		for nid in data.keys():
			self.add_node_point(self.points_layer, data[nid]['lat'], data[nid]['lon'])
			self.add_node_label(self.labels_layer, data[nid]['lat'], data[nid]['lon'], data[nid]['title'])
		
		# It's important to add points the last. Points are selectable while labels are not
		# If labels is added later, then you click on some point and it doesn't get selected
		# because you are really clicking on the label. Looks like an usability bug?
		self.view.add_layer(self.labels_layer)
		self.view.add_layer(self.points_layer)
		

	def completaArbol(self):
		# Add root zone
		parenttree = self.__addZoneToTree(self.cnmlp.rootzone, None)
		self.__addNodesFromZoneToTree(self.cnmlp.rootzone, parenttree)
		
		# Iter for every zone (except root) and adds them with nodes to the TreeView
		self.__completaArbol_recursive(self.cnmlp.rootzone, parenttree)
										
		self.treeview.expand_all()
		self.statusbar.push(0, "Loaded CNML succesfully")


	# Recursive
	def __completaArbol_recursive(self, parentzid, parenttree):
		zids = self.cnmlp.zones[parentzid]['subzones']
		
		for zid in zids:
			tree = self.__addZoneToTree(zid, parenttree)
			self.__addNodesFromZoneToTree(zid, tree)
			self.__completaArbol_recursive(zid, tree)
			
		
	def __addZoneToTree(self, zid, parentzone):
		
		# Given a list of node ids, counts how many of them are for each status (working, planned...)
		def countNodes(nodesid):
			nodescount = dict()
			nodescount[Status.UNKNOWN] = 0
			nodescount[Status.PLANNED] = 0
			nodescount[Status.WORKING] = 0
			nodescount[Status.TESTING] = 0
			nodescount[Status.BUILDING] = 0
			
			for nid in nodesid:
				st = self.cnmlp.nodes[nid]['status']
				nodescount[st] += 1
			
			assert nodescount[Status.UNKNOWN] == 0
			return (nodescount[Status.PLANNED], nodescount[Status.WORKING], nodescount[Status.TESTING], nodescount[Status.BUILDING])

		zones = self.cnmlp.zones
		nodeids = zones[zid]['nodes']
		
		col1 = "%s (%d)" %(zones[zid]['title'], len(nodeids))
		(nplanned, nworking, ntesting, nbuilding) = countNodes(nodeids)

		# Add a new row for the zone
		row = (col1, str(nworking), str(nbuilding), str(ntesting), str(nplanned), None)
		tree = self.treestore.append(parentzone, row)
		return tree
		
		
	def __addNodesFromZoneToTree(self, zid, parentzone):
		for nid in self.cnmlp.zones[zid]['nodes']:
			self.treestore.append(parentzone, (None, None, None, None, None, self.cnmlp.nodes[nid]['title']))
		

	def on_showPointsButton_toggled(self, widget, data=None):
		print 'Show points:', widget.get_active()	
		if widget.get_active():
			self.points_layer.show_all_markers()
		else:
			self.points_layer.hide_all_markers()

	
	def on_showLabelsButton_toggled(self, widget, data=None):
		print 'Show labels:', widget.get_active()
		if widget.get_active():
			self.labels_layer.show_all_markers()
		else:
			self.labels_layer.hide_all_markers()
	
	
	def on_showLinksButton_toggled(self, widget, data=None):
		print 'Show links:', widget.get_active()
	
	
	def on_action1_activate(self, action, data=None):
		self.nodedialog.show()
		self.nodedialog.set_title("Information about node XXX")


	def on_action2_activate(self, action, data=None):
		Gtk.show_uri(None, "http://guifi.net/node/", Gtk.get_current_event_time())
		

	def on_action3_activate(self, action, data=None):
		print 'View in map'


	def on_action4_activate(self, action, data=None):
		self.uscdialog.show()
		self.uscdialog.set_title("Unsolclic for device XXX")
		#self.usctextbuffer.set_text(self.usc.test1())
		self.usctextbuffer.set_text(self.usc.generate())

		
	def on_nodeDialog_delete_event(self, widget, data=None):
		self.nodedialog.hide()
		return True

	
	def on_autoloaduscbutton_clicked(self, widget, data=None):
		print 'Autoload configuration'
		raise NotImplementedError
		

	def on_copyuscbutton_clicked(self, widget, data=None):
		print 'copy usc to clipboard'
		cb = Gtk.Clipboard()
		cb.set_text(self.usctextbuffer.get_text(), -1)
		raise NotImplementedError
		

	def on_uscdialog_delete_event(self, widget, data=None):
		self.uscdialog.hide()
		return True
		

	def on_treeview1_button_release_event(self, widget, data=None):
		sel = widget.get_selection()
		(model, it) = sel.get_selected()
		
		col = widget.get_path_at_pos(int(data.x), int(data.y))[1]
		
		if data.button == 3: # Right button
			if col is self.t6 and model.get_value(it, 5) is not None: 
				#user clicked on a node
				self.menu.popup(None, None, None, None, data.button, data.time)
	

	def on_filechooserdialog1_file_activated(self, widget, data=None):
		print 'activated'


	def on_imagemenuitem2_activate(self, widget, data=None):
		self.opendialog.run()


	def on_button3_clicked(self, widget, data=None):
		self.cnmlFile = self.opendialog.get_filename()
		print filename
		self.opendialog.hide()
		self.completaArbol()


	def on_aboutdialog1_close(self, widget, data=None):
		self.about_ui.hide()
		return True


	def on_imagemenuitem10_activate(self, widget, data=None):
		self.about_ui.show()


	def on_changeViewButton_toggled(self, widget, data=None):
		print 'on_changeViewButton_toggled:', self.currentView
		
		if self.currentView == 0:
			self.currentView = 1
		else:
			self.currentView = 0
		self.notebook1.set_current_page(self.currentView)
		
	def gtk_main_quit(self, widget, data=None):
		Gtk.main_quit()
	

if __name__ == "__main__":

	if len(sys.argv) > 1:
		ui = GuifinetStudio(sys.argv[1])
	else:
		ui = GuifinetStudio()

	ui.mainWindow.show()
	Gtk.main()
