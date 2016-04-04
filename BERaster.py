# coding=utf-8
"""
@author: Sebastian Badur
"""

from ConfigParser import ConfigParser, Error

import gwy
plugin_type = 'FILE'
plugin_desc = "Bandanregungsspektrum (.ini)"


DEBUG = False
konfig = 'konfig'


def detect_by_name(dateiname):
    """
    :type dateiname: str
    :rtype: int
    """
    if dateiname.endswith('.ber'):
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
        if parser.get(konfig, 'format') == '"BE Raster"':
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
        import sys
        import os
        from os.path import sep
        home = os.getenv('HOME')
        verzeichnis = home + sep + '.gwyddion' + sep + 'pygwy' + sep + 'SpeckView' + sep + 'BE'
        pygwy = home + sep + '.gwyddion' + sep + 'pygwy'
        if not DEBUG:
            sys.path.append(pygwy)

        from SpeckView.BE.Konfiguration import KonfigFenster
        from SpeckView.BE.Laden import Laden
        geladen = Laden(KonfigFenster(verzeichnis, dateiname, pygwy).konf)

        # TODO Test: Befreien der reservierten Resourcen (Gwyddion-Bug?)
        return geladen.container

    else:  # Vorschau
        return None
