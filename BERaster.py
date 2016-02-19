# coding=utf-8
"""
@author: Sebastian Badur
"""

from ConfigParser import ConfigParser, NoOptionError

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
    if dateiname.endswith('.ini'):
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
    if kopf.startswith('['+konfig+']'):
        return 100
    else:
        return 0


def load(dateiname, modus=None):
    """
    :type dateiname: str
    :param modus: Gwyddion-Ausführungsmodus (Vorschau / Interaktiv)
    :rtype: gwy.Container
    """
    parser = ConfigParser()
    parser.read(dateiname)

    try:
        d = gwy.DataField(
            parser.getint(konfig, 'x_anz'),
            parser.getint(konfig, 'y_anz'),
            parser.getfloat(konfig, 'x_dim'),
            parser.getfloat(konfig, 'y_dim'),
            False
        )
    except NoOptionError:
        return None

    c = gwy.Container()
    c.set_object_by_name('/0/data', d)

    if modus == gwy.RUN_INTERACTIVE:
        # PLUGIN AUSFÜHREN:
        import sys
        from os import path
        if not DEBUG:
            sys.path.append('.gwyddion/pygwy/')
            from SpeckView.BE.Laden import Laden
            Laden('.gwyddion/pygwy/SpeckView/ui.glade', path.dirname(dateiname), parser, d)
        else:
            from SpeckView.BE.Laden import Laden
            Laden('SpeckView/ui.glade', path.dirname(dateiname), parser, d)

    return c
