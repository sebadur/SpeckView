# coding=utf-8
"""
@author: Sebastian Badur
@author: Valon Lushta
"""

import os
import numpy
from nptdms import TdmsFile
from glob import glob
from multiprocessing.dummy import Pool


class TDMS:
    def __init__(self, par):
        """
        :type par: SpeckView.BE.Parameter.Parameter
        """
        self.par = par

    def messwerte_lesen(self, typ):
        return numpy.reshape(
            Pool().map(self._lade_tdms, self._tdms_sortiert(typ)),
            (-1, self.par.messpunkte)
        )

    def _lade_tdms(self, dateiname):
        """
        :type dateiname: str
        :rtype: numpy.multiarray.ndarray
        """
        pixel = self.par.pixel
        messpunkte = self.par.messpunkte
        mittelungen = self.par.mittelungen

        index_fehler = False
        daten = numpy.ndarray((pixel, messpunkte))
        tdms = TdmsFile(dateiname).object(self.par.konf.gruppe, self.par.konf.kanal)

        for x in range(pixel):
            for durchlauf in range(mittelungen):
                try:
                    """
                    Mittelung (durch Addition)
                    UND
                    Begrenzung des Fitbereichs (zur Eliminierung von parasitären Frequenzpeaks) nach Angabe in GUI
                    """
                    links = x * messpunkte * mittelungen + durchlauf * messpunkte
                    rechts = links + messpunkte
                    daten[x] += tdms.data[links:rechts]

                except (ValueError, IndexError):
                    """
                    In diesem Fall ist ein Messfehler aufgetreten. Das kann (sehr selten) passieren, weshalb der Fit
                    dennoch funktionieren muss. Hier ist dann aber ein Einbruch in der Amplitude zu verzeichnen.
                    """
                    if not index_fehler:
                        index_fehler = True
                        print("Fehlende Messwerte in Datei " + dateiname)

        return daten / mittelungen

    def _tdms_sortiert(self, typ):
        """
        :type typ: str
        :rtype: list[str]
        """
        # Dateinamen aufteilen und numerisch sortieren:
        return sorted(
            glob(os.path.join(self.par.pfad, typ + '*.tdms')),  # alle Dateien in diesem Ordner mit der Endung TDMS
            key=lambda x: int(x.split(os.sep)[-1].split(typ)[1].split('.')[0])  # Zeilennummer hinter dem Typnamen
        )
