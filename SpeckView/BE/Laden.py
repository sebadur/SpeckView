# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
import numpy
from scipy.signal import savgol_filter
from ctypes import c_double

from SpeckView.Plotter import Plotter

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

        self.amplitude = None
        """ :type: numpy.multiarray.ndarray """
        self.phase = None
        """ :type: numpy.multiarray.ndarray """

        self.pfad = pfad
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

        self.ui = self.get_object('be_laden')
        """ :type: gtk.Window """

        konf = Konfiguration()
        self.konf = konf
        self.pixel = parser.getint(konf.konfig, konf.pixel)
        self.spinbox('be_pixel').set_value(self.pixel)

        self.df = self.spinbox('be_df')
        self.df.set_value(parser.getfloat(konf.konfig, konf.df))
        self.mittelungen = self.spinbox('be_mittelungen')
        self.mittelungen.set_value(parser.getint(konf.konfig, konf.mittelungen))
        self.fmin = self.spinbox('be_fmin')
        self.fmin.set_value(parser.getint(konf.konfig, konf.fmin))
        self.fmax = self.spinbox('be_fmax')
        self.fmax.set_value(parser.getint(konf.konfig, konf.fmax))

        self.get_object('be_pixel2').set_upper(self.pixel ** 2)
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

    def vorschau(self, box):
        """
        :type box: gtk.SpinButton
        """
        n = box.get_value()
        par, frequenz = self.fitparameter()
        if self.amplitude is None:
            self.messwerte_lesen(par)
        fit = Fit(par, self.amplitude, self.phase, frequenz, self.fortschritt.pulse)
        erg = fit.vorschau(n)
        self.plotter.leeren()
        self.plotter.plot(frequenz, self.amplitude[n])
        self.plotter.plot(erg.frequenzen, erg.amp_verlauf())
        self.plotter.draw()

    def fitparameter(self):
        """
        :rtype: (Parameter, numpy.multiarray.ndarray)
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
        ), numpy.arange(fmin, fmax, df)

    def messwerte_lesen(self, par):
        """
        :type par: Parameter
        :rtype: (numpy.multiarray.ndarray, numpy.multiarray.ndarray)
        """
        tdms = TDMS(par)
        self.amplitude = tdms.messwerte_lesen(self.konf.amp)
        self.phase = tdms.messwerte_lesen(self.konf.phase)
        if self.phase is None:
            self.phase = self.amplitude  # TODO: Wenn keine Phase vorhanden ist

    def fit_starten(self, _):
        par, frequenz = self.fitparameter()

        # Fortschrittsanzeige:
        self.ui.hide_all()
        self.ff.show_all()
        self.fortschritt.set_value(0)
        self.fortschritt.set_pulse_step(1 / self.pixel)
        while gtk.events_pending():
            gtk.main_iteration_do(True)

        # Messwerte einlesen:
        self.messwerte_lesen(par)

        # Gwyddion-Datenfeld:
        c_feld = c_double * self.pixel ** 2
        daten = c_feld.from_address(self.datenfeld.get_data_pointer())

        # Fitten:
        fit = Fit(par, self.amplitude, self.phase, frequenz, self.fortschritt.pulse)
        erg = fit.start()

        # Ermittelte Amplitude:
        daten[:] = [n.amp for n in erg]

        self.ff.hide_all()
        gtk.main_quit()
