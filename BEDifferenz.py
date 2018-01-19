# coding=utf-8
"""
@author: Sebastian Badur
"""

import gwy
plugin_type = 'PROCESS'
plugin_desc = "Zwei Bildkanäle über einen neutralen Bereich gewichtet subtrahieren"
plugin_menu = "/Bandanregung/Differenz bilden"


def run():
    from os import path
    home = path.expanduser('~')
    from platform import system
    if system() == 'Linux':
        gwyddion = '.gwyddion'
    else:
        gwyddion = 'gwyddion'
    sv = path.join(home, gwyddion, 'pygwy', 'SpeckView')

    from SpeckView.Dialog import Dialog
    Dialog(sv).info("Differenz bilden", "Nach Auswählen der ELEKTRISCHEN Amplitude bestätigen.")
    c = gwy.gwy_app_data_browser_get_current(gwy.APP_CONTAINER)
    el = gwy.gwy_app_data_browser_get_current(gwy.APP_DATA_FIELD)
    Dialog(sv).info("Differenz bilden", "Nach Auswählen der MECHANISCHEN Amplitude bestätigen.")
    me = gwy.gwy_app_data_browser_get_current(gwy.APP_DATA_FIELD)

    sub = el.new_alike(False)

    def differenz(faktor):
        mul = me.duplicate()
        mul.multiply(faktor)
        sub.subtract_fields(el, mul)
        return sub

    from numpy import array
    from scipy.optimize import minimize
    optimal = minimize(lambda x: abs(differenz(x).get_variation()), array([1]))

    if not hasattr(c, 'n_dd'):
        c.n_dd = 1000
    name = '/' + str(c.n_dd) + '/data'
    c.set_object_by_name(name, differenz(optimal.x[0]))
    c.set_string_by_name(name + '/title', "Amplitudendifferenz")
    c.set_boolean_by_name(name + '/visible', True)
    c.n_dd += 1

    return True
