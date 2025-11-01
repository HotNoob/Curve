import traceback
from typing import TYPE_CHECKING

import matplotlib.axes
import matplotlib.cm
import matplotlib.figure
import matplotlib.pyplot as pyplot
import pandas as pd

import defs.alert as alert
import global_vars
from classes.MinMaxScale import MinMaxScale
from classes.SelectFromCollection import SelectFromCollection
from defs.strtobool import strtobool
from enumerables import PlotType

if TYPE_CHECKING:
    from .. import Plot


def singleWellThreeDPlot(self : 'Plot'):
    '''
    Single 3_D Cross plot with Z axis
    '''

    global_vars.tmp.append(0)

    self.axes.clear()
    self.figures.clear()
    self.points.clear()

    # minimize graphs window
    self.graphingWindow.iconify()
    self.plotType = PlotType.ThreeDPlot

    #Ask for default settings
    self.loadOrCreateSettings()

    for well in self.wellList.GetWells():
        self.figures.clear()
        self.axes.clear()
        self.resetDataFrames.clear()

        #initialize dfs
        c1=pd.DataFrame(None)
        c2=pd.DataFrame(None)
        c3=pd.DataFrame(None)
        zc=pd.DataFrame(None)

        try:
            c1,c2,c3,zc, well_loc = self.mtp_well_df(well)
        except Exception:
            print(traceback.format_exc())
            self.graphingWindow.deiconify()
            return
        
        #load plot data from LAS and/or core
        #check if crvs are in cdescrvs

        crv1=self.settings.Get('curve1')
        crv2=self.settings.Get('curve2')
        crv3=self.settings.Get('curve3')
        zcrv=self.settings.Get('zcurve')

        #set curves that need markers
        marklist=['KMAX','KVRT','K90',
        'CPOR','GDEN','BDEN','RSO','RSW']

        #check if c1 not empty
        if  c1.empty==True:
            continue            #skip to next well
        elif  c2.empty==True:
            continue            #skip to next well
        elif  c3.empty==True:
            continue            #skip to next well
        elif  zc.empty==True:
            continue            #skip to next well

        #zcolmap=Zplot_colors()      # get default colors for Z-axis scale
        zcolmap=matplotlib.cm.get_cmap('viridis_r')

        c1_scale=MinMaxScale.FromString(self.settings.Get('c1_scale'))
        c2_scale=MinMaxScale.FromString(self.settings.Get('c2_scale'))
        c3_scale=MinMaxScale.FromString(self.settings.Get('c3_scale'))
        z_scale=MinMaxScale.FromString(self.settings.Get('z_scale'))

        #Create figure with subplots
        fig=pyplot.figure(f"{well.uwi}({well.alias}) - Curve {global_vars.SoftwareVersion}")        #not compatible with tight_layout? , constrained_layout=True
        self.figures.append(fig)
        self.resetDataFrames[fig.number] = [c1]


        widths = [6, 1, 1, 1]
        heights = [1]
        spec = fig.add_gridspec(ncols=4, nrows=1, width_ratios=widths, height_ratios=heights)

                  #clear axes
        self.axes=[                                      #Create a list of axes
            fig.add_subplot(spec[0,0],projection='3d'),
            fig.add_subplot(spec[0,1]),
            fig.add_subplot(spec[0,2]),
            fig.add_subplot(spec[0,3])
        ]

        # NaN to zero in zc
        try:
            self.points[fig.number] = self.axes[0].scatter3D(c1, c2, c3, c=zc, marker='o', cmap=zcolmap, vmin=z_scale.min, vmax=z_scale.max)
        except  Exception:
            Err_txt=f'{crv1} and {crv2} of {well.uwi}({well.alias}) have a different number of data points. Skip Well'
            alert.Error(Err_txt)
            continue      #skip well

        self.axes[2].sharey=self.axes[1]        #in case two depth tracks are required
        self.axes[3].sharey=self.axes[2]        #in case two depth tracks are required

        self.axes[0].set_xlabel(crv1)
        self.axes[0].set_ylabel(crv2)
        self.axes[0].set_zlabel(crv3)
        if c1_scale.base==10:
            self.axes[1].set_xscale('log', base=10, nonpositive='clip')
        if c2_scale.base==10:
            self.axes[1].set_yscale('log', base=10, nonpositive='clip')
            self.axes[1].set_ylim(c2_scale.min)    #Define limit data type first cast it on the Y axis
        if c2_scale.base==0:                 #linear scale
            self.axes[1].set_ylim(c2_scale.min, c2_scale.max)


        self.axes[0].set_xlim(c1_scale.min, c1_scale.max)
        self.axes[0].set_ylim(c2_scale.min, c2_scale.max)
        self.axes[0].set_zlim(c3_scale.min, c3_scale.max)
        #ax[0].set_xlim(left=-300, right=100)
        self.axes[0].set(title = '3D_plot of '+ crv2 +' versus ' + crv1 + ' with ' + crv3 + ' on z-axis')


        fig.canvas.mpl_connect('button_press_event', lambda e: self.plotOnClick(e))
        fig.canvas.mpl_connect('key_release_event', lambda k: self.plotOnBaseKey(k, well))

        # create an axes on the right side of ax.
        #divider = make_axes_locatable(ax[0])
        #cax = divider.append_axes("top", size="5%", pad=0.05)
        #cb = fig.colorbar(pts,ax=ax[0],cax=cax)
        cb = fig.colorbar(self.points[fig.number],ax=self.axes[0])
        cb.set_label(label=zcrv)
        cb.ax.tick_params(axis='y', direction='in')

        # Make three depth plots
        if crv1 in marklist:
            self.axes[1].scatter(c1, c1.index, color=self.settings.Get('c1_col'), marker='o')
        else:
            self.axes[1].plot(c1, c1.index, color=self.settings.Get('c1_col'), linestyle= self.settings.Get('c1_type'), linewidth=self.settings.Get('c1_width'))
        self.axes[1].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        self.axes[1].set(title = "Track 1",xlabel = crv1)      #, xlabel = crv1
        self.axes[1].tick_params(labelleft=False, labelright=False)

        if crv2 in marklist:
            self.axes[2].scatter(c2, c2.index, color=self.settings.Get('c2_col'), marker='o')
        else:
            self.axes[2].plot(c2, c2.index, color=self.settings.Get('c2_col'), linestyle= self.settings.Get('c2_type'), linewidth=self.settings.Get('c2_width'))
        self.axes[2].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        self.axes[2].set(title = "Track 2", xlabel = crv2, ylabel='DPT')

        if crv3 in marklist:
            self.axes[3].scatter(c3, c3.index, color=self.settings.Get('c3_col'), marker='o')
        else:
            self.axes[3].plot(c3, c3.index, color=self.settings.Get('c3_col'), linestyle= self.settings.Get('c3_type'), linewidth=self.settings.Get('c3_width'))
        self.axes[3].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        self.axes[3].set(title = "Track 3", xlabel = crv3)
        self.axes[3].tick_params(labelleft=False, labelright=False)

        # Grids on
        self.axes[0].grid(True)
        self.axes[1].grid(True)
        self.axes[2].grid(True)
        self.axes[3].grid(True)

        #fig.tight_layout()
        self.axes[0].set_aspect('auto')
        pyplot.show(block=True)

    #plt.close('all')
    # restore graphs window
    self.graphingWindow.deiconify()