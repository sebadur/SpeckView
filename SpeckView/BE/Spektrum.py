# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
from sys import stderr
import numpy as np
import gwy
from matplotlib.widgets import Cursor
from copy import copy

from SpeckView.Plotter import Plotter
from SpeckView import Format
from SpeckView.Dialog import Dialog

from Ergebnis import amp_verlauf, phase_verlauf
from Konstant import *
from Parameter import frequenzen, frequenzen_voll
from TDMS import TDMS
from Fit import Fit


class Spektrum(gtk.Builder):
    def __init__(self, sv, c):
        """
        :type sv: str
        :type c: gwy.Container.Container
        """
        gtk.Builder.__init__(self)

        self.sv = sv
        self.c = c

        self.add_from_file(sv + 'BE/spektrum.glade')

        self.ui = self.get_object('fenster_spektrum')
        """ :type: gtk.Window """

        self.x = self.spinbutton('x')
        self.y = self.spinbutton('y')

        self.plotter = Plotter("Frequenz (Hz)", "Amplitude (V)")
        self.get_object('vorschau').add(self.plotter)

        try:
            self.erg = Format.get_custom(c, ERGEBNIS)
            """ :type: list[SpeckView.BE.Ergebnis.Ergebnis] """
            self.par = Format.get_custom(c, PARAMETER)
            """ :type: SpeckView.BE.Parameter.Parameter """

            self.amplitude = np.array([])
            self.phase = np.array([])
            self.messwerte_lesen()
        except Exception as f:
            stderr.write("Spektroskopiedaten konnten nicht gelesen werden:\n" + f.message)
            return

        self.connect_signals({
            'ende': gtk.main_quit,
            'aktualisieren': self.aktualisieren,
            'fitten': self.fitten,
            'maskieren': self.maskieren,
            'speichern': self.speichern
        })
        self.ui.show_all()
        gtk.main()

    def spinbutton(self, name):
        """
        :type name: str
        :rtype: gtk.SpinButton
        """
        return self.get_object(name)

    def messwerte_lesen(self):
        """
        :rtype: (numpy.multiarray.ndarray, numpy.multiarray.ndarray)
        """
        tdms = TDMS(self.par, self.par.konf)
        self.amplitude = tdms.messwerte_lesen(self.par.kanal, 'amp')
        self.phase = tdms.messwerte_lesen(self.par.kanal, 'phase')
        self.x.set_range(1, self.par.pixel)
        self.y.set_range(1, self.par.pixel)

    def nx(self):
        return self.x.get_value_as_int() - 1

    def ny(self):
        return self.y.get_value_as_int() - 1

    def n(self):
        return self.nx() + self.ny() * self.par.pixel

    def aktualisieren(self, _):
        n = self.n()
        self.plotter.leeren()
        fit = Fit(self.par, self.amplitude, self.phase, lambda(i): None)
        freq = frequenzen(self.par)
        if self.get_object('amplitude').get_active():
            self.plotter.plot(freq, fit.amplitude(n))
            self.untergrund = fit.amplitude(n)[0]
            self.plotter.plot(freq, amp_verlauf(self.par, self.erg[n]))
        else:
            self.plotter.plot(freq, fit.phase(n))
            try:
                self.plotter.plot(freq, phase_verlauf(self.par, self.erg[n]))
            except ValueError:
                # Geglättete Phase oder kein Fit
                pass
        self.plotter.draw()

    def fitten(self, _):
        self.plotter.cursor = Cursor(self.plotter.axes, color='red', linewidth=2)
        def klick(e):
            self.plotter.cursor = None
            self.plotter.canvas.mpl_disconnect(self.cid)
            # Mit manuellen Parametern fitten:
            par_orig = copy(self.par)
            fit = Fit(self.par, self.amplitude, self.phase, lambda(i): None)
            self.par.fmin = 0.98 * e.xdata
            self.par.fmax = 1.02 * e.xdata
            self.par.amp_min = 0.95 * (e.ydata - self.untergrund)  # Amplitude, ohne Untergrund
            self.par.amp_max = 1.05 * (e.ydata - self.untergrund)
            x = self.nx()
            y = self.ny()
            n = self.n()
            neu = fit.vorschau(n)
            # Ergebnis übernehmen:
            self.erg[n] = neu
            c = gwy.gwy_app_data_browser_get_current(gwy.APP_CONTAINER)
            sq = c.get_double_by_name('/0/sq')
            c.get_object_by_name('/0/data').set_val(x, y, sq * neu.amp / neu.guete_amp)  # TODO unschön und hängt von Speicherreihenfolge ab
            c.get_object_by_name('/1/data').set_val(x, y, neu.amp)
            c.get_object_by_name('/2/data').set_val(x, y, neu.phase)
            c.get_object_by_name('/3/data').set_val(x, y, neu.resfreq)
            c.get_object_by_name('/4/data').set_val(x, y, neu.guete_amp)
            c.get_object_by_name('/5/data').set_val(x, y, neu.amp_fhlr)
            c.get_object_by_name('/6/data').set_val(x, y, neu.phase_fhlr)
            c.get_object_by_name('/7/data').set_val(x, y, neu.resfreq_fhlr)
            c.get_object_by_name('/8/data').set_val(x, y, neu.guete_amp_fhlr)
            c.get_object_by_name('/9/data').set_val(x, y, neu.guete_ph)
            c.get_object_by_name('/10/data').set_val(x, y, neu.untergrund)
            c.get_object_by_name('/11/data').set_val(x, y, neu.phase_rel)
            # Für restliche Daten alte Parameter wiederherstellen:
            self.par = par_orig
            self.aktualisieren(_)
        self.cid = self.plotter.canvas.mpl_connect('button_press_event', klick)
        self.plotter.draw()

    def maskieren(self, _):
        n = self.n()
        df = gwy.gwy_app_data_browser_get_current(gwy.APP_DATA_FIELD)
        """
        :type: gwy.DataField
        """
        x = self.nx()
        y = self.ny()
        df.set_val(x, y, 0.0)
        self.erg[n].amp = 0.0
        m = gwy.gwy_app_data_browser_get_current(gwy.APP_MASK_FIELD)
        if m is None:
            m = gwy.DataField(df.get_xres(), df.get_yres(), df.get_xreal(), df.get_yreal(), True)
            c = gwy.gwy_app_data_browser_get_current(gwy.APP_CONTAINER)
            id = gwy.gwy_app_data_browser_get_current(gwy.APP_DATA_FIELD_ID)
            c.set_object_by_name('/'+str(id)+'/mask', m)
        m.set_val(x, y, 1.0)
        self.aktualisieren(_)

    def speichern(self, _):
        n = self.n()
        fit = Fit(self.par, self.amplitude, self.phase, lambda(i): None)
        freq = frequenzen(self.par)
        if self.get_object('amplitude').get_active():
            dat = gwy.gwy_file_get_filename_sys(self.c).rsplit('.', 1)[0] + '-'
            np.array((freq, fit.amplitude(n))).T.tofile(dat + "dat.dat")
            np.array((freq, amp_verlauf(self.par, self.erg[n]))).T.tofile(dat + "fit.dat")
            Dialog(self.sv).info("Korrelation gespeichert", "In Datei gespeichert:\n" + dat + "...")
