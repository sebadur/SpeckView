# coding=utf-8
"""
@author: Sebastian Badur
"""

import gwy
plugin_type = 'PROCESS'
plugin_desc = "Amplituden-Frequenz-Korrelation darstellen"
plugin_menu = "/Bandanregung/A0-f0-Korrelation"


def feld1d(d0):
    import numpy as np
    return np.array(d0.get_data()).flatten()


def auswahl():
    d0 = gwy.gwy_app_data_browser_get_current(gwy.APP_DATA_FIELD)
    d0m = gwy.gwy_app_data_browser_get_current(gwy.APP_MASK_FIELD)
    if d0m is not None:
        return feld1d(d0), feld1d(d0m)
    else:
        return feld1d(d0), []


def run():
    from os import path
    home = path.expanduser('~')
    from platform import system
    if system() == 'Linux':
        gwyddion = '.gwyddion'
    else:
        gwyddion = 'gwyddion'
    sv = path.join(home, gwyddion, 'pygwy', 'SpeckView')

    import numpy as np
    from SpeckView.Dialog import Dialog
    Dialog(sv).info("Korrelation Y", "Nach Auswählen der AMPLITUDE bestätigen.")
    c = gwy.gwy_app_data_browser_get_current(gwy.APP_CONTAINER)
    y, ym = auswahl()
    a0id = gwy.gwy_app_data_browser_get_current(gwy.APP_DATA_FIELD_ID)
    anzeigen = Dialog(sv).frage("Korrelation X", "Jetzt FREQUENZ auswählen.", "anzeigen", "speichern")
    x, xm = auswahl()

    # Beide Masken kombinieren und zugehörige Daten löschen
    m = np.unique(np.concatenate((np.where(ym == 1)[0], np.where(xm == 1)[0])))
    x = np.delete(x, m)
    y = np.delete(y, m)

    if anzeigen:
        import matplotlib
        matplotlib.rcParams['backend'] = "GTKAgg"
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.scatter(x, y, marker='.', color='k', label="A")

        ax.set_xlabel("f0 [Hz]")
        ax.set_ylabel("A0 [m]")
        ax.set_xlim(x.min(), x.max())
        ax.set_ylim(y.min(), y.max())
        plt.legend()
        plt.show()

    else:
        appendix = gwy.gwy_app_get_data_field_title(c, a0id).split(' ', 1)[0].lower()
        dat = gwy.gwy_file_get_filename_sys(c).rsplit('.', 1)[0] + '-' + appendix + '.dat'
        np.array((x, y)).T.tofile(dat)
        Dialog(sv).info("Korrelation gespeichert", "In Datei gespeichert:\n" + dat)

    return True
