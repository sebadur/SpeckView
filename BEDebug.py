# coding=utf-8
"""
@author: Sebastian Badur
"""

import unittest

import gwy

plugin_type = 'PROCESS'
plugin_desc = "Debugfunktionen"
plugin_menu = "/Bandanregung/Debug"


def run():
    pass


pfad = "/home/sebadur/Dokumente/BaTiO3/2016-11-04/Messungen/"
messung = pfad + "16-11-04-14-08-09.be"
tdms = [
    pfad + "amp0.tdms",
    pfad + "amp1.tdms",
    pfad + "amp2.tdms",
    "A.ber doch nicht so!"
]


class DebugTest(unittest.TestCase):
    def test_name(self):
        import BELaden
        self.assertEqual(BELaden.detect_by_name(messung), 100)
        for datei in tdms:
            self.assertEqual(BELaden.detect_by_name(datei), 0)

    def test_inhalt(self):
        import BELaden
        self.assertEqual(BELaden.detect_by_content(messung, "", "", 0), 100)
        for datei in tdms:
            self.assertEqual(BELaden.detect_by_content(datei, "", "", 0), 0)

    def test_format(self):
        from SpeckView import Format
        from SpeckView.BE.Ergebnis import Ergebnis
        c = gwy.Container()
        debug = "debug"
        original = [Ergebnis(3, 5, 7, 11, 1, 1, 1)]
        Format.set_custom(c, debug, original)
        resultat = Format.get_custom(c, debug)
        """ :type: list[Ergebnis.Ergebnis] """
        self.assertEqual(len(resultat), len(original))
        for n in range(len(original)):
            alt = original[n]
            neu = resultat[n]
            self.assertEqual(neu.amp, alt.amp)
            self.assertEqual(neu.resfreq, alt.resfreq)
            self.assertEqual(neu.guete_amp, alt.guete_amp)
            self.assertEqual(neu.untergrund, alt.untergrund)

    def test_fit(self):
        from SpeckView.BE.Fit import Fit
        from SpeckView.BE.Parameter import Parameter, Fitparameter
        import numpy
        fit = Fit(
            Parameter(
                fmin=47000, fmax=64000, df=1000,
                raster=True, pixel=1, dim=0.000001,
                mittelungen=100,
                amp_fitfkt=0, ph_fitfkt=3, filterfkt=0,
                filter_breite=5, filter_ordnung=2,
                linkorr_a1=0.0, linkorr_a2=0.0, antipeaks="",
                phase_versatz=1000, phase_referenz=0,
                bereich_min=47000, bereich_max=64000,
                amp=Fitparameter(0.001, 1000, 0, 10),
                amp_min=0.001, amp_max=1000,
                f0_phase=True,
                phase=Fitparameter(0.00, 1000, 0, 1000),
                spektroskopie=False, hysterese=False, punkte=0, dcmax=0, dcmin=0, ddc=0,
                konf='', kanal='elstat', version=3
            ),
            numpy.array([[0, 0, 0, 0, 0, 1, 1, 5, 10, 5, 1, 1, 0, 0, 0, 0, 0]]),
            numpy.array([[180, 180, 180, 180, 179, 175, 174, 90, 0, -90, -174, -175, -179, -180, -180, -180, -180]]),
            lambda (n): None
        ).vorschau(0)
        self.assertAlmostEqual(fit.amp, 10, delta=1)
        self.assertAlmostEqual(fit.guete_amp, 78, delta=2)
        self.assertAlmostEqual(fit.phase, -180, delta=45)
        self.assertAlmostEqual(fit.resfreq, 55000, delta=500)
        self.assertAlmostEqual(fit.untergrund, 0)

    def test_gui(self):
        import BELaden
        BELaden.load(messung, gwy.RUN_NONINTERACTIVE)
        BELaden.load(messung, gwy.RUN_INTERACTIVE)
