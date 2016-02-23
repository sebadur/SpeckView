# coding=utf-8
"""
@author: Sebastian Badur
"""

from ConfigParser import ConfigParser, Error

import gwy
plugin_type = 'FILE'
plugin_desc = "Bandanregungsspektrum (.ini)"
plugin_menu = ""


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
        if parser.get(konfig, 'format') == 'BE Raster':
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

    parser = ConfigParser()
    parser.read(dateiname)
    pixel = parser.getint(konfig, 'pixel')
    dim = parser.getfloat(konfig, 'dim')
    d = gwy.DataField(pixel, pixel, dim, dim, False)

    c = gwy.Container()
    c.set_object_by_name('/0/data', d)

    if modus == gwy.RUN_INTERACTIVE:
        # PLUGIN AUSFÜHREN:
        import sys
        from os import path
        if not DEBUG:
            sys.path.append('.gwyddion/pygwy/')
            ui = '.gwyddion/pygwy/SpeckView/ui.glade'
        else:
            ui = 'SpeckView/ui.glade'
        from SpeckView.BE.Laden import Laden
        Laden(ui, path.dirname(dateiname), parser, d)

    return c
