# coding=utf-8
"""
@author: Sebastian Badur
"""


class Kompendium:
    def __init__(self, erg, par, amplitude, phase):
        """
        :param erg: SpeckView.BE.Ergebnis.Ergebnis
        :param par: SpeckView.BE.Parameter.Parameter
        :param amplitude: list
        :param phase: list
        """
        self.erg = erg
        self.par = par
        self.amplitude = amplitude
        self.phase = phase
