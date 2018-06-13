# coding=utf-8
"""
@author: Sebastian Badur
@author: Valon Lushta
"""

import os
import numpy
from lmfit import Parameters, Model
from scipy.signal import savgol_filter
from multiprocessing import Pool

from SpeckView.Sonstige import int_max

from Ergebnis import Ergebnis
from FitFunktion import fkt_amp, fkt_ph, fkt_filter, KEIN_FIT, GLAETTEN
from Parameter import index_freq, frequenzen


class Fit:
    def __init__(self, par, amplitude_voll, phase_voll, puls):
        """
        :type par: SpeckView.BE.Parameter.Parameter
        :type amplitude_voll: numpy.multiarray.ndarray
        :type phase_voll: numpy.multiarray.ndarray
        :type puls: (int) -> None
        """
        self.par = par
        self.amplitude_voll = amplitude_voll
        self.phase_voll = phase_voll
        self.puls = puls
        self.frequenz = frequenzen(par)

    def _belegen(self):
        global _instanz
        if _instanz is not self:
            _instanz = self
            global _par, _amplitude_voll, _phase_voll, _frequenz, _mod_amp, _mod_ph, _puls, _weiter
            _par = self.par
            _amplitude_voll = self.amplitude_voll
            _phase_voll = self.phase_voll
            _frequenz = self.frequenz
            _mod_amp = Model(fkt_amp[self.par.nr_fkt_amp])
            try:
                _mod_ph = Model(fkt_ph[self.par.nr_fkt_ph])
            except TypeError:
                _mod_ph = fkt_ph[self.par.nr_fkt_ph]
            _puls = self.puls
            _weiter = True

    def start(self):
        """
        Startet den Fit. Alle Zuweisungen wurden durch den Konstruktor vorgenommen.
        :return: Gefittete Amplitude und gefittete oder geglättete Phase im Bereich um Resonanzfrequenz +/- Versatz
        :rtype: multiprocessing.pool.AsyncResult
        """
        self._belegen()
        if hasattr(os, 'fork'):  # Multiprozessierung, wenn möglich
            return Pool().map_async(_fit_punkt, range(_par.spektren))
        else:  # Windows (langsamer)
            dat = map(_fit_punkt, range(_par.spektren))
            class AsyncResult:
                pass
            erg = AsyncResult()
            erg.get = lambda: dat
            erg.ready = lambda: True
            return erg

    def vorschau(self, n):
        """
        :type n: int
        :rtype: Ergebnis
        """
        self._belegen()
        return _fit_punkt(n)

    @staticmethod
    def stopp():
        """
        Bricht den Fit möglichst bald ab.
        """
        global _weiter
        _weiter = False


_instanz = None
""" :type: Fit """
_weiter = True
_puls = None
""" :type: (int) -> None """

_fit_genauigkeit = {
    'ftol': 1e-9,  # Geringe Toleranzen
    'xtol': 1e-9,
    'gtol': 1e-9,
    'maxfev': int_max,  # Maximale Iterationsanzahl
    'factor': 0.1  # Kleinster möglicher Schrittwert für die leastsq-Methode
}

_amplitude_voll = []
_phase_voll = []
_frequenz = None
""" :type: numpy.multiarray.ndarray """
_par = None
""" :type: SpeckView.BE.Parameter.Parameter """
_mod_amp = None
""" :type: Model """
_mod_ph = None
""" :type: Model """


def _bereich(feld):
    """
    :type feld: numpy.multiarray.ndarray
    :rtype: numpy.multiarray.ndarray
    """
    if _par.bereich_rechts == 0:
        return feld[_par.bereich_links:]
    else:
        return feld[_par.bereich_links:_par.bereich_rechts]


def _amp_gefiltert(n):
    """
    :type n: int
    :rtype: numpy.multiarray.ndarray
    """
    amplitude = fkt_filter[_par.nr_fkt_filter](_bereich(_amplitude_voll[n]), _par.filter_breite, _par.filter_ordnung)
    a1 = _par.linkorr_a1
    a2 = _par.linkorr_a2
    if a1 != a2:
        s = (a2 - a1) / float(amplitude.size)
        amplitude -= numpy.arange(a1, a2, s)
    return amplitude


