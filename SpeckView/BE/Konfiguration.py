# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
import cPickle
from cPickle import UnpicklingError, HIGHEST_PROTOCOL
from os.path import sep


class Konfiguration:
    def __init__(self, verzeichnis, datei,
                 version="version",
                 mittelungen="mittelungen", pixel="pixel",
                 df="df", fmin="fmin", fmax="fmax", dim="dim",
                 gruppe="Unbenannt", kanal="Untitled",
                 amp="amp", phase="phase"):
        """
        :type verzeichnis: str
        :type datei: str
        """
        self.verzeichnis = verzeichnis
        self.datei = datei  # TODO path.relpath(datei)

        self.version = version
        self.konfig = 'konfig'
        self.df = df
        self.mittelungen = mittelungen
        self.fmin = fmin
        self.fmax = fmax
        self.gruppe = gruppe  # 'Unbenannt', 'Untitled', 'elmech'
        self.kanal = kanal
        self.amp = amp
        self.phase = phase
        self.pixel = pixel
        self.dim = dim


class KonfigFenster(gtk.Builder):
    def __init__(self, verzeichnis, konfig_datei, pygwy):
        """
        :type verzeichnis: str
        :type konfig_datei: str
        :type pygwy: str
        """
        self.verzeichnis = verzeichnis
        self.konfig_datei = konfig_datei
        self.zuletzt = pygwy + sep + 'SpeckView' + sep + 'BE' + sep + 'konfig.tmp'

        gtk.Builder.__init__(self)
        self.add_from_file(verzeichnis + sep + 'konfig.glade')

        try:
            self.konf = cPickle.load(open(self.zuletzt, 'r'))
            """ :type: Konfiguration """
        except (IOError, EOFError, UnpicklingError):
            self.konf = Konfiguration(verzeichnis, konfig_datei)

        self.version = self.entry('version')
        self.version.set_text(self.konf.version)
        self.mittelungen = self.entry('mittelungen')
        self.mittelungen.set_text(self.konf.mittelungen)
        self.pixel = self.entry('pixel')
        self.pixel.set_text(self.konf.pixel)
        self.df = self.entry('df')
        self.df.set_text(self.konf.df)
        self.fmin = self.entry('fmin')
        self.fmin.set_text(self.konf.fmin)
        self.fmax = self.entry('fmax')
        self.fmax.set_text(self.konf.fmax)
        self.dim = self.entry('dim')
        self.dim.set_text(self.konf.dim)
        self.gruppe = self.entry('gruppe')
        self.gruppe.set_text(self.konf.gruppe)
        self.kanal = self.entry('kanal')
        self.kanal.set_text(self.konf.kanal)
        self.amp = self.entry('amp')
        self.amp.set_text(self.konf.amp)
        self.phase = self.entry('phase')
        self.phase.set_text(self.konf.phase)

        self.ui = self.get_object('fenster')
        """ :type: gtk.Window """

        self.connect_signals({
            'fertig': self.fertig
        })

        self.ui.show_all()
        gtk.main()

    def fertig(self, *_):
        self.konf = Konfiguration(
            verzeichnis=self.verzeichnis,
            datei=self.konfig_datei,
            version=self.version.get_text(),
            mittelungen=self.mittelungen.get_text(),
            pixel=self.pixel.get_text(),
            df=self.df.get_text(),
            fmin=self.fmin.get_text(),
            fmax=self.fmax.get_text(),
            dim=self.dim.get_text(),
            gruppe=self.gruppe.get_text(),
            kanal=self.kanal.get_text(),
            amp=self.amp.get_text(),
            phase=self.phase.get_text()
        )
        self.ui.destroy()
        cPickle.dump(self.konf, open(self.zuletzt, 'w'), HIGHEST_PROTOCOL)
        gtk.main_quit()

    def entry(self, name):
        """
        :type name: str
        :rtype: gtk.Entry
        """
        return self.get_object(name)
