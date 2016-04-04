# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk


class Konfiguration:
    def __init__(self, verzeichnis, datei,
                 version="version", konfig="konfig",
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
        self.konfig = konfig
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
    def __init__(self, verzeichnis, konfig_datei):
        """
        :type verzeichnis: str
        :type konfig_datei: str
        """
        self.verzeichnis = verzeichnis
        self.konfig_datei = konfig_datei

        gtk.Builder.__init__(self)
        self.add_from_file(verzeichnis + '/konfig.glade')

        self.konf = None
        """ :type: Konfiguration """
        
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
            version=self.entry('version').get_text(),
            konfig=self.entry('name').get_text(),
            mittelungen=self.entry('mittelungen').get_text(),
            pixel=self.entry('pixel').get_text(),
            df=self.entry('df').get_text(),
            fmin=self.entry('fmin').get_text(),
            fmax=self.entry('fmax').get_text(),
            dim=self.entry('dim').get_text(),
            gruppe=self.entry('gruppe').get_text(),
            kanal=self.entry('kanal').get_text(),
            amp=self.entry('amp').get_text(),
            phase=self.entry('phase').get_text()
        )
        self.ui.destroy()
        gtk.main_quit()

    def entry(self, name):
        """
        :type name: str
        :rtype: gtk.Entry
        """
        return self.get_object(name)
