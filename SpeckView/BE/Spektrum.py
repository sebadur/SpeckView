# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk

from SpeckView.Plotter import Plotter
from SpeckView import Format

from Ergebnis import amp_verlauf
from Konstant import *
from Parameter import frequenzen, frequenzen_voll


class Spektrum(gtk.Builder):
    def __init__(self, glade, c):
        """
        :type glade: str
        :type c: gwy.Container
        """
        gtk.Builder.__init__(self)

        self.erg = Format.get_custom(c, ERGEBNIS)
        """ :type: list[SpeckView.BE.Ergebnis.Ergebnis] """
        self.par = Format.get_custom(c, PARAMETER)
        """ :type: SpeckView.BE.Parameter.Parameter """
        self.amplitude = Format.get_custom(c, AMPLITUDE)
        """ :type: list """
        self.phase = Format.get_custom(c, PHASE)
        """ :type: list """

        self.add_from_file(glade)

        self.ui = self.get_object('fenster_spektrum')
        """ :type: gtk.Window """

        self.x = self.spinbox('bes_x')
        self.y = self.spinbox('bes_y')

        self.plotter = Plotter("Frequenz (Hz)", "Amplitude (V)")
        self.get_object('bes_vorschau').add(self.plotter)

        self.connect_signals({
            'bes_ende': gtk.main_quit,
            'bes_aktualisieren': self.aktualisieren
        })
        self.ui.show_all()
        gtk.main()

    def spinbox(self, name):
        """
        :type name: str
        :rtype: gtk.SpinButton
        """
        return self.get_object(name)

    def n(self):
        return self.x.get_value_as_int() + self.y.get_value_as_int() * self.par.pixel

    def aktualisieren(self, _):
        n = self.n()
        self.plotter.leeren()
        self.plotter.plot(frequenzen_voll(self.par), self.amplitude[n])
        self.plotter.plot(frequenzen(self.par), amp_verlauf(self.par, self.erg[n]))
        self.plotter.draw()