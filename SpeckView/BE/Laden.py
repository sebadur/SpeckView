# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
import numpy
from gwy import Container, SIUnit
from os.path import sep
from multiprocessing import Queue
from multiprocessing.queues import Empty

from SpeckView.Dialog import Dialog
from SpeckView import Format
from SpeckView.Plotter import Plotter
from SpeckView.Parser import DefaultParser

from Ergebnis import amp_verlauf, phase_verlauf
from Fit import Fit
from Konstant import *
from Parameter import *
from TDMS import TDMS


# Relevante Sektionen des BE-Formats Version 3
opt = 'BE'
sgl = 'Signal'
sgn = 'Signalgenerator'
man = 'Manipulation'
rst = 'Raster'


class Laden(gtk.Builder):
    def __init__(self, konf, svbe):
        """
        :type konf: str
        """
        self.konf = konf

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

        self.parser = DefaultParser()
        self.parser.read(konf)
        self.parser.getint = lambda sektion, option: int(self.parser.get(sektion, option).rsplit(',', 1)[0])

        self.version = self.parser.getint(opt, 'Version')
        if self.version >= 3:
            self.sv = svbe + sep + '..'
            if Dialog(self.sv).frage("Kanal", "Den gewünschten Kanal wählen:", "elstat.", "elmech."):
                self.kanal = 'elstat'
            else:
                self.kanal = 'elmech'
        else:
            self.kanal = 'Untitled'

        self.pixel = self.spinbutton('pixel')
        self.pixel.set_value(self.parser.getint(rst, 'Pixel'))
        self.dim = self.spinbutton('dim')
        self.dim.set_value(self.parser.getfloat(rst, 'Dimension'))

        self.df = self.spinbutton('df')
        self.df.set_value(self.parser.getfloat(sgl, 'Rate') / self.parser.getfloat(sgl, 'Sample'))
        self.mittelungen = self.spinbutton('mittelungen')
        self.mittelungen.set_value(1)
        self.fmin = self.spinbutton('fmin')
        self.bereich_min = self.spinbutton('bereich_min')
        fmin = self.parser.getint(sgn, 'f_start')
        self.fmin.set_value(fmin)
        self.bereich_min.set_value(fmin)
        self.fmax = self.spinbutton('fmax')
        self.bereich_max = self.spinbutton('bereich_max')
        fmax = self.parser.getint(sgn, 'f_ende')
        self.fmax.set_value(fmax)
        self.bereich_max.set_value(fmax)

        self.plotter = Plotter("Frequenz (Hz)", "Amplitude (V)")
        self.get_object('vorschau').add(self.plotter)
        self.ui.show_all()
        gtk.main()

    def vorschau(self, _):
        n = self.spinbutton('vorschau_spektren').get_value()
        par = self.fitparameter()
        frequenz = frequenzen(par)
        if self.amplitude is None:
            self.messwerte_lesen(par)
        erg = Fit(par, self.amplitude, self.phase, lambda(n): None).vorschau(n)

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
        return Parameter(
            fmin=self.fmin.get_value(),
            fmax=self.fmax.get_value(),
            df=self.df.get_value(),
            raster=self.parser.getboolean(rst, 'Raster'),
            pixel=self.pixel.get_value_as_int(),
            dim=self.dim.get_value(),
            spektroskopie=self.parser.getboolean(man, 'Spektroskopie'),
            hysterese=self.parser.getboolean(man, 'Hysterese'),
            dcmin=self.parser.getfloat(man, 'Umin'),
            dcmax=self.parser.getfloat(man, 'Umax'),
            ddc=self.parser.getfloat(man, 'dU'),
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
            kanal=self.kanal,
            version=self.version
        )

    def messwerte_lesen(self, par):
        """
        :type par: Parameter
        :rtype: (numpy.multiarray.ndarray, numpy.multiarray.ndarray)
        """
        tdms = TDMS(par, par.konf)
        self.amplitude = tdms.messwerte_lesen(self.kanal, 'amp')
        if par.nr_fkt_ph is not None:
            self.phase = tdms.messwerte_lesen(self.kanal, 'phase')
        self.get_object('spektren').set_upper(par.spektren)

    def fit_starten(self, _):
        par = self.fitparameter()

        # Messwerte einlesen:
        self.messwerte_lesen(par)

        self.ui.hide_all()
        self.ff.show_all()
        q = Queue()
        # Fitten:
        fit = Fit(par, self.amplitude, self.phase, q.put)
        erg = fit.start()

        x = 0.0
        while not erg.ready():
            gtk.main_iteration_do(False)
            try:
                q.get_nowait()
                x += 1.0 / par.spektren
                self.fortschritt.set_fraction(x)
            except Empty:
                pass
        q.close()
        erg = erg.get()
        """ :type: list[Ergebnis] """

        del self.amplitude, self.phase, fit

        # Gwyddion-Datenfeld:
        self.container = Container()

        def anlegen(inhalt, titel, einheit):
            if par.raster:
                Format.channel_data(
                    c=self.container,
                    inhalt=inhalt,
                    einheit_xy=SIUnit('m'),
                    einheit_z=SIUnit(einheit),
                    titel=titel,
                    dim=par.dim,
                    pixel=par.pixel  # TODO geht nur, wenn kein Spektrum
                )
            else:
                Format.spectra_data(
                    c=self.container,
                    x=hysterese(par.dcmin, par.dcmax, par.ddc),
                    y=inhalt,
                    label_x='', label_y=''
                )

        if par.spektroskopie:  # TODO Notlösung entfernen
            datei = open(par.konf.rsplit('.be', 1)[0] + ".fit", 'w')
            dc = hysterese(par.dcmin, par.dcmax, par.ddc)
            datei.write('DC/V,A/V,dA/V,f0/Hz,df0/Hz,Q,dQ,Phase\n')
            for n in range(par.spektren):
                datei.write(
                    str(dc[n]) + ',' + str(erg[n].amp) + ',' + str(erg[n].amp_fhlr) + ',' +
                    str(erg[n].resfreq) + ',' + str(erg[n].resfreq_fhlr) + ',' + str(erg[n].guete_amp) + ',' +
                    str(erg[n].guete_amp_fhlr) + ',' + str(erg[n].phase) + '\n'
                )
            datei.close()
            Dialog(self.sv).info("Gespeichert", "Fit gespeichert in " + datei.name)

        else:
            anlegen([n.amp for n in erg], "Amplitude", 'V')
            anlegen([n.phase for n in erg], "Phase", '°')
            anlegen([n.resfreq for n in erg], "Resonanzfrequenz", 'Hz')
            anlegen([n.guete_amp for n in erg], u"Güte (Amplitudenfit)", '')
            anlegen([n.amp_fhlr for n in erg], "Fehler Amp.", 'V')
            anlegen([n.phase_fhlr for n in erg], "Fehler Phase", '°')
            anlegen([n.resfreq_fhlr for n in erg], "Fehler Resfreq.", 'Hz')
            anlegen([n.guete_amp_fhlr for n in erg], u"Fehler Güte (Ampfit.)", '')
            anlegen([n.guete_ph for n in erg], u"Güte (Phasenfit)", '')
            anlegen([n.untergrund for n in erg], "Untergrund", 'V')
            anlegen([n.phase_rel for n in erg], "Phasenversatz", '°')

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


def hysterese(min, max, d):
    mitte = (max + min) / 2
    return numpy.concatenate((
        numpy.arange(mitte, max, d),
        numpy.arange(max, min, -d),
        numpy.arange(min, mitte, d),
        [ mitte ]
    ))
