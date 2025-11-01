

from typing import TYPE_CHECKING

import matplotlib.pyplot as pyplot
import pandas as pd

import defs.alert as alert
import global_vars
from defs.strtobool import strtobool
from enumerables import PlotType

if TYPE_CHECKING:
    from .. import Plot

def multipleWellHistograms(self : 'Plot'):
    '''
    Multiple well Histogram or Frequency plot
    '''

    global_vars.tmp.append(0)
    self.axes.clear()
    self.figures.clear()
    self.resetDataFrames.clear()
    mpoints=[]
    fg_idx=1
    ax_idx=0
    #set curves that need markers
    marklist=['KMAX','KVRT','K90',
    'CPOR','GDEN','BDEN','RSO','RSW']
    #fignum=1

    # minimize graphs window
    self.graphingWindow.iconify()
    self.plotType = PlotType.Histogram

    #Ask for default settings
    if self.loadOrCreateSettings() == False:
        alert.Error('Failed To Load or Create Settings')
        return

              #initialize reset curves
    for well in self.wellList.GetWells():

        c1=pd.DataFrame(None)

        try:
            c1, well_loc = self.mtp_well_df(well)
        except Exception:
            self.graphingWindow.deiconify()
            return

        #check if curve not empty
        if  c1.isnull().all():
            continue            #skip to next well


        # get scales from plot settings in strings
        c1_norm = self.settings.Get('c1_norm')     # normalized histogram if True
        c1_bins = self.settings.Get('c1_bins')
        c1_min = self.settings.Get('c1_min')
        c1_max = self.settings.Get('c1_max')
        c1_base = self.settings.Get('c1_base')
        c1_color = self.settings.Get('c1_col')
        c1_edge = self.settings.Get('c1_edge')

        #str to of type conversions
        c1_base = int(c1_base)
        c1_norm = bool(strtobool(c1_norm))
        c1_min = float(c1_min)
        c1_max = float(c1_max)

        '''
        if c1_base =='10': # If x-axis is in log scale
        pass
        '''


        # create figure with subplots and plot Histogram with depth curve besides it
        fig=pyplot.figure(f"{well.uwi}({well.alias}) - Curve {global_vars.SoftwareVersion}", constrained_layout=True)
        self.figures.append(fig)
        self.resetDataFrames[fig.number] = [c1]
        widths = [3, 1]
        heights = [1]
        spec = self.figures[fg_idx-1].add_gridspec(ncols=2, nrows=1, width_ratios=widths, height_ratios=heights)

        #Create a list of axes
        self.axes.append(self.figures[fg_idx-1].add_subplot(spec[0,0]))
        self.axes.append(self.figures[fg_idx-1].add_subplot(spec[0,1]))

        # Create histogram in first plot
        pts=self.axes[ax_idx].hist(c1, color = c1_color, edgecolor = c1_edge, bins = int(c1_bins), density=c1_norm)
        mpoints.append(pts)
        if c1_base==10:
            self.axes[ax_idx].set_xscale('log', nonpositive='clip')
            self.axes[ax_idx].set_xlim(c1_min)    #Define limit data type first cast it on the Y axis
        else:
            self.axes[ax_idx].set_xlim(c1_max, c1_min)

        crv1=c1.name
        if c1_norm:
            self.axes[ax_idx].set(title ='Normalized Histogram of '+  crv1)
        else:
            self.axes[ax_idx].set(title ='Histogram of '+  crv1)

        # Make depth plot
        if crv1 in marklist:
            self.axes[ax_idx+1].scatter(c1, c1.index, color=c1_color, marker='o')
        else:
            self.axes[ax_idx+1].plot(c1, c1.index, color=c1_color,  linewidth=1)

        self.axes[ax_idx+1].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        self.axes[ax_idx+1].set(title = "Track 1", xlabel = crv1, ylabel='DPT')

        fig.canvas.mpl_connect('button_press_event', lambda e: self.plotOnClick(e))
        fig.canvas.mpl_connect('key_release_event', lambda k: self.plotOnBaseKey(k, well))

        fg_idx +=1
        ax_idx +=2



    self.axes[0].set_aspect('auto')
    pyplot.show(block=True)

    # restore graphs window
    self.graphingWindow.deiconify()