def _fit_punkt(n):
    """
    :type n: int
    :return: Gefittete Amplitude und gefittete oder geglättete Phase im Bereich um Resonanzfrequenz +/- Versatz
    :rtype: list
    """
    if not _weiter:
        return None

    # ----------------------------------------
    # ----------- AMPLITUDE fitten -----------
    # ----------------------------------------

    amplitude = _amp_gefiltert(n)
    index_max = numpy.argmax(amplitude)
    start_freq = _frequenz[index_max]
    start_amp = amplitude[index_max]
    start_off = amplitude[0]  # Erster betrachteter Wert ist bereits eine gute Näherung für den Untergrund

    # Fitparameter für die Fitfunktion
    par_amp = Parameters()
    par_amp.add('resfreq', value=start_freq, min=_par.fmin, max=_par.fmax)
    par_amp.add('amp', value=start_amp, min=_par.amp_min, max=_par.amp_max)
    par_amp.add(
        'guete',
        value=0.5*(_par.amp.guete_max + _par.amp.guete_min),
        min=_par.amp.guete_min,
        max=_par.amp.guete_max
    )
    par_amp.add('untergrund', value=start_off, min=_par.amp.off_min, max=_par.amp.off_max)

    amp = _mod_amp.fit(
        data=amplitude,
        freq=_frequenz,
        params=par_amp,
        fit_kws=_fit_genauigkeit
    )

    _puls(n)
    # Wenn keine Phase gefittet werden soll:
    if _mod_ph is KEIN_FIT:
        return Ergebnis(
            amp=amp.params['amp'].value,
            amp_fhlr=amp.params['amp'].stderr,
            resfreq=amp.params['resfreq'].value,
            resfreq_fhlr=amp.params['resfreq'].stderr,
            guete_amp=amp.params['guete'].value,
            guete_amp_fhlr=amp.params['guete'].stderr,
            untergrund=amp.best_values['untergrund']
        )

    # Resonanzfrequenz
    resfreq = amp.best_values['resfreq']

    # ----------------------------------------
    # ------------- PHASE fitten -------------
    # ----------------------------------------

    halb = abs(_par.phase_versatz) + 10 * _par.df  # Halbe Frequenzbreite des Phasenversatzes
    # +df, weil der Fit auch bei Versatz = 0 funktionieren muss
    von = resfreq - halb  # Untere Versatzgrenze
    bis = resfreq + halb  # Obere Versatzgrenze

    if von < _par.fmin:  # Die Resonanzfrequenz liegt zu weit links:
        # Auswahlbereich nach rechts verschieben, aber nicht über den Frequenzbereich hinaus
        bis = min(bis - von + _par.fmin, _par.fmax)
        von = _par.fmin
    elif bis > _par.fmax:  # Die Resonanz lieg zu weit rechts:
        von = max(von - bis + _par.fmax, _par.fmin)  # Verschieben, aber nicht über linken Rand hinaus
        bis = _par.fmax

    # Phase beschneiden
    index_von = index_freq(_par, von)
    index_bis = index_freq(_par, bis)
    wahl_phase = _bereich(_phase_voll[n])[index_von:index_bis]

    if _mod_ph is GLAETTEN:  # Nur glätten:
        phase = savgol_filter(wahl_phase, 15, 3)  # TODO wählbar
        return Ergebnis(
            amp=amp.params['amp'].value,
            amp_fhlr=amp.params['amp'].stderr,
            resfreq=amp.params['resfreq'].value,
            resfreq_fhlr=amp.params['resfreq'].stderr,
            guete_amp=amp.params['guete'].value,
            guete_amp_fhlr=amp.params['guete'].stderr,
            untergrund=amp.best_values['untergrund'],
            phase=randwert(phase, _par.phase_versatz)
        )

    else:
        # Fitparameter für die Fitfunktion
        par_ph = Parameters()
        par_ph.add('resfreq', value=resfreq, min=von, max=bis)
        par_ph.add('guete', value=3, min=_par.phase.guete_min, max=_par.phase.guete_max)
        par_ph.add('rel', value=200, min=_par.phase.off_min, max=_par.phase.off_max)

        ph = _mod_ph.fit(
            data=wahl_phase,
            freq=_frequenz[index_von:index_bis],
            params=par_ph,
            method='cg'  # 'differential_evolution' passt auch gut
            # TODO fit_kws=self.fit_genauigkeit
        )

        return Ergebnis(
            amp=amp.params['amp'].value,
            amp_fhlr=amp.params['amp'].stderr,
            resfreq=amp.params['resfreq'].value,
            resfreq_fhlr=amp.params['resfreq'].stderr,
            guete_amp=amp.params['guete'].value,
            guete_amp_fhlr=amp.params['guete'].stderr,
            untergrund=amp.best_values['untergrund'],
            phase=randwert(ph.best_fit, _par.phase_versatz),
            guete_ph=ph.best_values['guete'],
            phase_rel=ph.best_values['rel'],
            phase_fhlr=ph.params['resfreq'].stderr
        )


def randwert(phase, versatz):
    """
    :type phase: numpy.multiarray.ndarray
    :type versatz: int
    """
    if versatz < 0:
        return phase[0]
    elif _par.phase_versatz > 0:
        return phase[-1]
    else:
        return phase[len(phase) // 2]
