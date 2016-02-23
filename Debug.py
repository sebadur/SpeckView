# coding=utf-8
"""
@author: Sebastian Badur
"""

import gwy
plugin_type = 'PROCESS'
plugin_desc = ""
plugin_menu = ""


def run():
    pass


if __name__ == '__main__':
    import BERaster
    BERaster.DEBUG = True
    messung = "/home/sebadur/Dokumente/BE-Raster/20160217-img008/konfig.ber"
    print "Name: " + str(BERaster.detect_by_name(messung))
    print "Inhalt: " + str(BERaster.detect_by_content(messung, "", "", 0))
    BERaster.load(messung, gwy.RUN_INTERACTIVE)
