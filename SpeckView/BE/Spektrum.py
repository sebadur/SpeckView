# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
from sys import stderr

from SpeckView.Plotter import Plotter
from SpeckView import Format

from Ergebnis import amp_verlauf
from Konstant import *
from Parameter import frequenzen, frequenzen_voll


class Spektrum(gtk.Builder):
    def __init__(self, glade, c):
        """
        :type glade: str
        :type c: gwy.Container.Container
        """
        gtk.Builder.__init__(self)

        try:
            self.erg = Format.get_custom(c, ERGEBNIS)
            """ :type: list[SpeckView.BE.Ergebnis.Ergebnis] """
            self.par = Format.get_custom(c, PARAMETER)
            """ :type: SpeckView.BE.Parameter.Parameter """
            self.amplitude = Format.get_custom(c, AMPLITUDE)
            """ :type: list """
            self.phase = Format.get_custom(c, PHASE)
            """ :type: list """
        except:
            stderr.write("Es sind keine Spektroskopiedaten vorhanden.")
            # TODO Messdaten ad-hoc einlesen, dafür aber Ergebnisse zwangsweise speichern (längere Ladezeit zur Anzeige der Spektren, aber weniger Speicherverbrauch).
            # TODO Womöglich sogar nur die nötige Zeile einlesen...
            return

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
