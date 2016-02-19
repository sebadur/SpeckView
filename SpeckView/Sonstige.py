# coding=utf-8
"""
@author: Sebastian Badur
"""


int_max = 2**31-1
""" Größter 32-Bit int-Wert """
int_min = -2**31
""" Kleinster 32-Bit in-Wert """


class Nichts:
    def __init__(self):
        pass


class Fehler(Exception):
    pass
