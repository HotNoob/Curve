import traceback
from typing import TYPE_CHECKING

import matplotlib.pyplot as pyplot
import pandas as pd

import defs.alert as alert
import global_vars
from defs.strtobool import strtobool
from enumerables import PlotType

if TYPE_CHECKING:
    from .. import Plot


def singleWellHistogramPlot(self : 'Plot'):
    '''
    #Single well Histogram or Frequency plot
    '''

    global_vars.tmp.append(0)
    self.axes.clear()
    self.figures.clear()
    mpoints=[]
    #set curves that need markers
    marklist=['KMAX','KVRT','K90','CPOR','GDEN','BDEN','RSO','RSW']

    # minimize graphs window
    self.graphingWindow.iconify()
    self.plotType = PlotType.Histogram

    global_vars.perfTest.Start("histogram_total")
    if self.loadOrCreateSettings() == False:
        alert.Error('Failed To Load or Create Settings')
        return


    for well in self.wellList.GetWells():
        self.resetDataFrames.clear()
        self.figures.clear()
        self.axes.clear()
        c1 : pd.DataFrame = pd.DataFrame(None)

        try:
            c1, well_loc=self.mtp_well_df(well)
        except Exception as e:
            print(traceback.format_exc())
            self.graphingWindow.deiconify()
            return
        
        #check if c1 not empty
        if  c1.empty==True:
            continue

        # get scales from plot settings in strings
        c1_color = self.settings.Get('c1_col')
        c1_edge = self.settings.Get('c1_edge')
        c1_norm = self.settings.Get('c1_norm')
        c1_bins = self.settings.Get('c1_bins')
        c1_min = self.settings.Get('c1_min')
        c1_max = self.settings.Get('c1_max')
        c1_base = self.settings.Get('c1_base')

        #settings str
        c1_norm = bool(strtobool(c1_norm))
        c1_base = int(c1_base)
        c1_min = float(c1_min)
        c1_max = float(c1_max)

        # create figure with subplots and plot Histogram with depth curve besides it
        crv1=c1.name
        figure=pyplot.figure(f"{well.uwi}({well.alias}) - Curve {global_vars.SoftwareVersion}" , constrained_layout=True)
        self.figures.append(figure)
        self.resetDataFrames[figure.number] = [c1]

        widths = [3, 1]
        heights = [1]
        spec = figure.add_gridspec(ncols=2, nrows=1, width_ratios=widths, height_ratios=heights)

        self.axes= [                         #Create a list of axes
                figure.add_subplot(spec[0,0]),
                figure.add_subplot(spec[0,1])
              ]

        # Create histogram in first plot
        self.axes[0].hist(c1, color = c1_color, edgecolor = c1_edge, bins = int(c1_bins), density=c1_norm)

        if c1_base==10:
            self.axes[0].set_xscale('log', base=10, nonpositive='clip')
            self.axes[0].set_xlim(c1_min)    #Define limit data type first cast it on the Y axis
        else:
            self.axes[0].set_xlim(c1_max, c1_min)
        #ax[0].set_xlim(left=-300, right=100)
        if c1_norm:
            self.axes[0].set(title =f'Normalized Histogram of {crv1}. Press h for help')
        else:
            self.axes[0].set(title =f'Histogram of {crv1}. Press h for help')

        # Make depth plot
        if crv1 in marklist:
            mp=self.axes[1].scatter(c1, c1.index, color=c1_color, marker='o', linewidth=1)
        else:
            mp=self.axes[1].plot(c1, c1.index, color=c1_color,  linewidth=1)

        mpoints.append(mp) #is normally sent to plotOnBaseKey, but it is not used there. is this needed?
        self.axes[1].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        self.axes[1].set(title = "Track 1", xlabel = crv1, ylabel='DPT')

        figure.canvas.mpl_connect('button_press_event', lambda e: self.plotOnClick(e))
        figure.canvas.mpl_connect('key_release_event', lambda k:  self.plotOnBaseKey(k, well))

        self.axes[0].set_aspect('auto')

        global_vars.perfTest.Stop("histogram_total")
        pyplot.show(block=True)

    # restore graphs window
    self.graphingWindow.deiconify()