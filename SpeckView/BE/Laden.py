# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
import numpy
from scipy.signal import savgol_filter
from ctypes import c_float

from SpeckView.Plotter import Plotter

import BERaster
from Fit import Fit
from TDMS import TDMS
from FitFunktion import *
from Konfiguration import Konfiguration
from Parameter import Parameter, Fitparameter


class Laden(gtk.Builder):
    def __init__(self, glade, pfad, parser, datenfeld):
        """
        :type glade: str
        :type pfad: str
        :type parser: ConfigParser.ConfigParser
        """
        gtk.Builder.__init__(self)
        self.datenfeld = datenfeld

        self.pfad = pfad
        self.add_from_file(glade)
        self.connect_signals({
            'be_ende': gtk.main_quit,
            'be_fit_starten': self.fit_starten,
            'abbrechen': lambda *args: Fit.stopp()
        })

        self.ff = self.get_object('fenster_fortschritt')
        """ :type: gtk.Window """
        self.fortschritt = self.get_object('fortschritt')
        """ :type: gtk.ProgressBar """

        self.ui = self.get_object('be_laden')
        """ :type: gtk.Window """

        konf = Konfiguration()
        self.konf = konf
        self.pixel = parser.getint(konf.konfig, konf.pixel)

        self.df = self.spinbox('be_df')
        self.df.set_value(parser.getfloat(konf.konfig, konf.df))
        self.mittelungen = self.spinbox('be_mittelungen')
        self.mittelungen.set_value(parser.getint(konf.konfig, konf.mittelungen))
        self.fmin = self.spinbox('be_fmin')
        self.fmin.set_value(parser.getint(konf.konfig, konf.fmin))
        self.fmax = self.spinbox('be_fmax')
        self.fmax.set_value(parser.getint(konf.konfig, konf.fmax))

        plotter = Plotter("x", "y")
        plotter.plot(range(100), range(100))
        self.get_object('plotbox').add(plotter)
        self.ui.show_all()
        gtk.main()

    def spinbox(self, name):
        """
        :type name: str
        :rtype: gtk.SpinButton
        """
        return self.get_object(name)

    def fit_starten(self, knopf):
        fmin = self.fmin.get_value()
        fmax = self.fmax.get_value()
        df = self.df.get_value()
        frequenz = numpy.arange(fmin, fmax, df)

        bereich_links = 0
        bereich_rechts = 0

        # self.spinbox('be_savgol_koeff').get_value()
        # self.spinbox('be_savgol_ordnung').get_value()
        par = Parameter(
            fmin=fmin,
            fmax=fmax,
            df=df,
            pixel=self.pixel,
            mittelungen=int(self.mittelungen.get_value()),
            amp_fitfkt=resonance_lorentz,  # TODO
            ph_fitfkt=phase_phenom,  # TODO
            filter_fkt=lambda verlauf: savgol_filter(verlauf, 15, 3),  # TODO
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

        # Fortschrittsanzeige:
        self.ui.hide_all()
        self.ff.show_all()
        self.fortschritt.set_value(0)
        self.fortschritt.set_pulse_step(1 / self.pixel)
        while gtk.events_pending():
            gtk.main_iteration_do(True)

        # Messwerte einlesen:
        tdms = TDMS(par)
        amplitude = tdms.messwerte_lesen(self.konf.amp)
        phase = tdms.messwerte_lesen(self.konf.phase)
        if phase is None:
            phase = amplitude  # TODO: Wenn keine Phase vorhanden ist

        # Gwyddion-Datenfeld:
        c_feld = c_float * self.pixel ** 2
        daten = c_feld.from_address(self.datenfeld.get_data_pointer())

        # Fitten:
        fit = Fit(par, amplitude, phase, frequenz, self.fortschritt.pulse)
        daten[:] = fit.start()

        if BERaster.DEBUG:
            from matplotlib import pyplot
            pyplot.matshow(numpy.array(daten[:]).reshape((self.pixel, self.pixel)))
            pyplot.show()

        """for x in range(self.pixel):
            for y in range(self.pixel):
                self.datenfeld.set_val(x, y, erg_amp[x + y * self.pixel])"""

        self.ff.hide_all()
        gtk.main_quit()
