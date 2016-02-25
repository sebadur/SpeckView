# coding=utf-8
"""
@author: Sebastian Badur
"""

# noinspection PyUnresolvedReferences
import gwy
from ctypes import c_double


class Container(gwy.Container):
    def __init__(self):
        gwy.Container.__init__(self)
        self.n_sd = 0

    def volume_data(self, inhalt, dim, pixel, dim_y=0, pixel_y=0,
                    titel=None):
        """
        :type inhalt: list
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

        # Belegen:
        c_feld = c_double * (pixel * pixel_y)
        zgr = c_feld.from_address(vd.get_data_pointer())
        zgr[:] = inhalt

        name = '/' + str(self.n_sd) + '/data'
        self.set_object_by_name(name, vd)
        if titel is not None:
            self.set_string_by_name(name + '/title', titel)
        self.n_sd += 1

# wnd = gwy_app_find_window_for_channel(gwy_app_data_browser_get_containers()[0],-1).get_window()
