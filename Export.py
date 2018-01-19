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
    dateiname = string.rstrip(dateiname, ".tex")

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

    gwy.gwy_file_save(daten, dateiname + ".png", gwy.RUN_NONINTERACTIVE)
    datei = open(dateiname + ".tex", 'w')

    xdiv = round(0.3 * xmax, 7)
    xdim = "$" + str(xdiv * 10**6) + "\\,$\\textmu m"
    xdiv = str(xdiv / xmax)

    einheit = bild.get_si_unit_z().get_string(gwy.SI_UNIT_FORMAT_TEX)
    zmin = "$" + str(zmin * 10**6) + "\\,$\\textmu " + einheit
    zmax = "$" + str(zmax * 10**6) + "\\,$\\textmu " + einheit
    datei.write(
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
        "\\node[white,anchor=north west]at(.05,.95){\\!\\contour{black}{\\gwylabel}};" +
        "\\filldraw[draw=black,fill=white,line width=.05em](.05,.05)rectangle+(" + xdiv + ",.25ex)" +
        "node[white,pos=.5,inner sep=.5ex,above]{\\contour{black}{" + xdim + "}};" +
        "\end{axis}\end{tikzpicture}"
    )
    datei.close()
    return True
