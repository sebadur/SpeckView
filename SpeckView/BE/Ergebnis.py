# coding=utf-8
"""
@author: Sebastian Badur
"""


class Ergebnis:
    def __init__(self, amp, phase, resfreq, guete, untergrund, amp_fkt, phase_fkt, frequenzen):
        """
        :type amp: float
        :type phase: float
        :type resfreq: float
        :type guete: float
        :type untergrund: float
        :type resfreq: float
        :type guete: float
        :type amp_fkt: (amp=float, float, float, float) -> float
        :type phase_fkt: (amp=float, float, float, float) -> float
        :type frequenzen: numpy.multiarray.ndarray
        """
        self.amp = amp
        self.phase = phase
        self.resfreq = resfreq
        self.guete = guete
        self.untergrund = untergrund
        self.amp_fkt = amp_fkt
        self.phase_fkt = phase_fkt
        self.frequenzen = frequenzen

    def amp_verlauf(self):
        """
        :rtype: list[float]
        """
        return [
            self.amp_fkt(freq, self.resfreq, self.amp, self.guete, self.untergrund)
            for freq in self.frequenzen
        ]
