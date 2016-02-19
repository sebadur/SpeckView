# coding=utf-8
"""
@author: Sebastian Badur
@author: Valon Lushta
"""

import numpy
from lmfit import Parameters
from multiprocessing.dummy import Pool

from SpeckView.Sonstige import int_max, Nichts


class Fit:
    def __init__(self, par):
        """
        :type par: SpeckView.BE.Parameter.Parameter
        """
        self.par = par
        self.fit_genauigkeit = {
            'ftol': 1e-9,  # Geringe Toleranzen
            'xtol': 1e-9,
            'gtol': 1e-9,
            'maxfev': int_max,  # Maximale Iterationsanzahl
            'factor': 0.1  # Kleinster möglicher Schrittwert für die leastsq-Methode
        }
        self.debug = 0

    def fit(self, amplitude, phase, frequenz):
        """
        :type amplitude: numpy.multiarray.ndarray
        :type phase: numpy.multiarray.ndarray
        :type frequenz: numpy.multiarray.ndarray
        :return: Gefittete Amplitude und gefittete oder geglättete Phase im Bereich um Resonanzfrequenz +/- Versatz
        :rtype: list[ModelResult], list[ModelResult]
        """
        frequenz_bereich = self.bereich(frequenz)
        Pool().map(
            lambda n: self._fit_punkt(
                amplitude=self.bereich(amplitude[n]),
                phase=self.bereich(phase[n]),
                frequenz=frequenz_bereich
            ), range(self.par.pixel ** 2)
        )

    def bereich(self, feld):
        """
        :type feld: numpy.multiarray.ndarray
        :rtype: numpy.multiarrayndarray
        """
        return feld[self.par.bereich_links:self.par.bereich_rechts]

    def _fit_punkt(self, amplitude, phase, frequenz):
        """
        :type amplitude: numpy.multiarray.ndarray
        :type phase: numpy.multiarray.ndarray
        :type frequenz: numpy.multiarray.ndarray
        :return: Gefittete Amplitude und gefittete oder geglättete Phase im Bereich um Resonanzfrequenz +/- Versatz
        :rtype: ModelResult, ModelResult
        """
        self.debug += 1
        print self.debug

        par = self.par

        # ----------------------------------------
        # ----------- AMPLITUDE fitten -----------
        # ----------------------------------------

        amplitude = par.filter(amplitude)
        index_max = numpy.argmax(amplitude)
        start_freq = frequenz[index_max]
        start_amp = amplitude[index_max]
        start_off = amplitude[0]  # Erster betrachteter Wert ist bereits eine gute Näherung für den Untergrund

        # Fitparameter für die Fitfunktion
        par_amp = Parameters()
        par_amp.add('resfreq', value=start_freq, min=par.fmin, max=par.fmax)
        par_amp.add('amp', value=start_amp, min=par.amp_min, max=par.amp_max)
        par_amp.add(
            'guete',
            value=0.5*(par.amp.guete_max + par.amp.guete_min),
            min=par.amp.guete_min,
            max=par.amp.guete_max
        )
        par_amp.add('off', value=start_off, min=par.amp.off_min, max=par.amp.off_max)

        amp = par.mod_amp.fit(
            data=amplitude,
            freq=frequenz,
            params=par_amp,
            fit_kws=self.fit_genauigkeit
        )
        # Resonanzfrequenz
        resfreq = amp.best_values['resfreq']

        # ----------------------------------------
        # ------------- PHASE fitten -------------
        # ----------------------------------------

        halb = abs(par.phase_versatz) * par.df  # Halbe Frequenzbreite des Phasenversatzes
        von = resfreq - halb  # Untere Versatzgrenze
        bis = resfreq + halb  # Obere Versatzgrenze

        if von < par.fmin:  # Die Resonanzfrequenz liegt zu weit links:
            # Auswahlbereich nach rechts verschieben, aber nicht über den Frequenzbereich hinaus
            bis = min(bis - von + par.fmin, par.fmax)
            von = par.fmin
        elif bis > par.fmax:  # Die Resonanz lieg zu weit rechts:
            von = max(von - bis + par.fmax, par.fmin)  # Verschieben, aber nicht über linken Rand hinaus
            bis = par.fmax

        # Phase und Frequenz beschneiden
        index_von = par.index_freq(von)
        index_bis = par.index_freq(bis)
        wahl_phase = phase[index_von:index_bis]
        wahl_frequenz = frequenz[index_von:index_bis]

        # Fitparameter für die Fitfunktion
        par_ph = Parameters()
        par_ph.add('resfreq', value=resfreq, min=von, max=bis)
        par_ph.add('guete', value=3, min=par.phase.guete_min, max=par.phase.guete_max)
        par_ph.add('phase', value=200, min=par.phase.off_min, max=par.phase.off_max)

        if par.mod_ph is not None:
            ph = par.mod_ph.fit(
                data=wahl_phase,
                freq=wahl_frequenz,
                params=par_ph,
                method='cg',  # 'differential_evolution' passt auch gut
                fit_kws=self.fit_genauigkeit
            )
        else:
            ph = Nichts()
            ph.best_fit = par.filter(wahl_phase)
            ph.chisqr = 0  # TODO

        # Zusätzliche Informationen für den Phasenfit:
        if par.phase_versatz < 0:
            ph.mit_versatz = ph.best_fit[0]
        elif par.phase_versatz > 0:
            ph.mit_versatz = ph.best_fit[-1]
        else:
            ph.mit_versatz = ph.best_fit[len(ph.best_fit) // 2]
        ph.frequenzen = wahl_frequenz

        return amp, ph
