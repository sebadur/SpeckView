# coding=utf-8
"""
@author: Sebastian Badur
@author: Valon Lushta
"""

import numpy
from lmfit import Parameters
from multiprocessing import Pool

from SpeckView.Sonstige import int_max, Nichts

from Ergebnis import Ergebnis


class Fit:
    def __init__(self, par, amplitude_komplett, phase_komplett, frequenz, puls):
        """
        :type par: SpeckView.BE.Parameter.Parameter
        :type amplitude_komplett: numpy.multiarray.ndarray
        :type phase_komplett: numpy.multiarray.ndarray
        :type frequenz: numpy.multiarray.ndarray
        :type puls: () -> None
        """
        self.par = par
        self.amplitude_komplett = amplitude_komplett
        self.phase_komplett = phase_komplett
        self.puls = puls
        global _par
        _par = par
        self.frequenz = _bereich(frequenz)  # Vorsicht wegen Abhängigkeiten (_par)

    def _belegen(self):
        global _instanz
        if _instanz is not self:
            _instanz = self
            global _par, _amplitude_komplett, _phase_komplett, _frequenz, _puls, _weiter
            _par = self.par
            _amplitude_komplett = self.amplitude_komplett
            _phase_komplett = self.phase_komplett
            _frequenz = self.frequenz
            _puls = self.puls
            _weiter = True

    def start(self):
        """
        Startet den Fit. Alle Zuweisungen wurden durch den Konstruktor vorgenommen.
        :return: Gefittete Amplitude und gefittete oder geglättete Phase im Bereich um Resonanzfrequenz +/- Versatz
        :rtype: list[Ergebnis]
        """
        self._belegen()
        return Pool().map(_fit_punkt, range(_par.pixel ** 2))

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
""" :type: () -> None """

_fit_genauigkeit = {
    'ftol': 1e-9,  # Geringe Toleranzen
    'xtol': 1e-9,
    'gtol': 1e-9,
    'maxfev': int_max,  # Maximale Iterationsanzahl
    'factor': 0.1  # Kleinster möglicher Schrittwert für die leastsq-Methode
}

_amplitude_komplett = []
_phase_komplett = []
_frequenz = None
""" :type: numpy.multiarray.ndarray """
_par = None
""" :type: SpeckView.BE.Parameter.Parameter """


def _bereich(feld):
    """
    :type feld: numpy.multiarray.ndarray
    :rtype: numpy.multiarray.ndarray
    """
    return feld[_par.bereich_links:_par.bereich_rechts]


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

    amplitude = _par.filter(_bereich(_amplitude_komplett[n]))
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

    amp = _par.mod_amp.fit(
        data=amplitude,
        freq=_frequenz,
        params=par_amp,
        fit_kws=_fit_genauigkeit
    )
    # Resonanzfrequenz
    resfreq = amp.best_values['resfreq']

    #puls()
    return Ergebnis(
        amp=amp.best_values['amp'],
        phase=0,
        resfreq=amp.best_values['resfreq'],
        guete=amp.best_values['guete'],
        untergrund=amp.best_values['untergrund'],
        amp_fkt=_par.fkt_amp,
        phase_fkt=_par.fkt_ph,
        frequenzen=_frequenz
    )

    # ----------------------------------------
    # ------------- PHASE fitten -------------
    # ----------------------------------------

    halb = abs(_par.phase_versatz) * _par.df  # Halbe Frequenzbreite des Phasenversatzes
    von = resfreq - halb  # Untere Versatzgrenze
    bis = resfreq + halb  # Obere Versatzgrenze

    if von < _par.fmin:  # Die Resonanzfrequenz liegt zu weit links:
        # Auswahlbereich nach rechts verschieben, aber nicht über den Frequenzbereich hinaus
        bis = min(bis - von + _par.fmin, _par.fmax)
        von = _par.fmin
    elif bis > _par.fmax:  # Die Resonanz lieg zu weit rechts:
        von = max(von - bis + _par.fmax, _par.fmin)  # Verschieben, aber nicht über linken Rand hinaus
        bis = _par.fmax

    # Phase und Frequenz beschneiden
    index_von = _par.index_freq(von)
    index_bis = _par.index_freq(bis)
    wahl_phase = _bereich(_phase_komplett[n])[index_von:index_bis]
    wahl_frequenz = _frequenz[index_von:index_bis]

    # Fitparameter für die Fitfunktion
    par_ph = Parameters()
    par_ph.add('resfreq', value=resfreq, min=von, max=bis)
    par_ph.add('guete', value=3, min=_par.phase.guete_min, max=_par.phase.guete_max)
    par_ph.add('phase', value=200, min=_par.phase.off_min, max=_par.phase.off_max)

    if _par.mod_ph is not None:
        ph = _par.mod_ph.fit(
            data=wahl_phase,
            freq=wahl_frequenz,
            params=par_ph,
            method='cg'  # 'differential_evolution' passt auch gut
            # TODO fit_kws=self.fit_genauigkeit
        )
    else:
        ph = Nichts()
        ph.best_fit = _par.filter(wahl_phase)
        ph.chisqr = 0  # TODO

    # Zusätzliche Informationen für den Phasenfit:
    if _par.phase_versatz < 0:
        ph.mit_versatz = ph.best_fit[0]
    elif _par.phase_versatz > 0:
        ph.mit_versatz = ph.best_fit[-1]
    else:
        ph.mit_versatz = ph.best_fit[len(ph.best_fit) // 2]
    ph.frequenzen = wahl_frequenz

    return amp, ph
