# coding=utf-8
"""
@author: Sebastian Badur
"""

from os import path
import gtk
import numpy
from scipy.signal import savgol_filter
from ConfigParser import ConfigParser

from SpeckView.Plotter import Plotter
from SpeckView.Format import Container

from Fit import Fit
from TDMS import TDMS
from FitFunktion import *
from Konfiguration import Konfiguration
from Parameter import Parameter, Fitparameter


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

        self.ui = self.get_object('be_laden')
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
            pixel=int(self.pixel.get_value()),
            dim=self.dim.get_value(),
            mittelungen=int(self.mittelungen.get_value()),
            amp_fitfkt=resonance_lorentz,  # TODO
            ph_fitfkt=[phase_phenom, None][self.combobox('be_methode_phase').get_active()],  # TODO
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
        if par.fkt_ph is not None:
            self.phase = tdms.messwerte_lesen(self.konf.phase)
        self.get_object('be_pixel2').set_upper(self.pixel.get_value() ** 2)

    def fit_starten(self, _):
        par, frequenz = self.fitparameter()

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
        fit = Fit(par, self.amplitude, self.phase, frequenz, self.fortschritt.pulse)
        erg = fit.start()

        # Gwyddion-Datenfeld:
        self.container = Container()
        self.container.volume_data(
            inhalt=[n.amp for n in erg],
            titel="Amplitude (a.u.)",
            dim=par.dim,
            pixel=par.pixel
        )
        self.container.volume_data(
            inhalt=[n.phase for n in erg],
            titel="Phase (°)",
            dim=par.dim,
            pixel=par.pixel
        )
        self.container.volume_data(
            inhalt=[n.resfreq for n in erg],
            titel="Resonanzfrequenz (Hz)",
            dim=par.dim,
            pixel=par.pixel
        )
        self.container.volume_data(
            inhalt=[n.guete for n in erg],
            titel="Guete",
            dim=par.dim,
            pixel=par.pixel
        )
        self.container.volume_data(
            inhalt=[n.untergrund for n in erg],
            titel="Untergrund (a.u.)",
            dim=par.dim,
            pixel=par.pixel
        )

        self.ff.hide_all()
        gtk.main_quit()
