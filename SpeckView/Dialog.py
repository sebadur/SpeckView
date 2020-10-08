# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
from os import path


class Dialog(gtk.Builder):
    def __init__(self, sv):
        gtk.Builder.__init__(self)
        self.add_from_file(path.join(sv, 'dialog.glade'))
        self.antwort = False
        self.dialog = self.get_object('dialog')
        """ :type: gtk.Window """
        self.connect_signals({
            'ja': lambda _: self.ende(True),
            'nein': lambda _: self.ende(False)
        })

    def info(self, titel, info):
        self.get_object('ja').set_visible(False)
        self.dialog.set_title(titel)
        self.get_object('frage').set_text(info)
        self.get_object('ja').set_label("")
        self.get_object('nein').set_label("OK")
        self.dialog.show_all()
        gtk.main()

    def frage(self, titel, frage, ja, nein):
        """
        :type titel: str
        :type frage: str
        :type ja: str
        :type nein: str
        :rtype: bool
        """
        self.get_object('ja').set_visible(True)
        self.dialog.set_title(titel)
        self.get_object('frage').set_text(frage)
        self.get_object('ja').set_label(ja)
        self.get_object('nein').set_label(nein)
        self.dialog.show_all()
        gtk.main()
        return self.antwort

    def ende(self, antwort):
        """
        :type antwort: bool
        """
        self.antwort = antwort
        self.dialog.hide()
        gtk.main_quit()
