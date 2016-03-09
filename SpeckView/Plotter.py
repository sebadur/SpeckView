# coding=utf-8
"""
@author: Sebastian Badur
"""

import gtk
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
from matplotlib.figure import Figure


class Plotter(gtk.VBox):
    def __init__(self, xlabel, ylabel, width=500, height=500, dpi=75):
        """
        :type xlabel: str
        :type ylabel: str
        :type width: int
        :type height: int
        :type dpi: int
        """
        gtk.VBox.__init__(self)
        figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = figure.add_subplot(111, xlabel=xlabel, ylabel=ylabel)
        """ :type: matplotlib.axes.Axes """
        self.axes.hold(False)
        self.canvas = FigureCanvas(figure)
        nav = NavigationToolbar(self.canvas, self)
        self.pack_start(nav, False, False)
        self.pack_start(self.canvas)

    def leeren(self):
        self.axes.hold(False)

    def plot(self, x, y, **args):
        self.axes.plot(x, y, antialiased=True, **args)
        self.axes.hold(True)

    def draw(self):
        self.canvas.draw()
