# coding=utf-8
"""
@author: Valon Lushta
@author: Sebastian Badur
"""

import numpy as np


in_grad = 180 / np.pi


# AMPLITUDE:

def resonance_lorentz(freq, resfreq, amp, guete, untergrund):
    """
    :type freq: float
    :type resfreq: float
    :type amp: float
    :type guete: float
    :type untergrund: float
    :return: Lorentzverteilung für den Cantilever
    :rtype: float
    """
    return amp * resfreq**2 / (
        guete * np.sqrt((freq**2 - resfreq**2)**2 + (freq * resfreq / guete)**2)
    ) + untergrund


def drive_lorentz(freq, resfreq, amp, guete, untergrund):
    """
    :type freq: float
    :type resfreq: float
    :type amp: float
    :type guete: float
    :type untergrund: float
    :return: Lorentzverteilung für das antreibende System
    :rtype: float
    """
    return amp * resfreq**2 / np.sqrt(
        (freq**2 - resfreq**2) ** 2 + (freq * resfreq / guete)**2
    ) + untergrund


fkt_amp = [
    resonance_lorentz,
    drive_lorentz
]


# PHASE:

def phase_lorentz(freq, resfreq, guete, rel):
    """
    :type freq: float
    :type resfreq: float
    :type guete: float
    :type rel: float
    :return: Phase in Grad
    :rtype: float
    """
    return (in_grad * np.arctan(
        resfreq * freq / (guete * (resfreq**2 - freq**2))
    ) + rel) % 360 - 180


def phase_aghr(freq, resfreq, guete, rel):
    """
    :type freq: float
    :type resfreq: float
    :type guete: float
    :type rel: float
    :return: Phase in Grad nach T. R. Albrecht, P. Grutter, D. Horne, D. Rugar, J. Appl. Phys., 1991, 69, 668–673.
    :rtype: float
    """
    return (in_grad * np.arctan(
        5 * guete * (freq / resfreq - resfreq / freq)
    ) + rel) % 360 - 180


def phase_phenom(freq, resfreq, guete, rel):
    """
    :type freq: float
    :type resfreq: float
    :type guete: float
    :type rel: float
    :return: Phase in Grad
    :rtype: float
    """
    return (in_grad * np.arctan(
        (resfreq - freq) / (500 * guete)
    ) + rel) % 360 - 180


fkt_ph = [
    phase_lorentz,
    phase_aghr,
    phase_phenom,
    None
]
