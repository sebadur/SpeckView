# coding=utf-8
"""
@author: Sebastian Badur
"""

from os import path
import numpy
from nptdms import TdmsFile
from multiprocessing import Pool


class TDMS:
    def __init__(self, par):
        """
        :type par: SpeckView.BE.Parameter.Parameter
        """
        self.par = par

    def messwerte_lesen(self, typ):
        """
        :type typ: str
        :rtype: numpy.multiarray.ndarray
        """
        global _par, _typ
        _par = self.par
        _typ = typ
        return numpy.reshape(
            Pool().map(_lade_tdms, range(1, _par.pixel + 1)),
            (-1, _par.messpunkte)
        )


_par = None
""" :type: SpeckView.BE.Parameter.Parameter """
_typ = ''


def _lade_tdms(y):
    """
    :type y: int
    :rtype: numpy.multiarray.ndarray
    """
    dateiname = _par.pfad + path.sep + _typ + str(y) + '.tdms'
    pixel = _par.pixel
    messpunkte = _par.messpunkte
    mittelungen = _par.mittelungen

    daten = numpy.zeros((pixel, messpunkte))
    tdms = TdmsFile(dateiname).object(_par.konf.gruppe, _par.konf.kanal)

    if len(tdms.data) != pixel * messpunkte * mittelungen:
        print("Die angegebenen Messparameter stimmen nicht für " + dateiname)
        return daten

    for x in range(pixel):
        for durchlauf in range(mittelungen):
            """
            Mittelung (durch Addition)
            UND
            Begrenzung des Fitbereichs (zur Eliminierung von parasitären Frequenzpeaks) nach Angabe in GUI
            """
            von = x * messpunkte * mittelungen + durchlauf * messpunkte
            bis = von + messpunkte
            daten[x] += tdms.data[von:bis]

    return daten / mittelungen
