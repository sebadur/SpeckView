# coding=utf-8
"""
@author: Sebastian Badur
"""

from Parameter import frequenzen
from FitFunktion import fkt_amp


class Ergebnis:
    def __init__(self, amp, phase, resfreq, guete, untergrund):
        """
        :type amp: float
        :type phase: float
        :type resfreq: float
        :type guete: float
        :type untergrund: float
        :type resfreq: float
        :type guete: float
        """
        self.amp = amp
        self.phase = phase
        self.resfreq = resfreq
        self.guete = guete
        self.untergrund = untergrund


def amp_verlauf(par, erg):
    """
    :type par: SpeckView.BE.Parameter.Parameter
    :type erg: Ergebnis
    :rtype: list[float]
    """
    return [
        fkt_amp[par.nr_fkt_amp](freq, erg.resfreq, erg.amp, erg.guete, erg.untergrund)
        for freq in frequenzen(par)
    ]
