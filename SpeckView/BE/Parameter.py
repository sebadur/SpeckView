# coding=utf-8
"""
@author: Sebastian Badur
"""

import numpy

from SpeckView.Sonstige import Fehler


class Parameter:
    """ Alle für den Fit einer Rastermessung nötigen Messparameter """
    def __init__(self, fmin, fmax, df, pixel, dim, mittelungen, amp_fitfkt, ph_fitfkt, filter_breite, filter_ordnung,
                 phase_versatz, bereich_min, bereich_max, amp, amp_min, amp_max, phase, konf, version):
        """
        :type fmin: int
        :type fmax: int
        :type df: int
        :type pixel: int
        :type dim: float
        :type mittelungen: int
        :param amp_fitfkt: Nummer der Fitfunktion für die Amplitude
        :type amp_fitfkt: int
        :param ph_fitfkt: Nummer der Fitfunktion für die Phase
        :type ph_fitfkt: int
        :type filter_breite: int
        :type filter_ordnung: int
        :param phase_versatz: Die zur Resonanz gehörige Phase wird diesen Frequenzversatz neben der Resonanzfrequenz aus
        der geglätteten Phasenmessung entnommen.
        :type phase_versatz: int
        :type bereich_min: float
        :type bereich_max: float
        :type amp: Fitparameter
        :type amp_min: float
        :type amp_max: float
        :type phase: Fitparameter
        :type konf: SpeckView.BE.Konfiguration.Konfiguration
        ;:type version: int
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
        """ Anzahl der Mittelungen pro Rasterpunkt """
        self.nr_fkt_amp = amp_fitfkt
        """ Zum Fitten der Amplitude in Abhängigkeit zur Phase für jede einzelne Messung verwendete Funktion """
        self.nr_fkt_ph = ph_fitfkt
        """ Fitfunktion für die Phase """
        self.filter_breite = filter_breite
        """ Breite des Filterfensters """
        self.filter_ordnung = filter_ordnung
        """ Ordnung des Filterpolynoms """
        self.phase_versatz = phase_versatz
        """ Die Phase wird diesen Versatz in Hz neben der Resonanzfrequenz der Phasenauswertung entnommen """

        self.konf = konf
        """ Konfigurationseinstellungen """
        self.version = version
        """ Version des Speicherformats (0, 1: zeilenweise getrennt, 2: kombiniert) """

        self.df = df
        """ Abstand der Messwerte auf der Frequenzskala in Hz """
        self.messpunkte = int((fmax - fmin) // df)
        """ Anzahl der Messpunkte bezüglich der Freqzenz """

        self.bereich_links = int((bereich_min - fmin) // df)
        """ Linker Rand in Messpunkten für Fitbereich """
        self.bereich_rechts = int((bereich_max - fmax) // df)
        """ Rechter Rand in Messpunkten des Fitbereichs (negativ) """


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
