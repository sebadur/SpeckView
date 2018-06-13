# coding=utf-8
"""
@author: Sebastian Badur
"""

import numpy

from SpeckView.Sonstige import Fehler


class Parameter:
    """ Alle für den Fit nötigen Messparameter """
    def __init__(self, fmin, fmax, df, raster, pixel, dim, spektroskopie, hysterese, dcmin, dcmax, ddc, mittelungen,
                 amp_fitfkt, ph_fitfkt, filterfkt, filter_breite, filter_ordnung, linkorr_a1, linkorr_a2, phase_versatz,
                 bereich_min, bereich_max, amp, amp_min, amp_max, phase, konf, kanal, version):
        """
        :type fmin: int
        :type fmax: int
        :type df: int
        :type raster: bool
        :type pixel: int
        :type dim: float
        :type spektroskopie: bool
        :type hysterese: bool
        :type dcmin: float
        :type dcmax: float
        :type ddc: float
        :type mittelungen: int
        :param amp_fitfkt: Nummer der Fitfunktion für die Amplitude
        :type amp_fitfkt: int
        :param ph_fitfkt: Nummer der Fitfunktion für die Phase
        :type ph_fitfkt: int
        :param amp_fitfkt: Nummer der Filterfunktion für die Amplitude
        :type amp_fitfkt: int
        :type filter_breite: int
        :type filter_ordnung: int
        :type linkorr_a1: float
        :type linkorr_a2: float
        :param phase_versatz: Die zur Resonanz gehörige Phase wird diesen Frequenzversatz neben der Resonanzfrequenz aus
        der geglätteten Phasenmessung entnommen.
        :type phase_versatz: int
        :type bereich_min: float
        :type bereich_max: float
        :type amp: Fitparameter
        :type amp_min: float
        :type amp_max: float
        :type phase: Fitparameter
        :type konf: str
        :type kanal: str
        :type version: int
        """
        if fmin >= fmax or amp_min >= amp_max:
            raise Fehler()

        self.amp_min = amp_min
        """ Minimale Amplitude für den Fit """
        self.amp_max = amp_max
        """ Maximale Amplitude für den Fit """
        self.amp = amp
        """ Beschränkungen der Fitparameter für die Amplitude """
        self.phase = phase
        """ Beschränkungen der Fitparameter für die Phase """

        self.fmin_voll = fmin
        """ Anfangsfrequenz des vollen Bereichs der aufgenommenen Bandanregung """
        self.fmin = bereich_min
        """ Anfangsfrequenz des Spektrums der Bandanregung im gewählten Frequenzbereich in Hz """
        self.fmax_voll = fmax
        """ Endfrequenz des vollen Messbereichs der Bandanregung """
        self.fmax = bereich_max
        """ Endfrequenz des Spektrums der Bandanregung im gewählten Frequenzbereich in Hz """
        self.pixel = pixel
        """ Pixelgröße des (quadratischen) Messbereichs """
        self.dim = dim
        """ Physikalische Dimension des Messbereichs """
        self.mittelungen = mittelungen
        """ Anzahl der nachträglichen Mittelungen pro Rasterpunkt """
        self.nr_fkt_amp = amp_fitfkt
        """ Zum Fitten der Amplitude in Abhängigkeit zur Phase für jede einzelne Messung verwendete Funktion """
        self.nr_fkt_filter = filterfkt
        """ Die zu verwendende Filterfunktion für die Amplitude """
        self.nr_fkt_ph = ph_fitfkt
        """ Fitfunktion für die Phase """
        self.filter_breite = filter_breite
        """ Breite des Filterfensters """
        self.filter_ordnung = filter_ordnung
        """ Ordnung des Filterpolynoms """
        self.linkorr_a1 = linkorr_a1
        """ Anfangsamplitude der Linearkorrektur """
        self.linkorr_a2 = linkorr_a2
        """ Endamplitude der Linearkorrektur """
        self.phase_versatz = phase_versatz
        """ Die Phase wird diesen Versatz in Hz neben der Resonanzfrequenz der Phasenauswertung entnommen """

        self.konf = konf
        """ Konfigurationseinstellungen """

        self.version = version
        """ Version der Speicherdatei (Standard = 3) """

        self.df = df
        """ Abstand der Messwerte auf der Frequenzskala in Hz """
        self.messpunkte = int((fmax - fmin) // df)
        """ Anzahl der Messpunkte bezüglich der Freqzenz """

        self.bereich_links = int((bereich_min - fmin) // df)
        """ Linker Rand in Messpunkten für Fitbereich """
        self.bereich_rechts = int((bereich_max - fmax) // df)
        """ Rechter Rand in Messpunkten des Fitbereichs (negativ) """

        self.raster = raster
        """ Gridmodus, oder nicht """
        self.spektroskopie = spektroskopie
        """ DC-Spektroskopie, oder nicht """
        self.hysterese = hysterese
        """ DC-Hysterese, oder nicht """
        self.dcmin = dcmin
        """ Niedrigster DC-Wert in Volt """
        self.dcmax = dcmax
        """ Höchster DC-Wert in Volt """
        self.ddc = ddc
        """ Abstand der DC-Werte in Volt """
        self.spektren = 0
        """ Anzahl der in dieser Messung aufgezeichneten Spektren, die alle gefittet werden müssen """
        if raster:
            self.spektren = pixel ** 2
        else:
            self.spektren = 1
        if spektroskopie:
            if hysterese:
                self.spektren *= int(2 * (dcmax - dcmin) / ddc + 1)
            else:
                self.spektren *= int((dcmax - dcmin) / ddc + 1)

        self.kanal = kanal
        """ Kanal der Tdms-Datei (elstat/elmech) """


def index_freq(par, freq):
    """
    :type par: Parameter
    :type freq: float
    :return: Index der Frequenz innerhalb des beschränkten Frequenzbereichs
    :rtype: int
    """
    return int((freq - par.fmin) // par.df)


_freq = []


def frequenzen(par):
    """
    :type par: Parameter
    :rtype: numpy.multiarray.ndarray
    """
    global _freq
    if len(_freq) < 1 or _freq[0] != par.fmin or _freq[-1] != par.fmax or _freq[1]-_freq[0] != par.df:
        _freq = numpy.arange(par.fmin, par.fmax, par.df)
    return _freq


_freqv = []


def frequenzen_voll(par):
    """
    :type par: Parameter
    :rtype: numpy.multiarray.ndarray
    """
    global _freqv
    if len(_freqv) < 1 or _freqv[0] != par.fmin_voll or _freqv[-1] != par.fmax_voll or _freqv[1]-_freqv[0] != par.df:
        _freqv = numpy.arange(par.fmin_voll, par.fmax_voll, par.df)
    return _freqv


class Fitparameter:
    def __init__(self, guete_min, guete_max, off_min, off_max):
        """
        :type guete_min: float
        :type guete_max: float
        :type off_min: float
        :type off_max: float
        """
        if guete_min >= guete_max or off_min >= off_max:
            raise Fehler()

        self.guete_min = guete_min
        """ Minimaler Gütefaktor beim Amplitudenfit """
        self.guete_max = guete_max
        """ Maximaler Gütefaktor beim Amplitudenfit """
        self.off_min = off_min
        """ Minimaler Untergrund beim Amplitudenfit """
        self.off_max = off_max
        """ Maximaler Untergrund beim Amplitudenfit """
