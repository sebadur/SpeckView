# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
import numpy
from gwy import Container
from os.path import sep

from SpeckView import Format
from SpeckView.Plotter import Plotter
from SpeckView.Parser import DefaultParser

from Ergebnis import amp_verlauf, phase_verlauf
from Fit import Fit
from Konstant import *
from Parameter import *
from TDMS import TDMS


class Laden(gtk.Builder):
    def __init__(self, konf, svbe):
        """
        :type konf: Konfiguration.Konfiguration
        """
        gtk.Builder.__init__(self)

        self.container = None
        """ :type: Container """

        self.amplitude = None
        """ :type: numpy.multiarray.ndarray """
        self.phase = None
        """ :type: numpy.multiarray.ndarray """

        self.add_from_file(svbe + sep + 'laden.glade')

        self.ui = self.window('fenster_laden')
        self.ff = self.window('fenster_fortschritt')

        self.connect_signals({
            'ende': gtk.main_quit,
            'fit_starten': self.fit_starten,
            'abbrechen': lambda _: Fit.stopp(),
            'vorschau': self.vorschau
        })

        self.fortschritt = self.get_object('fortschritt')
        """ :type: gtk.ProgressBar """

        parser = DefaultParser()
        parser.read(konf.datei)

        self.konf = konf
        self.version = parser.getint(konf.konfig, konf.version)

        self.pixel = self.spinbutton('pixel')
        self.pixel.set_value(parser.getint(konf.konfig, konf.pixel))
        self.dim = self.spinbutton('dim')
        self.dim.set_value(parser.getfloat(konf.konfig, konf.dim))

        self.df = self.spinbutton('df')
        self.df.set_value(parser.getfloat(konf.konfig, konf.df))
        self.mittelungen = self.spinbutton('mittelungen')
        self.mittelungen.set_value(parser.getint(konf.konfig, konf.mittelungen))
        self.fmin = self.spinbutton('fmin')
        self.bereich_min = self.spinbutton('bereich_min')
        fmin = parser.getint(konf.konfig, konf.fmin)
        self.fmin.set_value(fmin)
        self.bereich_min.set_value(fmin)
        self.fmax = self.spinbutton('fmax')
        self.bereich_max = self.spinbutton('bereich_max')
        fmax = parser.getint(konf.konfig, konf.fmax)
        self.fmax.set_value(fmax)
        self.bereich_max.set_value(fmax)

        self.plotter = Plotter("Frequenz (Hz)", "Amplitude (V)")
        self.get_object('vorschau').add(self.plotter)
        self.ui.show_all()
        gtk.main()

    def vorschau(self, _):
        n = self.spinbutton('vorschau_pixel2').get_value()
        par = self.fitparameter()
        frequenz = frequenzen(par)
        if self.amplitude is None:
            self.messwerte_lesen(par)
        erg = Fit(par, self.amplitude, self.phase, self.fortschritt.pulse).vorschau(n)

        def plot(messung, fit):
            """
            :param messung: list
            :param fit: list
            """
            self.plotter.leeren()
            self.plotter.plot(frequenzen_voll(par), messung)
            if fit is not None:
                self.plotter.plot(frequenz, fit, linewidth=2)
            self.plotter.draw()

        if self.radiobutton('vorschau_amp').get_active():
            plot(self.amplitude[n], amp_verlauf(par, erg))
        else:  # if self.radiobutton('vorschau_phase').get_active():
            plot(self.phase[n], phase_verlauf(par, erg))

    def fitparameter(self):
        """
        :rtype: Parameter
        """
        fmin = self.fmin.get_value()
        fmax = self.fmax.get_value()
        df = self.df.get_value()

        return Parameter(
            fmin=fmin,
            fmax=fmax,
            df=df,
            pixel=self.pixel.get_value_as_int(),
            dim=self.dim.get_value(),
            mittelungen=self.mittelungen.get_value_as_int(),
            amp_fitfkt=self.combobox('methode_amp').get_active(),
            ph_fitfkt=self.combobox('methode_phase').get_active(),
            filter_breite=self.spinbutton('savgol_koeff').get_value_as_int(),
            filter_ordnung=self.spinbutton('savgol_ordnung').get_value_as_int(),
            phase_versatz=self.spinbutton('phase_versatz').get_value(),
            bereich_min=self.bereich_min.get_value(),
            bereich_max=self.bereich_max.get_value(),
            amp=Fitparameter(
                guete_min=self.spinbutton('q_min').get_value(),
                guete_max=self.spinbutton('q_max').get_value(),
                off_min=self.spinbutton('off_min').get_value(),
                off_max=self.spinbutton('off_max').get_value()
            ),
            amp_min=self.spinbutton('amp_min').get_value(),
            amp_max=self.spinbutton('amp_max').get_value(),
            phase=Fitparameter(
                guete_min=self.spinbutton('phase_q_min').get_value(),
                guete_max=self.spinbutton('phase_q_max').get_value(),
                off_min=self.spinbutton('phase_off_min').get_value(),
                off_max=self.spinbutton('phase_off_max').get_value()
            ),
            konf=self.konf,
            version=self.version
        )

    def messwerte_lesen(self, par):
        """
        :type par: Parameter
        :rtype: (numpy.multiarray.ndarray, numpy.multiarray.ndarray)
        """
        tdms = TDMS(par, self.konf)
        self.amplitude = tdms.messwerte_lesen(self.konf.amp)
        if par.nr_fkt_ph is not None:
            self.phase = tdms.messwerte_lesen(self.konf.phase)
        self.get_object('pixel2').set_upper(self.pixel.get_value() ** 2)

    def fit_starten(self, _):
        par = self.fitparameter()

        # Fortschrittsanzeige:
        self.fortschritt.set_value(0)
        self.fortschritt.set_pulse_step(1 / par.pixel)
        self.ui.hide_all()
        self.ff.show_all()
        while gtk.events_pending():
            gtk.main_iteration_do(True)
        pass

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

        anlegen([n.amp for n in erg], "Amplitude (V)", "V")
        anlegen([n.phase for n in erg], "Phase (°)", "°")
        anlegen([n.resfreq for n in erg], "Resonanzfrequenz (Hz)", "Hz")
        anlegen([n.guete_amp for n in erg], u"Güte (Amplitudenfit)", "")
        anlegen([n.guete_ph for n in erg], u"Güte (Phasenfit)", "")
        anlegen([n.guete_amp for n in erg], "Mittlere Abweichung (V)", "V")
        anlegen([n.untergrund for n in erg], "Untergrund (V)", "V")
        anlegen([n.phase_rel for n in erg], "Phasenversatz (°)", "°")

        Format.set_custom(self.container, ERGEBNIS, erg)
        Format.set_custom(self.container, PARAMETER, par)

        self.ff.hide_all()
        gtk.main_quit()

    # Hilfsfunktionen (für Typentreue):

    def window(self, name):
        """
        :type name: str
        :rtype: gtk.Window
        """
        return self.get_object(name)

    def spinbutton(self, name):
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

    def radiobutton(self, name):
        """
        :type name: str
        :rtype: gtk.RadioButton
        """
        return self.get_object(name)

    def entry(self, name):
        """
        :type name: str
        :rtype: gtk.Entry
        """
        return self.get_object(name)
