# coding=utf-8
"""
@author: Sebastian Badur
"""

from os import path
import gtk
import numpy
# noinspection PyUnresolvedReferences
from gwy import Container
from ConfigParser import ConfigParser

from SpeckView.Plotter import Plotter
from SpeckView import Format

from Ergebnis import amp_verlauf
from Fit import Fit
from TDMS import TDMS
from Konfiguration import Konfiguration
from Konstant import *
from Parameter import *


class Laden(gtk.Builder):
    def __init__(self, glade, konfig_datei):
        """
        :type glade: str
        :type konfig_datei: str
        """
        gtk.Builder.__init__(self)

        self.container = None
        """ :type: Container """

        self.amplitude = None
        """ :type: numpy.multiarray.ndarray """
        self.phase = None
        """ :type: numpy.multiarray.ndarray """

        self.pfad = path.dirname(konfig_datei)
        self.add_from_file(glade)
        self.connect_signals({
            'be_ende': gtk.main_quit,
            'be_fit_starten': self.fit_starten,
            'abbrechen': lambda *args: Fit.stopp(),
            'vorschau': self.vorschau
        })

        self.ff = self.get_object('fenster_fortschritt')
        """ :type: gtk.Window """
        self.fortschritt = self.get_object('fortschritt')
        """ :type: gtk.ProgressBar """

        self.ui = self.get_object('fenster_laden')
        """ :type: gtk.Window """

        parser = ConfigParser()
        parser.read(konfig_datei)

        konf = Konfiguration()
        self.konf = konf
        self.pixel = self.spinbox('be_pixel')
        self.pixel.set_value(parser.getint(konf.konfig, konf.pixel))
        self.dim = self.spinbox('be_dim')
        self.dim.set_value(parser.getfloat(konf.konfig, konf.dim))

        self.df = self.spinbox('be_df')
        self.df.set_value(parser.getfloat(konf.konfig, konf.df))
        self.mittelungen = self.spinbox('be_mittelungen')
        self.mittelungen.set_value(parser.getint(konf.konfig, konf.mittelungen))
        self.fmin = self.spinbox('be_fmin')
        self.fmin.set_value(parser.getint(konf.konfig, konf.fmin))
        self.fmax = self.spinbox('be_fmax')
        self.fmax.set_value(parser.getint(konf.konfig, konf.fmax))

        self.plotter = Plotter("Frequenz (Hz)", "Amplitude (V)")
        self.get_object('be_vorschau').add(self.plotter)
        self.ui.show_all()
        gtk.main()

    def spinbox(self, name):
        """
        :type name: str
        :rtype: gtk.SpinButton
        """
        return self.get_object(name)

    def combobox(self, name):
        """
        :type name: str
        :rtype: gtk.ComboBox
        """
        return self.get_object(name)

    def vorschau(self, box):
        """
        :type box: gtk.SpinButton
        """
        n = box.get_value()
        par = self.fitparameter()
        frequenz = frequenzen(par)
        if self.amplitude is None:
            self.messwerte_lesen(par)
        fit = Fit(par, self.amplitude, self.phase, self.fortschritt.pulse)
        erg = fit.vorschau(n)
        self.plotter.leeren()
        self.plotter.plot(frequenzen_voll(par), self.amplitude[n])
        self.plotter.plot(frequenz, amp_verlauf(par, erg))
        self.plotter.draw()

    def fitparameter(self):
        """
        :rtype: Parameter
        """
        fmin = self.fmin.get_value()
        fmax = self.fmax.get_value()
        df = self.df.get_value()

        bereich_links = 0
        bereich_rechts = 0

        # self.spinbox('be_savgol_koeff').get_value()
        # self.spinbox('be_savgol_ordnung').get_value()
        return Parameter(
            fmin=fmin,
            fmax=fmax,
            df=df,
            pixel=self.pixel.get_value_as_int(),
            dim=self.dim.get_value(),
            mittelungen=self.mittelungen.get_value_as_int(),
            amp_fitfkt=0,  # TODO
            ph_fitfkt=self.combobox('be_methode_phase').get_active(),
            filter_breite=self.spinbox('be_savgol_koeff').get_value_as_int(),
            filter_ordnung=self.spinbox('be_savgol_ordnung').get_value_as_int(),
            phase_versatz=50,  # TODO und eigene Fitparameter für Phase!
            bereich_links=bereich_links,
            bereich_rechts=bereich_rechts,
            amp=Fitparameter(
                guete_min=self.spinbox('be_q_min').get_value(),
                guete_max=self.spinbox('be_q_max').get_value(),
                off_min=self.spinbox('be_off_min').get_value(),
                off_max=self.spinbox('be_off_max').get_value()
            ),
            amp_min=self.spinbox('be_amp_min').get_value(),
            amp_max=self.spinbox('be_amp_max').get_value(),
            phase=Fitparameter(
                guete_min=self.spinbox('be_phase_q_min').get_value(),
                guete_max=self.spinbox('be_phase_q_max').get_value(),
                off_min=self.spinbox('be_phase_off_min').get_value(),
                off_max=self.spinbox('be_phase_off_max').get_value()
            ),
            konf=self.konf,
            pfad=self.pfad
        )

    def messwerte_lesen(self, par):
        """
        :type par: Parameter
        :rtype: (numpy.multiarray.ndarray, numpy.multiarray.ndarray)
        """
        tdms = TDMS(par)
        self.amplitude = tdms.messwerte_lesen(self.konf.amp)
        if par.nr_fkt_ph is not None:
            self.phase = tdms.messwerte_lesen(self.konf.phase)
        self.get_object('be_pixel2').set_upper(self.pixel.get_value() ** 2)

    def fit_starten(self, _):
        par = self.fitparameter()

        # Fortschrittsanzeige:
        self.ui.hide_all()
        self.ff.show_all()
        self.fortschritt.set_value(0)
        self.fortschritt.set_pulse_step(1 / par.pixel)
        while gtk.events_pending():
            gtk.main_iteration_do(True)

        # Messwerte einlesen:
        self.messwerte_lesen(par)

        # Fitten:
        fit = Fit(par, self.amplitude, self.phase, self.fortschritt.pulse)
        erg = fit.start()

        # Gwyddion-Datenfeld:
        self.container = Container()
        xy = Format.si_unit("m")

        def anlegen(inhalt, titel, einheit):
            Format.volume_data(
                c=self.container,
                inhalt=inhalt,
                einheit_xy=xy,
                einheit_z=Format.si_unit(einheit),
                titel=titel,
                dim=par.dim,
                pixel=par.pixel
            )

        anlegen([n.amp for n in erg], "Amplitude (a.u.)", "a.u.")
        anlegen([n.phase for n in erg], "Phase (°)", "°")
        anlegen([n.resfreq for n in erg], "Resonanzfrequenz (Hz)", "Hz")
        anlegen([n.guete for n in erg], u"Güte", "")
        anlegen([n.untergrund for n in erg], "Untergrund (a.u.)", "a.u.")

        Format.set_custom(self.container, ERGEBNIS, erg)
        Format.set_custom(self.container, PARAMETER, par)
        Format.set_custom(self.container, AMPLITUDE, self.amplitude)
        Format.set_custom(self.container, PHASE, self.phase)

        self.ff.hide_all()
        gtk.main_quit()
