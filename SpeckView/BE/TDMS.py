# coding=utf-8
"""
@author: Sebastian Badur
"""

import numpy
import os
from nptdms import TdmsFile


class TDMS:
    def __init__(self, par, konf):
        """
        :type par: SpeckView.BE.Parameter.Parameter
        :type konf: str
        """
        self.par = par
        self.konf = konf

    def messwerte_lesen(self, kanal, typ):
        """
        :type kanal: str
        :type typ: str
        :rtype: numpy.multiarray.ndarray
        """
        global _par, _typ
        _par = self.par
        _typ = typ

        if _par.version >= 3:
            tdms = TdmsFile(os.path.expanduser('~') + os.sep + _par.konf.rsplit('.be', 1)[0] + '.tdms')
            return _lade_tdms(kanal=tdms.object(kanal, typ))
        else:
            pfad = _par.konf.rsplit(os.sep, 1)[0] + os.sep + typ
            for n in range(1, _par.pixel + 1):
                tdms = TdmsFile(pfad + str(n) + '.tdms')
                dat = _lade_tdms(kanal=tdms.object(kanal, 'Untitled'))
                if n == 1:
                    daten = dat
                else:
                    daten = numpy.append(daten, dat, axis=0)
            return daten


_par = None
""" :type: SpeckView.BE.Parameter.Parameter """
_typ = ''


def _lade_tdms(kanal):
    """
    :type kanal: nptdms.TdmsObject
    :rtype: numpy.multiarray.ndarray
    """
    messpunkte = _par.messpunkte
    mittelungen = _par.mittelungen
    if _par.version >= 3:
        spektren = _par.spektren
    else:
        spektren = _par.pixel

    daten = numpy.zeros((spektren, messpunkte))

    for n in range(spektren):
        for durchlauf in range(mittelungen):
            try:
                """
                Mittelung (durch Addition)
                UND
                Begrenzung des Fitbereichs (zur Eliminierung von parasitären Frequenzpeaks) nach Angabe in GUI
                """
                #von = ((3*n+1) * mittelungen + durchlauf) * messpunkte
                von = (n * mittelungen + durchlauf) * messpunkte
                bis = von + messpunkte
                daten[n] += kanal.data[von:bis]
            except ValueError:
                """
                Fehlende Daten werden hier zunächst ignoriert
                """
                pass

    return daten / mittelungen
