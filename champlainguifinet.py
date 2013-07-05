#!/usr/bin/env python

from gi.repository import GtkClutter, Clutter
GtkClutter.init([])  # Must be initialized before importing those:
from gi.repository import Gtk
from gi.repository import GtkChamplain, Champlain

import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('lib')
sys.path.append('lib/libcnml')

from libcnml import CNMLParser, Status
from utils import APP_NAME, LOCALE_DIR

import gettext
gettext.bindtextdomain(APP_NAME, LOCALE_DIR)
gettext.textdomain(APP_NAME)
_ = gettext.gettext


class GuifiNodeMarker:
    def __init__(self, nid, lat, lon, status, size=8):
        self.double_click_cb = None
        self.id = nid
        self.point = Champlain.Point.new()
        self.point.set_location(lat, lon)
        self.point.set_size(size)
        color = self.color_from_status(status)
        self.point.set_color(color)
        self.set_double_click_cb(self.point_button_release_cb)  # default callback

    @staticmethod
    def fromCNML(cnmlnode):
        """
        Instantiate GuifiNodeMarker from libcnml node structure
        """
        nid, lat, lon, status = cnmlnode.id, cnmlnode.latitude, cnmlnode.longitude, cnmlnode.status
        marker = GuifiNodeMarker(nid, lat, lon, status)
        return marker

    def get_champlain_point(self):
        return self.point

    def set_double_click_cb(self, func):
        if self.double_click_cb:
            self.point.disconnect_by_func(self.double_click_cb)
        self.point.connect('button-release-event', func)
        self.double_click_cb = func

    def color_from_status(self, status):
        # Planned: blue
        # Working: green
        # Testing: orange
        # Building: black
        # Reserved: red
        # Dropped: gray
        if status == Status.PLANNED:
            color = Clutter.Color.new(0, 0, 255, 255)
        elif status == Status.WORKING:
            color = Clutter.Color.new(44, 188, 15, 255)
        elif status == Status.TESTING:
            color = Clutter.Color.new(255, 174, 69, 255)
        elif status == Status.BUILDING:
            color = Clutter.Color.new(0, 0, 0, 255)
        elif status == Status.RESERVED:
            color = Clutter.Color.new(255, 0, 0, 255)
        elif status == Status.DROPPED:
            color = Clutter.Color.new(100, 100, 100, 255)
        else:
            raise ValueError

        return color

    # TODO: This shouldn't be in the view but in the controller
    def point_button_release_cb(self, widget, event):
        """
        Default double-click handler
        """
        if event.button == 1 and event.click_count > 1:
            print 'Marcador pulsado'
            from ui import NodeDialog
            NodeDialog()
        return True


# It's compound of two ChamplainMarkerLayer layers
class GtkGuifinetMap(GtkChamplain.Embed):
    def __init__(self, parent):
        GtkChamplain.Embed.__init__(self)
        self.set_size_request(640, 480)

        self.parent = parent
        self.view = self.get_view()
        self.view.set_reactive(True)
        self.view.set_kinetic_mode(True)
        self.view.set_zoom_level(13)
        self.view.center_on(36.72341, -4.42428)  # TODO: Set to center of default zone
        self.view.connect('button-release-event', self.mouse_click_cb)

        scale = Champlain.Scale()
        scale.connect_view(self.view)
        self.view.bin_layout_add(scale, Clutter.BinAlignment.START, Clutter.BinAlignment.END)

        self.points = {}
        self.points_layer = Champlain.MarkerLayer()
        self.points_layer.set_selection_mode(Champlain.SelectionMode.SINGLE)
        self.labels_layer = Champlain.MarkerLayer()

        # It's important to add points the last. Points are selectable while labels are not
        # If labels is added later, then you click on some point and it doesn't get selected
        # because you are really clicking on the label. Looks like an usability bug?
        self.view.add_layer(self.labels_layer)
        self.view.add_layer(self.points_layer)

        self.menu = Gtk.Menu()
        menuitem1 = Gtk.MenuItem(_('Create new Guifi.net node here'))
        menuitem1.connect('activate', self.create_new_node_cb)
        self.menu.append(menuitem1)
        self.menu.show_all()

    def get_point_from_nid(self, nid):
        """
        Return Champlain.Point instance of node with id "nid"
        """
        return self.points[nid]

    def create_new_node_cb(self, action, data=None):
        self.parent.create_new_node((self.lat, self.lon))
        del self.lat, self.lon

    def add_node_point(self, cnmlnode, size=8):
        p = GuifiNodeMarker.fromCNML(cnmlnode)
        self.points_layer.add_marker(p.get_champlain_point())
        self.points[cnmlnode.id] = p

    def add_node_label(self, cnmlnode):
        nid, lat, lon, text, status = cnmlnode.id, cnmlnode.latitude, cnmlnode.longitude, cnmlnode.title, cnmlnode.status

        p = Champlain.Label.new()
        p.set_text(text)
        color = Clutter.Color.new(0, 0, 0, 255)
        p.set_text_color(color)
        p.set_location(lat, lon)
        p.set_draw_background(False)
        self.labels_layer.add_marker(p)

    def start_traceroute_path(self):
        self.tr_points_layer = Champlain.MarkerLayer()
        self.tr_path_layer = Champlain.PathLayer()
        self.view.add_layer(self.tr_points_layer)
        self.view.add_layer(self.tr_path_layer)

    def add_traceroute_path(self, lat, lon):
        p = Champlain.Point.new()
        p.set_location(lat, lon)
        p.set_size(12)
        color = Clutter.Color.new(0, 0, 255, 255)
        p.set_color(color)
        self.tr_points_layer.add_marker(p)
        self.tr_path_layer.add_node(p)

    def end_traceroute_path(self):
        self.view.remove_layer(self.tr_points_layer)
        self.view.remove_layer(self.tr_path_layer)
        try:
            del self.tr_points_layer, self.tr_path_layer
        except:
            pass

    # nodes = self.cnmlp.getNodes()
    def paintMap(self, nodes):
        for n in nodes:
            self.add_node_point(n.latitude, n.longitude, n.status)
            self.add_node_label(n.latitude, n.longitude, n.title, n.status)

    def reset(self):
        self.points_layer.remove_all()
        self.labels_layer.remove_all()

    def zoom_in(self):
        self.view.zoom_in()

    def zoom_out(self):
        self.view.zoom_out()

    def show_points(self, active):
        if active:
            self.points_layer.show_all_markers()
        else:
            self.points_layer.hide_all_markers()

    def show_labels(self, active):
        if active:
            self.labels_layer.show_all_markers()
        else:
            self.labels_layer.hide_all_markers()

    # TODO: This shouldn't be in the view but in the controller
    def mouse_click_cb(self, widget, event):
        # event == void (GdkEventButton?)
        if event.button == 3:  # Right button
            X, Y = event.x, event.y
            self.lon, self.lat = self.view.x_to_longitude(X), self.view.y_to_latitude(Y)
            self.menu.popup(None, None, None, None, event.button, event.time)

    def getView(self):
        return self.view


if __name__ == '__main__':
    w = Gtk.Window()
    map = GtkGuifinetMap()
    w.add(map)
    w.show_all()
    w.connect('destroy', Gtk.main_quit)

    Gtk.main()
