# coding=utf-8
"""
@author: Sebastian Badur
"""

import gwy
plugin_type = 'PROCESS'
plugin_desc = "Darstellung des Spektrums an einem Ort"
plugin_menu = "/Bandanregung/Spektren darstellen"


def run():
    import sys
    import os
    home = os.getenv('HOME')
    sys.path.append(home + '/.gwyddion/pygwy/')

    from SpeckView.BE.Spektrum import Spektrum
    Spektrum(
        home + '/.gwyddion/pygwy/SpeckView/',
        gwy.gwy_app_data_browser_get_current(gwy.APP_CONTAINER)
    )
