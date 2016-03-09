# coding=utf-8
"""
@author: Sebastian Badur
"""

import gwy
plugin_type = 'PROCESS'
plugin_desc = "Debugfunktionen"
plugin_menu = "/SpeckView/Debug"


def run():
    pass


if __name__ == '__main__':
    import BERaster
    BERaster.DEBUG = True
    messung = "/home/sebadur/Dokumente/BaTiO3/2016-03-08-R/16-03-08-11-16-50.ber"

    print "Name: " + str(BERaster.detect_by_name(messung))

    print "Inhalt: " + str(BERaster.detect_by_content(messung, "", "", 0))

    from SpeckView import Format
    from SpeckView.BE.Ergebnis import Ergebnis
    c = gwy.Container()
    debug = "debug"
    Format.set_custom(
        c, debug,
        [Ergebnis(1, 2, 3, 4, 5)]
    )
    erg = Format.get_custom(c, debug)
    """ :type: list[SpeckView.BE.Ergebnis.Ergebnis] """
    print erg
    print erg[0].amp

    BERaster.load(messung, gwy.RUN_INTERACTIVE)
