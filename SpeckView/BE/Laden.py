# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
import numpy
from scipy.signal import savgol_filter

from SpeckView.Plotter import Plotter
from SpeckView.BE.Fit import Fit
from SpeckView.BE.FitFunktion import *
from SpeckView.BE.Konfiguration import Konfiguration
from SpeckView.BE.Parameter import Parameter, Fitparameter
from SpeckView.BE.TDMS import TDMS


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
            'be_fit_starten': self.fit_starten
        })

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
        bereich_rechts = -1

        par = Parameter(
            fmin=fmin,
            fmax=fmax,
            df=df,
            pixel=self.pixel,
            mittelungen=int(self.mittelungen.get_value()),
            amp_fitfkt=resonance_lorentz,  # TODO
            ph_fitfkt=phase_phenom,  # TODO
            filter_fkt=lambda verlauf: savgol_filter(  # TODO
                verlauf,
                self.spinbox('be_savgol_koeff').get_value(),
                self.spinbox('be_savgol_ordnung').get_value()
            ),
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

        tdms = TDMS(par)
        amplitude = tdms.messwerte_lesen(self.konf.amp)
        phase = tdms.messwerte_lesen(self.konf.phase)

        fitter = Fit(par)
        amp, ph = fitter.fit(amplitude, phase, frequenz)

        for x in range(self.pixel):
            for y in range(self.pixel):
                self.datenfeld.set_val(x, y, amp[x + y * self.pixel])

        self.ui.destroy()
        gtk.main_quit()
