# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
from os import path


class Export(gtk.Builder):
    def __init__(self, sv):
        gtk.Builder.__init__(self)
        self.add_from_file(path.join(sv, 'export.glade'))
        self.antwort = False
        self.export = self.get_object('export')
        """ :type: gtk.Window """
        self.connect_signals({
            'ok': lambda _: self.speichern(),
            'png': lambda _: self.vorschau(),
            'cb': lambda _: self.cb()
        })
        self.tex = True
        self.cbb = self.get_object('cbBeschriftung')
        self.bes = self.get_object('beschriftung')
        self.obn = self.get_object('legendeOben')
        self.unt = self.get_object('legendeUnten')
        self.cbm = self.get_object('cbMaszstab')
        self.mas = self.get_object('maszstab')
        self.bes.set_sensitive(False)
        self.mas.set_sensitive(False)

    def optionen(self, oben, unten, masz):
        self.obn.set_text(oben)
        self.unt.set_text(unten)
        self.mas.set_text(masz)

        self.export.show_all()
        gtk.main()
        return self.tex, self.cbb.get_active(), self.bes.get_text(), self.obn.get_text(), self.unt.get_text(), \
               self.cbm.get_active(), self.mas.get_text()

    def speichern(self):
        self.export.hide()
        gtk.main_quit()

    def vorschau(self):
        self.tex = False
        self.speichern()

    def cb(self):
        self.bes.set_sensitive(self.cbb.get_active())
        self.mas.set_sensitive(self.cbm.get_active())
