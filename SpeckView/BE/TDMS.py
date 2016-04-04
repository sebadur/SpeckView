# coding=utf-8
"""
@author: Sebastian Badur
"""

from os import path
import numpy
from nptdms import TdmsFile
from multiprocessing import Pool


class TDMS:
    def __init__(self, par, konf):
        """
        :type par: SpeckView.BE.Parameter.Parameter
        :type konf: SpeckView.BE.Konfiguration.Konfiguration
        """
        self.par = par
        self.konf = konf

    def messwerte_lesen(self, typ):
        """
        :type typ: str
        :rtype: numpy.multiarray.ndarray
        """
        global _par, _typ
        _par = self.par
        _typ = typ

        if self.par.version == 2:
            #  Komplettes Raster in einer Datei
            return _lade_tdms(
                tdms=TdmsFile(_par.konf.datei.rsplit('.ber', 1)[0] + '.tdms').object(_par.konf.gruppe, typ)
            )
        else:
            if self.par.version == 1:
                start = 1
            else:
                start = 0
            #  Je eine Datei pro Zeile im Raster
            return numpy.reshape(
                Pool().map(_lade_zeile, range(start, start + _par.pixel)),
                (-1, _par.messpunkte)
            )


_par = None
""" :type: SpeckView.BE.Parameter.Parameter """
_typ = ''


def _lade_zeile(y):
    """
    :type y: int
    :rtype: numpy.multiarray.ndarray
    """
    return _lade_tdms(
        TdmsFile(_par.konf.pfad + path.sep + _typ + str(y) + '.tdms').object(_par.konf.gruppe, _par.konf.kanal),
        dim=1
    )


def _lade_tdms(tdms, dim=2):
    """
    :type tdms: nptdms.TdmsObject
    :type dim: int
    :rtype: numpy.multiarray.ndarray
    """
    pixel = _par.pixel ** dim
    messpunkte = _par.messpunkte
    mittelungen = _par.mittelungen

    daten = numpy.zeros((pixel, messpunkte))

    for n in range(pixel):
        for durchlauf in range(mittelungen):
            try:
                """
                Mittelung (durch Addition)
                UND
                Begrenzung des Fitbereichs (zur Eliminierung von parasitären Frequenzpeaks) nach Angabe in GUI
                """
                von = n * messpunkte * mittelungen + durchlauf * messpunkte
                bis = von + messpunkte
                daten[n] += tdms.data[von:bis]
            except ValueError:
                """
                Fehlende Daten werden hier zunächst ignoriert
                """
                pass

    return daten / mittelungen
