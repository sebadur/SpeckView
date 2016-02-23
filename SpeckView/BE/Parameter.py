# coding=utf-8
"""
@author: Sebastian Badur
"""

from lmfit import Model

from SpeckView.Sonstige import Fehler


class Parameter:
    """ Alle für den Fit einer Rastermessung nötigen Messparameter """
    def __init__(self, fmin, fmax, df, pixel, mittelungen, amp_fitfkt, ph_fitfkt, filter_fkt,
                 phase_versatz, bereich_links, bereich_rechts, amp, amp_min, amp_max, phase, konf, pfad):
        """
        :type fmin: int
        :type fmax: int
        :type df: int
        :type pixel: int
        :type mittelungen: int
        :param amp_fitfkt: Mit den Parametern Frequenz, Resonanzfrequenz, Amplitude, Güte und Offset
        :type amp_fitfkt: (float, float, float, float, float) -> float
        :param ph_fitfkt: Fitmethodik für die Phase
        :type ph_fitfkt: (float, float, float, float) -> float
        :param filter_fkt: Die zur Glättung der Messdaten zu verwendende Filterfunktion
        :type filter_fkt: (list) -> list
        :param phase_versatz: Die zur Resonanz gehörige Phase wird diese Anzahl an Messpunkten neben der
        Resonanzfrequenz aus der geglätteten Phasenmessung entnommen.
        :type phase_versatz: int
        :param bereich_links: Die Anzahl der zu entfernenden niedrigen Frequenzen
        :type bereich_links: int
        :param bereich_rechts: Die Anzahl der zu entfernenden hohen Frequenzen
        :type bereich_rechts: int
        :type amp: Fitparameter
        :type amp_min: float
        :type amp_max: float
        :type phase: Fitparameter
        :type konf: SpeckView.BE.Konfiguration.Konfiguration
        :type pfad: str
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

        self.fmin = fmin + bereich_links * df
        """ Anfangsfrequenz des Spektrums der Bandanregung im gewählten Frequenzbereich in Hz """
        self.fmax = fmax - bereich_rechts * df
        """ Endfrequenz des Spektrums der Bandanregung im gewählten Frequenzbereich in Hz """
        self.pixel = pixel
        """ Pixelgröße des (quadratischen) Messbereichs """
        self.mittelungen = mittelungen
        """ Anzahl der Mittelungen pro Rasterpunkt """
        self.mod_amp = Model(amp_fitfkt)
        """ Zum Fitten der Amplitude in Abhängigkeit zur Phase für jede einzelne Messung verwendete Funktion """
        self.mod_ph = Model(ph_fitfkt)
        """ Fit-Model für die Phase """
        self.filter = filter_fkt
        """ Die Funktion zum Glätten der Messdaten """
        self.phase_versatz = phase_versatz
        """ Die Phase wird diese Anzahl an Messpunkten neben der Resonanzfrequenz der Phasenauswertung entnommen """
        self.bereich_links = bereich_links
        """ Linker Rand für Fitbereich """
        self.bereich_rechts = -(bereich_rechts + 1)
        """ Rechter Rand des Fitbereichs """

        self.konf = konf
        """ Konfigurationseinstellungen """
        self.pfad = pfad
        """ Stammverzeichnis der Messdateien """

        self.df = df
        """ Abstand der Messwerte auf der Frequenzskala in Hz """
        self.messpunkte = int((fmax - fmin) // df)
        """ Anzahl der Messpunkte bezüglich der Freqzenz """

    def index_freq(self, freq):
        """
        :type freq: float
        :return: Index der Frequenz innerhalb des beschränkten Frequenzbereichs
        :rtype: int
        """
        return int((freq - self.fmin) // self.df)


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
