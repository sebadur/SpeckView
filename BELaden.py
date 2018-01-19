# coding=utf-8
"""
@author: Sebastian Badur
"""

from ConfigParser import ConfigParser, Error

import gwy
plugin_type = 'FILE'
plugin_desc = "Bandanregungsspektrum (.be)"


def detect_by_name(dateiname):
    """
    :type dateiname: str
    :rtype: int
    """
    if dateiname.endswith('.be'):
        return 100
    else:
        return 0


def detect_by_content(dateiname, kopf, s, g):
    """
    :type dateiname: str
    :type kopf: str
    :type s: str
    :type g: int
    :rtype: int
    """
    try:
        parser = ConfigParser()
        parser.read(dateiname)
        if parser.getint('BE', 'Version') <= 4:
            return 100
    except Error:
        pass
    return 0


def load(dateiname, modus=None):
    """
    :type dateiname: str
    :param modus: Gwyddion-Ausführungsmodus (Vorschau / Interaktiv)
    :rtype: gwy.Container
    """
    if modus == gwy.RUN_INTERACTIVE:
        # PLUGIN AUSFÜHREN:
        from os import path
        home = path.expanduser('~')
        from platform import system
        if system() == 'Linux':
            gwyddion = '.gwyddion'
        else:
            gwyddion = 'gwyddion'
        pygwy = path.join(home, gwyddion, 'pygwy')
        svbe = path.join(pygwy, 'SpeckView', 'BE')

        from SpeckView.BE.Laden import Laden
        geladen = Laden(path.relpath(dateiname), svbe)

        daten = geladen.container
        del geladen
        return daten

    else:  # Vorschau
        return None


def save(daten, dateiname, modus=None):
    return False
