# coding=utf-8
"""
@author: Sebastian Badur
"""

import gwy
plugin_type = 'FILE'
plugin_desc = "TikZ-Bild mit PNG (.tex)"


def detect_by_name(dateiname):
    if dateiname.endswith(".tex"):
        return 100
    else:
        return 0


def detect_by_content(dateiname, kopf, s, g):
    return 0


def load(dateiname, modus=None):
    return None


def save(daten, dateiname, *args):
    from os.path import basename
    import string
    dateiname = string.rsplit(dateiname, ".tex", 1)[0]

    feld = '/' + str(gwy.gwy_app_data_browser_get_current(gwy.APP_DATA_FIELD_ID))
    zmin = daten.get_double_by_name(feld + '/base/min')
    zmax = daten.get_double_by_name(feld + '/base/max')
    bild = gwy.gwy_app_data_browser_get_current(gwy.APP_DATA_FIELD)
    xmax = bild.get_xreal()

#   titel = daten.get_string_by_name(feld + '/data/title')
    titel = ""

    f = gwy.RGBA(0, 0, 0, 0)
    gradient = gwy.gwy_gradients_get_gradient(daten.get_string_by_name(feld + '/base/palette'))
    gradient.get_color(0, f)
    palette = ""
    n = gradient.get_npoints()
    for i in range(n):
        gradient.get_color(i/float(n-1), f)  # nicht korrekt für unregelmäßige Abstände, aber geht derzeit nicht anders
        palette += "rgb=("+str(f.r)+","+str(f.g)+","+str(f.b)+")"

    xdiv = round(0.3 * xmax, 7)
    xdim = "$" + str(xdiv * 10**6) + "\\,$\\textmu m"
    xdiv = str(xdiv / xmax)

    einheit = bild.get_si_unit_z().get_string(gwy.SI_UNIT_FORMAT_TEX)
    vors = [(10**9, "G"), (10**6, "M"), (10**3, "k"), (10**0, ""),
            (10**-3, "m"), (10**-6, "\\textmu"), (10**-9, "n"), (10**-12, "p"), (10**-15, "f"), (10**-18, "a")]
    for vor in vors:
        zvor = vor
        if zmax > vor[0]:
            break
    zmin = "$%.1f" % (zmin / zvor[0]) + "\\,$" + zvor[1] + einheit
    zmax = "$%.1f" % (zmax / zvor[0]) + "\\,$" + zvor[1] + einheit

    import os
    from platform import system
    if system() == 'Linux':
        gwyddion = '.gwyddion'
    else:
        gwyddion = 'gwyddion'
    sv = os.path.join(os.path.expanduser('~'), gwyddion, 'pygwy', 'SpeckView', 'Export')
    from SpeckView.Export.Export import Export
    tex, cbb, bes, zmax, zmin, dim, xdim = Export(sv).optionen(zmax, zmin, xdim)

    if cbb:
        beschriftung = "\\node[white,anchor=north west]at(.05,.95){\\!\\contour{black}{" + bes + "}};"
    else:
        beschriftung = ""

    if dim:
        dimension = "\\filldraw[draw=black,fill=white,line width=.05em](.05,.05)rectangle+(" + xdiv + ",.25ex)" + \
                    "node[white,pos=.5,inner sep=.5ex,above]{\\contour{black}{" + xdim + "}};"
    else:
        dimension = ""

    if not tex:
        anfang = "\\documentclass[10pt,a4paper]{article}\\pagestyle{empty}\\usepackage[utf8]{inputenc}" + \
                 "\\usepackage[T1]{fontenc}\\usepackage{lmodern}\\usepackage[english]{babel}\\usepackage{amsmath}" + \
                 "\\usepackage{textcomp}\\usepackage[outline]{contour}\\contourlength{.05em}\\usepackage{pgfplots}" + \
                 "\\pgfplotsset{compat=newest}\\newcommand{\\gwywidth}{.5\\textwidth}\\newcommand{\\gwylabel}{}" + \
                 "\\begin{document}\\begin{figure}"
        pfad, name = os.path.split(dateiname)
        temp = os.path.join(pfad, ".speckviewtempdir")
        os.mkdir(temp)
        dat0name = dateiname
        dateiname = os.path.join(temp, name)
        ende = "\\end{figure}\\end{document}"
    else:
        anfang = ""
        ende = ""

    gwy.gwy_file_save(daten, dateiname + ".png", gwy.RUN_NONINTERACTIVE)
    datei = open(dateiname + ".tex", 'w')
    datei.write(
        anfang +
        "\\begin{tikzpicture}[inner sep=0,outer sep=0]\\begin{axis}" +
        "[scale only axis,width=\\gwywidth,title={" + titel + "},xlabel={},ylabel={},point meta min=0,point meta max=1," +
        "colorbar,colorbar/width=1.3em,colorbar style={extra description/.code={" +
        "\\node[white,rotate=90,anchor=west]at(0.5,0){\\:" + zmin + "};" +
        "\\node[black,rotate=90,anchor=east]at(0.5,1){" + zmax + "\\:};" +
        "},major tick length=0,yticklabels={,,}},colorbar shift/.style={xshift=0}," +
        "colormap={gwycolor}{" + palette + "}," +
        "tick style={major tick length=0,xticklabels={,,},yticklabels={,,}}," +
        "enlargelimits=false,axis on top,axis equal image]\\addplot graphics[xmin=0,xmax=1,ymin=0,ymax=1]" +
        "{" + basename(dateiname) + ".png};" +
        beschriftung + dimension +
        "\\end{axis}\\end{tikzpicture}" +
        ende
    )
    datei.close()

    if not tex:
        os.chdir(temp)
        os.system('pdflatex "' + dateiname + '.tex"')
        os.system('pdfcrop "' + dateiname + '.pdf" "' + dateiname + '.pdf"')
        os.system('pdftoppm -singlefile -png -q -r 300 "' + dateiname + '.pdf" "' + dat0name + '"')

        from shutil import rmtree
        rmtree(temp, True)

    return True
