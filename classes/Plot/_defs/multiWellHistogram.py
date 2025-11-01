import traceback
from typing import TYPE_CHECKING
import classes.UI.Graphing as graphing
import matplotlib.pyplot as pyplot


import global_vars
from defs.strtobool import strtobool
from enumerables import PlotType

if TYPE_CHECKING:
    from .. import Plot


def multiWellHistogram(self : 'Plot'):
    '''
    #Multi well Histogram or Frequency plot
    '''

    self.mlti_f = True           #mlti flag = on
    global_vars.PF=[]
    global_vars.facies=0
    global_vars.tmp.append(0)
    self.figures.clear()
    self.axes.clear()
    self.points.clear()

    # minimize graphs window
    self.graphingWindow.iconify()
    self.plotType = PlotType.Histogram

    #self.graphing.update()
    self.loadOrCreateSettings()

    try:
        c1 = self.mlt_well_df(self.wellList)
    except Exception:
        traceback.print_exc()
        self.graphingWindow.deiconify()
        self.mlti_f=False #reset
        return

    # get scales from plot settings in strings
    crv1=self.settings.Get('curve1')
    c1_norm = self.settings.Get('c1_norm')     # normalized histogram if True
    c1_bins = self.settings.Get('c1_bins')
    c1_min = self.settings.Get('c1_min')
    c1_max = self.settings.Get('c1_max')
    c1_base= self.settings.Get('c1_base')
    c1_color= self.settings.Get('c1_col')
    c1_edge = self.settings.Get('c1_edge')

    #str to of type conversions
    c1_base = int(c1_base)
    c1_norm = bool(strtobool(c1_norm))
    c1_norm = True ##to emulate old version. remove later
    c1_min = float(c1_min)
    c1_max = float(c1_max)

    # create figure with subplots and plot Histogram with depth curve besides it

    fig = pyplot.figure('All Wells'+ ' - Curve '+global_vars.SoftwareVersion, constrained_layout=True)
    self.figures.append(fig)
    self.resetDataFrames[fig.number] = [c1]
    self.axes= [                         #Create a list of axes
            fig.add_subplot(111)
        ]

    # Create histogram in first plot
    mpoints=[]
    pts=self.axes[0].hist(c1, color = c1_color, edgecolor = c1_edge, bins = int(c1_bins), density=c1_norm)
    mpoints.append(pts)
    if c1_base==10:
        self.axes[0].set_xscale('log', base=10, nonpositive='clip')
        self.axes[0].set_xlim(c1_min)    #Define limit data type first cast it on the Y axis
    else:
        self.axes[0].set_xlim(c1_max, c1_min)

    if c1_norm:
        self.axes[0].set(title ='Normalized Histogram of '+  crv1)
    else:
        self.axes[0].set(title ='Histogram of '+  crv1)


    fig.canvas.mpl_connect('button_press_event', lambda e: self.plotOnClick(e))
    fig.canvas.mpl_connect('key_release_event', lambda k: self.plotOnBaseKey(k))

    self.axes[0].set_aspect('auto')
    pyplot.show(block=True)

    self.mlti_f=False #reset
    self.graphingWindow.deiconify()
