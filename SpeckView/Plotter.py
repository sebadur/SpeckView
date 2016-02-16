# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas
from matplotlib.figure import Figure


class Plotter(FigureCanvas):
    def __init__(self, statusbar, xlabel, ylabel, width=500, height=500, dpi=75):
        """
        :type statusbar: gtk.Statusbar
        :type xlabel: str
        :type ylabel: str
        :type width: int
        :type height: int
        :type dpi: int
        """
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.figure.add_subplot(111, xlabel=xlabel, ylabel=ylabel)
        """ :type: matplotlib.axes.Axes """
        self.axes.hold(False)
        FigureCanvas.__init__(self, self.figure)
        self.statusbar = statusbar
        self.mpl_connect('motion_notify_event', self.maus_bewegt)

    def maus_bewegt(self, event):
        """
        :type event: matplotlib.backend_bases.MouseEvent
        """
        if event.inaxes is not None:
            self.statusbar.pop(0)
            self.statusbar.push(0, str(event.xdata) + "|" + str(event.ydata))
        else:
            self.statusbar.pop(0)

    def plot(self, x, y):
        """
        :type y: list
        :type x: list
        """
        self.axes.plot(x, y, antialiased=True)
        self.draw()
