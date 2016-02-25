# coding=utf-8
"""
@author: Sebastian Badur
"""

import gwy
plugin_type = 'PROCESS'
plugin_desc = "Darstellung des Spektrums an einem Ort"
plugin_menu = "/SpeckView/BE-Spektren darstellen"


def run():
    import sys
    import os
    sys.path.append(os.getenv('HOME') + '/.gwyddion/pygwy/')
    from SpeckView import Format

    c = gwy.gwy_app_data_browser_get_current(gwy.APP_CONTAINER)
    sys.stderr.write(Format.get_custom(c))
