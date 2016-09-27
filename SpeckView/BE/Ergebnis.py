# coding=utf-8
"""
@author: Sebastian Badur
"""

from numpy import NaN

from Parameter import frequenzen
from FitFunktion import fkt_amp, fkt_ph


class Ergebnis:
    def __init__(self, amp, resfreq, guete_amp, untergrund,
                 amp_fhlr, resfreq_fhlr, guete_amp_fhlr, phase_fhlr=NaN,
                 phase=NaN, guete_ph=NaN, phase_rel=NaN):
        """
        :type amp: float
        :type phase: float
        :type resfreq: float
        :type guete_amp: float
        :type untergrund: float
        :type resfreq: float
        :type guete_ph: float
        :type phase_rel: float
        :type amp_fhlr: float
        :type resfreq_fhlr: float
        :type guete_amp_fhlr: float
        :type phase_fhlr: float
        """
        self.amp = amp
        self.phase = phase
        self.resfreq = resfreq
        self.guete_amp = guete_amp
        self.guete_ph = guete_ph
        self.untergrund = untergrund
        self.phase_rel = phase_rel
        self.amp_fhlr = amp_fhlr
        self.resfreq_fhlr = resfreq_fhlr
        self.guete_amp_fhlr = guete_amp_fhlr
        self.phase_fhlr = phase_fhlr


def amp_verlauf(par, erg):
    """
    :type par: SpeckView.BE.Parameter.Parameter
    :type erg: Ergebnis
    :rtype: list[float]
    """
    return [
        fkt_amp[par.nr_fkt_amp](freq, erg.resfreq, erg.amp, erg.guete_amp, erg.untergrund)
        for freq in frequenzen(par)
    ]


def phase_verlauf(par, erg):
    """
    :type par: SpeckView.BE.Parameter.Parameter
    :type erg: Ergebnis
    :rtype: list[float]
    """
    fkt = fkt_ph[par.nr_fkt_ph]
    if type(fkt) is int:
        return None
    else:
        return [
            fkt(freq, erg.resfreq, erg.guete_amp, erg.phase_rel)
            for freq in frequenzen(par)
        ]
