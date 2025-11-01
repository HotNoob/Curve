import traceback
from typing import TYPE_CHECKING

import matplotlib
import matplotlib.pyplot as pyplot

import defs.alert as alert
import global_vars
from classes.MinMaxScale import MinMaxScale
from enumerables import PlotType

if TYPE_CHECKING:
    from .. import Plot


def multiWellThreeDPlot(self : 'Plot'):
    '''
    Multi well Cross plot with color bar = zplot
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
    self.plotType = PlotType.ThreeDPlot

    selectors=['']
    rect_selectors=['']

    self.loadOrCreateSettings()

    try:
        c1, c2, c3, zc = self.mlt_well_df(self.wellList)
    except Exception:
        traceback.print_exc()
        self.graphingWindow.deiconify()
        self.mlti_f=False #reset
        return

    #set curves
    crv1=self.settings.Get('curve1')
    crv2=self.settings.Get('curve2')
    crv3=self.settings.Get('curve3')
    zcrv=self.settings.Get('zcurve')

    #set curves that need markers
    marklist=['KMAX','KVRT','K90',
    'CPOR','GDEN','BDEN','RSO','RSW']

        #check if c1 not empty
    if  c1.empty==True:
        return        #return to c_graph
    elif  c2.empty==True:
        return        #return to c_graph
    elif  c3.empty==True:
        return        #return to c_graph
    elif  zc.empty==True:
        return        #return to c_graph

    # create figure with subplots and plot Histogram with depth curve besides it
    #zcolmap=Zplot_colors()      # get default colors for Z-axis scale

    c1_scale=MinMaxScale.FromString(self.settings.Get('c1_scale'))
    c2_scale=MinMaxScale.FromString(self.settings.Get('c2_scale'))
    c3_scale=MinMaxScale.FromString(self.settings.Get('c3_scale'))
    zc_scale=MinMaxScale.FromString(self.settings.Get('z_scale'))

    fig = pyplot.figure('All Wells'+ ' - Curve '+global_vars.SoftwareVersion)
    self.figures.append(fig)
    my_ann=''

    #zcolmap=Zplot_colors()      # get default colors for Z-axis scale
    zcolmap=matplotlib.cm.get_cmap('viridis_r')


    self.axes= [                         #Create figure with one axes
            fig.add_subplot(111, projection='3d')
        ]

    # set color bar scale
    try:
        self.points[fig.number] = self.axes[0].scatter3D(c1, c2, c3, c=zc, marker='o', cmap=zcolmap, vmin=zc_scale.min, vmax=zc_scale.max)
    except  Exception:
        Err_txt=f'{crv1} and {crv2} have a different number of data points.'
        alert.Error(Err_txt)
        return        #return to c_graph

    self.axes[0].set_xlabel(crv1)
    self.axes[0].set_ylabel(crv2)
    self.axes[0].set_zlabel(crv3)

    if c1_scale.base==10:
        self.axes[0].set_xscale('log', base=10, nonpositive='clip')
    if c2_scale.base==10:
        self.axes[0].set_yscale('log', base=10, nonpositive='clip')
    if c3_scale.base==10:
        self.axes[0].set_zscale('log', base=10, nonpositive='clip')

    #define limits
    self.axes[0].set_xlim(c1_scale.min, c1_scale.max)
    self.axes[0].set_ylim(c2_scale.min, c2_scale.max)
    self.axes[0].set_zlim(c3_scale.min, c3_scale.max)

    self.axes[0].set(title = f'3D_plot of {crv2} versus {crv1} and {crv3} on z-axis. Press h for help')

    fig.canvas.mpl_connect('button_press_event', lambda e: self.plotOnClick(e))
    fig.canvas.mpl_connect('key_release_event', lambda k: self.plotOnBaseKey(k))

    # create an colorbar on the right side of ax.
    #divider = make_axes_locatable(ax[0])
    #cax = divider.append_axes("right", size="5%", pad=.2)
    cb = fig.colorbar(self.points[fig.number])
    cb.set_label(label=zcrv)
    cb.ax.tick_params(axis='y', direction='out')

    # Grids on
    self.axes[0].grid(True)

    self.axes[0].set_aspect('auto')

    pyplot.show(block=True)

    # restore graphs window
    self.mlti_f=False #reset
    self.graphingWindow.deiconify()
    pass