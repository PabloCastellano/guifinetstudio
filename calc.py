#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# calc.py - Guifi.net Calculator
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


from gi.repository import Gtk
import math


class Calculator:

    # Used to calculate attenuation
    K1 = [0.70501, 0.32062, 0.24271, 0.12013, 0.07563, 0.05190]
    K2 = [0.00183, 0.00034, 0.00032, 0.00031, 0.00026, 0.00015]

    def __init__(self):
        self.ui = Gtk.Builder()
        self.ui.add_from_file('ui/calc.ui')
        self.ui.connect_signals(self)

        self.calcdialog = self.ui.get_object('calcdialog')

        self.notebook = self.ui.get_object('notebook')
        self.notebook.set_show_tabs(False)

        self.convertertoolbutton = self.ui.get_object('convertertoolbutton')
        self.attenuationtoolbutton = self.ui.get_object('attenuationtoolbutton')
        self.powertoolbutton = self.ui.get_object('powertoolbutton')

        # Unit converter tab
        self.mwlabel1 = self.ui.get_object('mwlabel1')
        self.mwlabel2 = self.ui.get_object('mwlabel2')
        self.dbmlabel1 = self.ui.get_object('dbmlabel1')
        self.dbmlabel2 = self.ui.get_object('dbmlabel2')
        self.dbmmwentry = self.ui.get_object('dbmmwentry')
        self.dbmmwentry.set_text('100')

        # Attenuation tab
        self.dblosslabel = self.ui.get_object('dblosslabel')
        self.lengthentry = self.ui.get_object('lengthentry')
        self.freqentry = self.ui.get_object('freqentry')
        self.coaxialcombobox = self.ui.get_object('coaxialcombobox')
        self.lengthentry.set_text('300')
        self.freqentry.set_text('2445')
        self.calculate_loss()

        # Power emission tab
        self.radiopowerentry = self.ui.get_object('radiopowerentry')
        self.coaxialcombobox2 = self.ui.get_object('coaxialcombobox2')
        self.lengthentry2 = self.ui.get_object('lengthentry2')
        self.freqentry2 = self.ui.get_object('freqentry2')
        self.lossesentry = self.ui.get_object('lossesentry')
        self.gainentry = self.ui.get_object('gainentry')
        self.powerlabel = self.ui.get_object('powerlabel')
        self.eirplabel = self.ui.get_object('eirplabel')
        self.radiopowerentry.set_text('65')
        self.lengthentry2.set_text('300')
        self.freqentry2.set_text('2445')
        self.lossesentry.set_text('0')
        self.gainentry.set_text('3')
        self.calculate_emission()

        self.calcdialog.show_all()

    def on_convertertoolbutton_clicked(self, widget, data=None):
        self.notebook.set_current_page(0)

    def on_attenuationtoolbutton_clicked(self, widget, data=None):
        self.notebook.set_current_page(1)

    def on_powertoolbutton_clicked(self, widget, data=None):
        self.notebook.set_current_page(2)

    def on_dbmmwentry_changed(self, widget, data=None):
        def mw2dbm(mw):
            dbm = pow(10, mw / 10)
            return dbm

        def dbm2mw(dbm):
            mw = 10 * math.log10(dbm)
            return mw

        text = widget.get_text()

        try:
            val = float(text)
            mw = str(dbm2mw(val))
            dbm = str(mw2dbm(val))
            self.mwlabel1.set_text(text + ' mW')
            self.mwlabel2.set_text(mw + ' mW')
            self.dbmlabel1.set_text(text + ' dBm')
            self.dbmlabel2.set_text(dbm + ' dBm')
        except:
            # ValueError, OverflowError
            self.mwlabel1.set_text(text + ' mW')
            self.mwlabel2.set_text('NaN')
            self.dbmlabel1.set_text(text + ' dBm')
            self.dbmlabel2.set_text('NaN')

    def dBcalc(self, freqentry, lengthentry, n):
        freq = float(freqentry.get_text())
        length = float(lengthentry.get_text()) / 100.0
        mldb = (self.K1[n] * math.sqrt(freq) + self.K2[n] * freq) / 100.0 * length / 0.3048
        alpha = math.pow(10, mldb / 10.0)
        calcdb = 10 * math.log10(math.pow(alpha, 2) / alpha)
        return calcdb

    def calculate_loss(self, widget=None, data=None):
        it = self.coaxialcombobox.get_active_iter()
        n = self.coaxialcombobox.get_model().get_value(it, 0)

        try:
            calcdb = self.dBcalc(self.freqentry, self.lengthentry, n)
            loss = round(round(calcdb * 1000.0, 3) / 1000.0, 3)
            self.dblosslabel.set_text(str(loss) + ' dB')
        except:
            self.dblosslabel.set_text('NaN')

    def calculate_emission(self, widget=None, data=None):
        it = self.coaxialcombobox2.get_active_iter()
        n = self.coaxialcombobox2.get_model().get_value(it, 0)

        try:
            radiopower = float(self.radiopowerentry.get_text())
            otherloss = float(self.lossesentry.get_text())
            gain = float(self.gainentry.get_text())
            calcdb = self.dBcalc(self.freqentry2, self.lengthentry2, n)
            totaldb = calcdb + otherloss

            emittedpower = (radiopower / 1000) * math.pow(10, -totaldb / 10)
            emittedpower = int(emittedpower * 1000)
            emittedpower = round(emittedpower * 1000) / 1000

            eirp = 10 * math.log10(radiopower) + gain - totaldb
            eirp = math.pow(10, eirp / 10) / 1000.0
            eirp = round(eirp * 100) / 100.0

            self.powerlabel.set_text(str(emittedpower) + ' mW')
            self.eirplabel.set_text(str(eirp) + ' W')
        except:
            self.eirplabel.set_text('NaN')
            self.powerlabel.set_text('NaN')

    def on_calcdialog_response(self, widget, data=None):
        self.calcdialog.destroy()

if __name__ == '__main__':
    w = Calculator()
    w.calcdialog.connect('destroy', Gtk.main_quit)
    Gtk.main()
