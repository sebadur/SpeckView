# coding=utf-8
"""
@author: Sebastian Badur
"""

from os import path


class Konfiguration:
    def __init__(self, datei):
        """
        :type datei: str
        """
        self.datei = datei  # TODO path.relpath(datei)
        self.pfad = path.dirname(datei)

        self.format = 1
        self.konfig = 'konfig'
        self.df = 'df'
        self.mittelungen = 'mittelungen'
        self.fmin = 'fmin'
        self.fmax = 'fmax'
        self.gruppe = 'Unbenannt'  # 'Untitled'
        self.kanal = 'Untitled'
        self.amp = 'amp'
        self.phase = 'phase'
        self.pixel = 'pixel'
        self.dim = 'dim'
