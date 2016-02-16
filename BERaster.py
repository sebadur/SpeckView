# coding=utf-8
"""
@author: Sebastian Badur
"""

from ConfigParser import ConfigParser, NoOptionError

import gwy
plugin_type = 'FILE'
plugin_desc = "Bandanregungsspektrum (.ini)"
plugin_menu = ""


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
        gui_laden(dateiname)
    return c


def gui_laden(dateiname):
    """
    :type dateiname: str
    """
    import gtk
    import sys
    sys.path.append('.gwyddion/pygwy/')
    from SpeckView.Plotter import Plotter

    ui = gtk.Window(gtk.WINDOW_TOPLEVEL)
    widget = gtk.VBox()
    widget.set_size_request(400, 400)
    ui.add(widget)
    sb = gtk.Statusbar()
    sb.show()
    widget.add(sb)
    widget.add(Plotter(sb, "x", "y"))
    widget.show()
    ui.show()
