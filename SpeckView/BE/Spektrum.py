# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
from sys import stderr

from SpeckView.Plotter import Plotter
from SpeckView import Format

from Ergebnis import amp_verlauf, phase_verlauf
from Konstant import *
from Parameter import frequenzen, frequenzen_voll
from TDMS import TDMS


class Spektrum(gtk.Builder):
    def __init__(self, glade, c):
        """
        :type glade: str
        :type c: gwy.Container.Container
        """
        gtk.Builder.__init__(self)

        self.add_from_file(glade + 'spektrum.glade')

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

            self.amplitude = []
            self.phase = []
            self.messwerte_lesen()
        except Exception as f:
            stderr.write("Spektroskopiedaten konnten nicht gelesen werden:\n" + f.message)
            return

        self.connect_signals({
            'ende': gtk.main_quit,
            'aktualisieren': self.aktualisieren
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
        self.amplitude = tdms.messwerte_lesen(self.par.konf.amp)
        if self.par.nr_fkt_ph is not None:
            self.phase = tdms.messwerte_lesen(self.par.konf.phase)
        self.x.set_range(1, self.par.pixel)
        self.y.set_range(1, self.par.pixel)

    def n(self):
        return self.x.get_value_as_int() - 1 + (self.y.get_value_as_int() - 1) * self.par.pixel

    def aktualisieren(self, _):
        n = self.n()
        self.plotter.leeren()
        if self.get_object('amplitude').get_active():
            self.plotter.plot(frequenzen_voll(self.par), self.amplitude[n])
            self.plotter.plot(frequenzen(self.par), amp_verlauf(self.par, self.erg[n]))
        else:
            self.plotter.plot(frequenzen_voll(self.par), self.phase[n])
            try:
                self.plotter.plot(frequenzen(self.par), phase_verlauf(self.par, self.erg[n]))
            except ValueError:
                # Geglättete Phase oder kein Fit
                pass
        self.plotter.draw()
