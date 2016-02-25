# coding=utf-8
"""
@author: Sebastian Badur
"""

# noinspection PyUnresolvedReferences
import gwy
from ctypes import c_double


def volume_data(c, inhalt, einheit_xy, einheit_z,
                dim, pixel, dim_y=0, pixel_y=0,
                titel=None):
    """
    :type c: gwy.Container
    :type inhalt: list
    :type einheit_xy: gwy.SIUnit
    :type einheit_z: gwy.SIUnit
    :type dim: float
    :type pixel: int
    :param dim_y: Wenn die Dimension von x und y verschieden sind
    :type dim_y: int
    :param pixel_y: Für nicht quadratische Datenfelder
    :type pixel_y: int
    :type titel: str
    """
    if pixel_y == 0:
        pixel_y = pixel
    if dim_y == 0:
        dim_y = dim

    # Neues, nicht initialisiertes Datenfeld erstellen:
    vd = gwy.DataField(pixel, pixel_y, dim, dim_y, False)
    vd.set_si_unit_xy(einheit_xy)
    vd.set_si_unit_z(einheit_z)

    # Belegen:
    c_feld = c_double * (pixel * pixel_y)
    zgr = c_feld.from_address(vd.get_data_pointer())
    zgr[:] = inhalt

    if not hasattr(c, 'n_sd'):
        c.n_sd = 0
    name = '/' + str(c.n_sd) + '/data'
    c.set_object_by_name(name, vd)
    if titel is not None:
        c.set_string_by_name(name + '/title', titel)
    c.n_sd += 1


def si_unit(einheit):
    """
    :type einheit: str
    :rtype: gwy.SIUnit
    """
    si = gwy.SIUnit()
    si.set_from_string(einheit)
    return si


def set_custom(c, obj):
    """
    :type c: gwy.Container
    """
    anz = 1
    brick = gwy.Brick(1, 1, anz, 1, 1, 1, False)
    c_feld = c_double * anz

    c.set_object_by_name('/custom', brick)


def get_custom(c):
    """
    :type c: gwy.Container
    """
    c.get_object_by_name('/custom')

# wnd = gwy_app_find_window_for_channel(gwy_app_data_browser_get_containers()[0],-1).get_window()
