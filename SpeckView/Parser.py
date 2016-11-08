# coding=utf-8
"""
@author: Sebastian Badur
"""

from ConfigParser import ConfigParser, NoSectionError, NoOptionError


class DefaultParser(ConfigParser):
    def __init__(self):
        ConfigParser.__init__(self)

    def getboolean(self, section, option):
        try:
            return ConfigParser.getboolean(self, section, option)
        except NoOptionError:
            return False

    def getint(self, section, option):
        try:
            return ConfigParser.getint(self, section, option)
        except NoOptionError:
            return 0

    def getfloat(self, section, option):
        try:
            # Komma und Punkt als Dezimaltrennzeichen erlauben (keine Tausendertrennzeichen):
            return float(self.get(section, option).replace(',', '.'))
        except (NoSectionError, NoOptionError):
            return 0.0
