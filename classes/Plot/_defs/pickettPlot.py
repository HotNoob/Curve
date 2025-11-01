import traceback
from typing import TYPE_CHECKING

import matplotlib.axes
import matplotlib.cm
import matplotlib.figure
import matplotlib.pyplot as pyplot
import numpy as np
from matplotlib.ticker import FormatStrFormatter
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable

import defs.excel as excel
import global_vars
from enumerables import PlotType

if TYPE_CHECKING:
    from .. import Plot


#--------------------------------------------------------------------------------------------------------------------------------------------
def pickettPlot(self : 'Plot'):
    '''
        Display Pickett plot for eacH well in Well_List
    '''
    self.axes.clear()
    self.figures.clear()

    fg_idx=ax_idx=0

    # minimize graphs window
    self.graphingWindow.iconify()
    self.plotType = PlotType.PK

    self.loadOrCreateSettings()

    #get parms
    #mpath='databases/Params.xlsx'
    #excel.get_exceldata(mpath)

    
    for well in self.wellList.GetWells():
        try:
            c1, c2, zc, mdis, well_loc = self.mtp_well_df(well)
        except Exception:
            print(traceback.format_exc())
            # restore graphs window
            self.graphingWindow.deiconify()
            return

        #get zone
        zone=self.settings.Get('zone')
        # Archie Parameters - Get for zone

        # from para_df
        
        a =float(global_vars.project.formationZoneParameters.Get('a').Get(zone))         #turtuosity factor
        m =float(global_vars.project.formationZoneParameters.Get('m').Get(zone))         #cementation factor
        n =float(global_vars.project.formationZoneParameters.Get('n').Get(zone))         #saturation exponent
        rw=float(global_vars.project.formationZoneParameters.Get('rw').Get(zone))        #water resistivity

        #zcolmap=Zplot_colors()      # get default colors for Z-axis scale
        zcolmap=matplotlib.cm.get_cmap('viridis_r')

                #check if c1 not empty
        if  c1.isnull().all():
            continue            #skip to next well
        elif  c2.isnull().all():
            continue            #skip to next well
        elif  zc.isnull().all():
            continue            #skip to next well

        c1_min=0.1
        c1_max=1000
        c1_base : int =10
        c2_min=0.01
        c2_max=1.0
        c2_base : int = 10
        zc_min=0
        zc_max=1.0
        zc_base= 0

        #Create figure with subplots
        fig=pyplot.figure(f"{well.uwi}({well.alias}) - Curve {global_vars.SoftwareVersion}")
        self.figures.append(fig)
        widths = [3, 1, 1]
        heights = [1]
        spec = self.figures[fg_idx].add_gridspec(ncols=3, nrows=1, width_ratios=widths, height_ratios=heights)

        #Create a list of 3 axes
        self.axes.append(self.figures[fg_idx].add_subplot(spec[0,0]))
        self.axes.append(self.figures[fg_idx].add_subplot(spec[0,1]))
        self.axes.append(self.figures[fg_idx].add_subplot(spec[0,2]))
        #discriminator plotting
        dis_val=float(self.settings.Get('comp_val'))
        if self.settings.Get('comparitor')=='<':
            c1_T=c1[mdis<dis_val]
            c2_T=c1[mdis<dis_val]
        elif self.settings.Get('comparitor')=='>':
            c1_T=c1[mdis>dis_val]
            c2_T=c1[mdis>dis_val]

        self.axes[ax_idx].scatter(c1_T, c2_T, marker='o', color=self.settings.Get('c1_col'))           # Xplot

        crv1=c1.name
        crv2=c2.name
        self.axes[ax_idx].set_xlabel(crv1)
        self.axes[ax_idx].set_ylabel(crv2)
        if int(c1_base)==10:
            self.axes[ax_idx].set_xscale('log', base=10, nonpositive='clip')
        if int(c2_base)==10:
            self.axes[ax_idx].set_yscale('log', base=10, nonpositive='clip')

        f_min=float(c1_min) #Define limit data type first cast it on the X axis
        f_max=float(c1_max)
        self.axes[ax_idx].set_xlim(f_min, f_max)
        f_min=float(c2_min) #Define limit data type first cast it on the Y axis
        f_max=float(c2_max)
        self.axes[ax_idx].set_ylim(f_min, f_max)

        self.axes[ax_idx].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        self.axes[ax_idx].xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        mtxt='Pickett Plot for '+self.settings.Get('cp_crv')+' '+self.settings.Get('comparitor')+' '+self.settings.Get('comp_val')
        self.axes[ax_idx].set(title = mtxt)

        #my_ann=ax[ax_idx].annotate('',xy=(0.05, 0.95), xycoords='axes fraction',xytext=(0.2, 0.95), textcoords='axes fraction')

        # NaN to zero in zc
        vmin=zc_min
        vmax=zc_max

        pts=self.axes[ax_idx].scatter(c1, c2, c=zc, marker='o', cmap=zcolmap, vmin=vmin, vmax=vmax)           # Xplot  pts is needed to connect to colorbar

        # create an colorbar on the right side of ax.
        divider = make_axes_locatable(self.axes[ax_idx])
        cax = divider.append_axes("right", size="5%", pad=.05)
        cb = fig.colorbar(pts,ax=self.axes[ax_idx],cax=cax)
        cb.set_label(label=zc.name)
        cb.ax.tick_params(axis='y', direction='in')

        # Make two depth plots
        self.axes[ax_idx+2].sharey=self.axes[ax_idx+1]        #in case two depth tracks are required

        self.axes[ax_idx+1].plot(c1, c1.index, color=self.settings.Get('c1_col'), linestyle=self.settings.Get('c1_type'), linewidth=self.settings.Get('c1_width'))
        self.axes[ax_idx+1].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        self.axes[ax_idx+1].set(title = "Track 1", xlabel = crv1, ylabel='DPT')      #
        self.axes[ax_idx+1].tick_params(labelleft=False, labelright=False)

        self.axes[ax_idx+2].plot(c2, c2.index, color=self.settings.Get('c2_col'), linestyle=self.settings.Get('c2_type'), linewidth=self.settings.Get('c2_width'))
        self.axes[ax_idx+2].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        self.axes[ax_idx+2].set(title = "Track 2", xlabel = crv2)
        self.axes[ax_idx+2].tick_params(labelleft=False, labelright=True)

        self.axes[ax_idx].set_aspect('auto')

        # Grids on
        self.axes[ax_idx].grid(True, which='both',ls='-',color='silver')
        self.axes[ax_idx+1].grid(True)
        self.axes[ax_idx+2].grid(True)

        #calculate the saturation lines
        sw_plot=(1.0,0.5,0.25)
        phit_plot=(0.01,1)
        sw_len=len(sw_plot)
        phit_len=len(phit_plot)
        rt_plot=np.zeros((sw_len,phit_len))

        for i in range (0,sw_len):
            for j in range (0,phit_len):
                rt_result=((a*rw)/(sw_plot[i]**n)/(phit_plot[j]**m))
                rt_plot[i,j]=rt_result
        for i in range(0,sw_len):
            self.axes[ax_idx].plot(rt_plot[i],phit_plot, label='Sw '+str(float(sw_plot[i]))+' v/v')
            self.axes[ax_idx].legend (loc='best')


        self.figures[fg_idx].canvas.mpl_connect('button_press_event',lambda e: self.pickettPlotOnClick(zone))            #on click left mouse button
        #fg[fg_idx].tight_layout()

        fg_idx +=1
        ax_idx +=3
    #End well list loop
    pyplot.show()

    self.graphingWindow.deiconify()
