# coding=utf-8
"""
@author: Sebastian Badur
"""

from os import path
import gtk
import numpy
from gwy import Container
from ConfigParser import ConfigParser

from SpeckView.Plotter import Plotter
from SpeckView import Format

from Ergebnis import amp_verlauf, phase_verlauf
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
        self.glade = glade
        self.add_from_file(glade + '/laden.glade')
        self.connect_signals({
            'ende': gtk.main_quit,
            'fit_starten': self.fit_starten,
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
        # Komma und Punkt als Dezimaltrennzeichen erlauben (keine Tausendertrennzeichen):
        parser.getfloat = lambda s, o: float(parser.get(s, o).replace(',', '.'))
        parser.read(konfig_datei)

        konf = Konfiguration()
        self.konf = konf
        self.pixel = self.spinbutton('pixel')
        self.pixel.set_value(parser.getint(konf.konfig, konf.pixel))
        self.dim = self.spinbutton('dim')
        self.dim.set_value(parser.getfloat(konf.konfig, konf.dim))

        self.df = self.spinbutton('df')
        self.df.set_value(parser.getfloat(konf.konfig, konf.df))
        self.mittelungen = self.spinbutton('mittelungen')
        self.mittelungen.set_value(parser.getint(konf.konfig, konf.mittelungen))
        self.fmin = self.spinbutton('fmin')
        self.fmin.set_value(parser.getint(konf.konfig, konf.fmin))
        self.fmax = self.spinbutton('fmax')
        self.fmax.set_value(parser.getint(konf.konfig, konf.fmax))

        self.plotter = Plotter("Frequenz (Hz)", "Amplitude (V)")
        self.get_object('vorschau').add(self.plotter)
        self.ui.show_all()
        gtk.main()

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

        bereich_links = 0
        bereich_rechts = 0

        # self.spinbox('savgol_koeff').get_value()
        # self.spinbox('savgol_ordnung').get_value()
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
            phase_versatz=50,  # TODO und eigene Fitparameter für Phase!
            bereich_links=bereich_links,
            bereich_rechts=bereich_rechts,
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
        self.get_object('pixel2').set_upper(self.pixel.get_value() ** 2)

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
        anlegen([n.guete_amp for n in erg], u"Güte (Amplitudenfit)", "")
        anlegen([n.guete_ph for n in erg], u"Güte (Phasenfit)", "")
        anlegen([n.untergrund for n in erg], "Untergrund (a.u.)", "a.u.")
        anlegen([n.phase_rel for n in erg], "Phasenversatz (°)", "°")

        speichern = self.get_object('speichern')
        """ :type: gtk.CheckButton """
        permanent = speichern.get_active()

        Format.set_custom(self.container, ERGEBNIS, erg, permanent)
        Format.set_custom(self.container, PARAMETER, par, permanent)
        Format.set_custom(self.container, AMPLITUDE, self.amplitude, permanent)
        Format.set_custom(self.container, PHASE, self.phase, permanent)

        self.ff.hide_all()
        gtk.main_quit()
