from typing import TYPE_CHECKING

import matplotlib.axes
import matplotlib.cm
import matplotlib.figure
import matplotlib.pyplot as pyplot

import defs.alert as alert
import global_vars
from classes.MinMaxScale import MinMaxScale
from enumerables import PlotType

if TYPE_CHECKING:
    from .. import Plot


def multipleWellThreeDPlot(self : 'Plot'):
    '''
     Multiple Cross plot with 3d axes for each well in well list and colot bar
    '''
    global_vars.PF=[]
    global_vars.facies=0
    global_vars.tmp.append(0)
    self.axes.clear()
    self.figures.clear()
    self.points.clear()
    self.resetDataFrames.clear()
    ax_idx=0
    fg_idx=1

    # minimize graphs window
    self.graphingWindow.iconify()
    self.plotType = PlotType.ThreeDPlot

    self.loadOrCreateSettings()


    #load plot data from LAS and/or core
    crv1=self.settings.Get('curve1')
    crv2=self.settings.Get('curve2')
    crv3=self.settings.Get('curve3')
    zcrv=self.settings.Get('zcurve')

    for well in self.wellList.GetWells():
        try:
            c1, c2, c3, zc, well_loc = self.mtp_well_df(well)

        except Exception:
            self.graphingWindow.deiconify()
            return

        #set curves that need markers
        marklist=['KMAX','KVRT','K90',
        'CPOR','GDEN','BDEN','RSO','RSW']

            #zcolmap=Zplot_colors()      # get default colors for Z-axis scale
        zcolmap=matplotlib.cm.get_cmap('viridis_r')

        #check if c1 not empty
        if  c1.empty==True:
            continue            #skip to next well
        elif  c2.empty==True:
            continue            #skip to next well
        elif  c3.empty==True:
            continue            #skip to next well
        elif  zc.empty==True:
            continue            #skip to next well

        c1_scale=MinMaxScale.FromString(self.settings.Get('c1_scale'))
        c2_scale=MinMaxScale.FromString(self.settings.Get('c2_scale'))
        c3_scale=MinMaxScale.FromString(self.settings.Get('c3_scale'))
        zc_scale=MinMaxScale.FromString(self.settings.Get('z_scale'))

        #Create figure with subplots
        fig=pyplot.figure(f"{well.uwi}({well.alias}) - Curve {global_vars.SoftwareVersion}")
        self.figures.append(fig)
        #set reset curve list
        self.resetDataFrames[fig.number] = [c1,c2, c3, zc]

        widths = [6, 1, 1, 1]
        heights = [1]
        spec = self.figures[fg_idx-1].add_gridspec(ncols=4, nrows=1, width_ratios=widths, height_ratios=heights)

        #Create a list of 4 axes
        self.axes.append(self.figures[fg_idx-1].add_subplot(spec[0,0], projection='3d'))
        self.axes.append(self.figures[fg_idx-1].add_subplot(spec[0,1]))
        self.axes.append(self.figures[fg_idx-1].add_subplot(spec[0,2]))
        self.axes.append(self.figures[fg_idx-1].add_subplot(spec[0,3]))

        self.axes[ax_idx+2].sharey=self.axes[ax_idx+1]        #in case two depth tracks are required
        self.axes[ax_idx+3].sharey=self.axes[ax_idx+2]        #in case two depth tracks are required

        # NaN to zero in zc
        vmin=float(zc_scale.min)
        vmax=float(zc_scale.max)

        try:
            self.points[fig.number] = self.axes[ax_idx].scatter3D(c1, c2, c3, c=zc, marker='o', cmap=zcolmap, vmin=vmin, vmax=vmax)
        except  Exception:
            Err_txt=f'{crv1} and {crv2} of {well.uwi}({well.alias}) have a different number of data points. Skip Well'
            alert.Error(Err_txt)
            continue      #skip well

        self.axes[ax_idx].set_xlabel(crv1)
        self.axes[ax_idx].set_ylabel(crv2)
        self.axes[ax_idx].set_zlabel(crv3)

        if c1_scale.base==10:
            self.axes[ax_idx].set_xscale('log', base=10, nonpositive='clip')
        if c2_scale.base==10:
            self.axes[ax_idx].set_yscale('log', base=10, nonpositive='clip')
        if c3_scale.base==10:
            self.axes[ax_idx].set_zscale('log', base=10, nonpositive='clip')

        #Define limits
        self.axes[ax_idx].set_xlim(c1_scale.min, c1_scale.max)
        self.axes[ax_idx].set_ylim(c2_scale.min, c2_scale.max)
        f_min=float(c3.min())
        f_max=float(c3.max())
        self.axes[ax_idx].set_zlim(f_min, f_max)
        #ax[ax_idx].set_xlim(left=-300, right=100)

        self.axes[ax_idx].set(title = '3D_plot of '+ crv2 +' versus ' + crv1 + ' with ' + crv3 + ' on z-axis')

        fig.canvas.mpl_connect('button_press_event', lambda e: self.plotOnClick(e))
        fig.canvas.mpl_connect('key_release_event', lambda k: self.plotOnBaseKey(k, well))

        # create an axes on the right side of ax.
        #divider = make_axes_locatable(ax[ax_idx])
        #cax = divider.append_axes("top", size="5%", pad=0.05)
        #cb = fig.colorbar(pts,ax=ax[ax_idx],cax=cax)
        cb = fig.colorbar(self.points[fig.number],ax=self.axes[ax_idx])
        cb.set_label(label=zcrv)
        cb.ax.tick_params(axis='y', direction='in')

        # Make three depth plots
        self.axes[ax_idx+2].sharey=self.axes[ax_idx+1]        #in case two depth tracks are required
        self.axes[ax_idx+3].sharey=self.axes[ax_idx+1]        #in case two depth tracks are required

        if crv1 in marklist:
            self.axes[ax_idx+1].scatter(c1, c1.index, color=self.settings.Get('c1_col'), marker='o')
        else:
            self.axes[ax_idx+1].plot(c1, c1.index, color=self.settings.Get('c1_col'), linestyle= self.settings.Get('c1_type'), linewidth=self.settings.Get('c1_width'))
        self.axes[ax_idx+1].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        self.axes[ax_idx+1].set(title = "Track 1",xlabel = crv1)      #, xlabel = crv1
        self.axes[ax_idx+1].tick_params(labelleft=False, labelright=False)

        if crv2 in marklist:
            self.axes[ax_idx+2].scatter(c2, c2.index, color=self.settings.Get('c2_col'), marker='o')
        else:
            self.axes[ax_idx+2].plot(c2, c2.index, color=self.settings.Get('c2_col'), linestyle= self.settings.Get('c2_type'), linewidth=self.settings.Get('c2_width'))
        self.axes[ax_idx+2].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        #ax[ax_idx+

        if crv3 in marklist:
            self.axes[ax_idx+3].scatter(c3, c3.index, color=self.settings.Get('c3_col'), marker='o')
        else:
            self.axes[ax_idx+3].plot(c3, c3.index, color=self.settings.Get('c3_col'), linestyle= self.settings.Get('c3_type'), linewidth=self.settings.Get('c3_width'))
        self.axes[ax_idx+3].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        self.axes[ax_idx+3].set(title = "Track 3", xlabel = crv3)
        self.axes[ax_idx+3].tick_params(labelleft=False, labelright=False)

        # Grids on
        self.axes[ax_idx].grid(True)
        self.axes[ax_idx+1].grid(True)
        self.axes[ax_idx+2].grid(True)
        self.axes[ax_idx+3].grid(True)

        fg_idx +=1
        ax_idx +=4

    #ax[0].set_aspect('auto')
    pyplot.show(block=True)

    #plt.close('all')
    # restore graphs window
    self.graphingWindow.deiconify()