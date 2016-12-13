# coding=utf-8
"""
@author: Sebastian Badur
"""

import numpy
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

        tdms = TdmsFile(_par.konf.rsplit('.be', 1)[0] + '.tdms')
        return _lade_tdms(kanal=tdms.object(kanal, typ))

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

    daten = numpy.zeros((_par.spektren, messpunkte))

    for n in range(_par.spektren):
        for durchlauf in range(mittelungen):
            try:
                """
                Mittelung (durch Addition)
                UND
                Begrenzung des Fitbereichs (zur Eliminierung von parasitären Frequenzpeaks) nach Angabe in GUI
                """
                von = n * messpunkte * mittelungen + durchlauf * messpunkte
                bis = von + messpunkte
                daten[n] += kanal.data[von:bis]
            except ValueError:
                """
                Fehlende Daten werden hier zunächst ignoriert
                """
                pass

    return daten / mittelungen
