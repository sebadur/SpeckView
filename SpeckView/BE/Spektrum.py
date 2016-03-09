# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
from threading import Thread

from SpeckView.Plotter import Plotter
from SpeckView import Format

from Ergebnis import amp_verlauf
from Konstant import *
from Parameter import frequenzen, frequenzen_voll


class Parallel(Thread):
    def __init__(self, glade, c, komp):
        """
        :type glade: str
        :type c: gwy.Container.Container
        :type komp: SpeckView.BE.Kompendium.Kompendium
        """
        Thread.__init__(self)
        self.glade = glade
        self.c = c
        self.komp = komp

    def run(self):
        Spektrum(self.glade, self.c, self.komp)


class Spektrum(gtk.Builder):
    def __init__(self, glade, c, komp=None):
        """
        :type glade: str
        :type c: gwy.Container.Container
        :type komp: SpeckView.BE.Kompendium.Kompendium
        """
        gtk.Builder.__init__(self)

        if komp is None:
            self.erg = Format.get_custom(c, ERGEBNIS)
            """ :type: list[SpeckView.BE.Ergebnis.Ergebnis] """
            self.par = Format.get_custom(c, PARAMETER)
            """ :type: SpeckView.BE.Parameter.Parameter """
            self.amplitude = Format.get_custom(c, AMPLITUDE)
            """ :type: list """
            self.phase = Format.get_custom(c, PHASE)
            """ :type: list """
        else:
            self.erg = komp.erg
            self.par = komp.par
            self.amplitude = komp.amplitude
            self.phase = komp.phase

        self.add_from_file(glade + 'spektrum.glade')

        self.ui = self.get_object('fenster_spektrum')
        """ :type: gtk.Window """

        self.x = self.spinbox('x')
        self.y = self.spinbox('y')

        self.plotter = Plotter("Frequenz (Hz)", "Amplitude (V)")
        self.get_object('vorschau').add(self.plotter)

        self.connect_signals({
            'ende': gtk.main_quit,
            'aktualisieren': self.aktualisieren
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
