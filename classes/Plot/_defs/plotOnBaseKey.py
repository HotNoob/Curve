from typing import TYPE_CHECKING

import matplotlib.pyplot as pyplot
from matplotlib.backend_bases import KeyEvent
from numpy import nan as NaN

import global_vars
import defs.alert as alert
import defs.main as main

from enumerables import PlotType, Help

if TYPE_CHECKING:
    from .. import Plot
    from classes.Project.Well import Well


def plotOnBaseKey(self : 'Plot', event : KeyEvent, well : 'Well'):
    '''
    On Key press for histograms and 3D
    Graph manipulation keys    e = event    d= set discriminators

    parms:e,fg, ax, pts, plt_set, dpt_line, tl_deg, t_line
    '''


    figure = event.canvas.figure
    if event.key=='h':
        #open help file.
        main.c_help(Help.Graph)

    #Set active figure
    if figure.number>len(global_vars.project.currentWellList):   #more figures than there are wells in the Well_List
        print('WARNING: CLOSING FIGURES, more figures than wells')
        pyplot.close('all')
        return
    
    pyplot.figure(figure)                  #set active figure
    ax_idx=(figure.number-1)*3
    #find well number of selected figure


    if event.key=='d' and self.mlti_f==False and self.plotType==PlotType.Histogram:   #discriminator selected

        crv1 = self.settings.Get('curve1')
        c1_color = self.settings.Get('c1_col')
        c1_edge = self.settings.Get('c1_edge')
        c1_norm = self.settings.Get('c1_norm')
        c1_bins = self.settings.Get('c1_bins')
        c1_min = self.settings.Get('c1_min')
        c1_max = self.settings.Get('c1_max')
        c1_base = self.settings.Get('c1_base')

        #set curves that need markers
        marklist=['KMAX','KVRT','K90',
        'CPOR','GDEN','BDEN','RSO','RSW']

        c1=self.resetDataFrames[figure.number][0]

        #get discriminator
        disc1, disc2, min1, max1, min2, max2 = self.get_discriminator(well)

        ax_idx=0   #get axis

        if global_vars.tmp!=[]:             #reset
            global_vars.tmp=[]
            figure.axes[ax_idx].clear()
            figure.axes[ax_idx].hist(c1, color = c1_color, edgecolor = c1_edge, bins = int(c1_bins), density=bool(c1_norm))
            if int(c1_base)==10:
                figure.axes[ax_idx].set_xscale('log', base=10, nonpositive='clip')
                figure.axes[ax_idx].set_xlim(float(c1_min))    #Define limit data type first cast it on the Y axis

            else:
                f_min=float(c1_min)
                f_max=float(c1_max)
                figure.axes[ax_idx].set_xlim(f_max, f_min)

            if c1_norm=='True':
                figure.axes[ax_idx].set(title =f'Normalized Histogram of {crv1}. Press h for help')
            else:
                figure.axes[ax_idx].set(title =f'Histogram of {crv1}. Press h for help')

            figure.axes[ax_idx].figure.canvas.draw()

            if len(figure.axes)>0:
                figure.axes[ax_idx+1].clear()
                figure.axes[ax_idx+1].set_ylim(float(c1.index[-1]), float(c1.index[0]))   # reverses depth scale to shallow at top
                figure.axes[ax_idx+1].set(title = "Track 1", xlabel = crv1, ylabel='DPT')
                if crv1 in marklist:
                    figure.axes[ax_idx+1].scatter(c1, c1.index, color=c1_color, marker='o', linewidth=1)
                else:
                    figure.axes[ax_idx+1].plot(c1, c1_bins.index, color=c1_color,  linewidth=1)
                figure.axes[ax_idx+1].figure.canvas.draw()
                return

        cd1=c1.copy()     #original
        cd2=c1.copy()
        cd2[:]=NaN

        #ensure same core curve df and las curve df length
        mxlen=len(cd1)*0.1
        mtop=cd1.index[0]

        #Apply discriminator filters
        if disc1.empty==False:         #if discrimator curve 1 NOT empty
            #check for discriminator compatibility
            disc_top= disc1.index[0]
            disc_len=len(disc1)*0.1
            #if depth interval of disc1 does not cover cd1 (c1)
            if disc_top > mtop or ((disc_top + disc_len) < (mtop + mxlen)):
                alert.Error(f"{c1.name} and {disc1.name} are not compatible")
                return
            cd1=cd1[disc1>min1]
            cd1=cd1[disc1<max1]
        if disc2.empty==False:
            #check for discriminator compatibility
            disc_top= disc2.index[0]
            disc_len=len(disc2)*0.1
            #if depth interval of disc1 does not cover cd1 (c1)
            if disc_top > mtop or ((disc_top + disc_len)< (mtop + mxlen)):
                alert.Error(f"{c1.name} and {disc2.name} are not compatible")
                return
            cd1=cd1[disc2>min2]
            cd1=cd1[disc2<max2]

        if cd1.empty==True:             #if all data points are filtered out
            alert.Error(f"All data points in {well.uwi}({well.alias}) have been filtered out. Select other discriminators")
            return

        #update graph
        figure.axes[ax_idx].clear()
        figure.axes[ax_idx].hist(cd1, color = c1_color, edgecolor = c1_edge, bins = int(c1_bins), density=bool(c1_norm))

        if int(c1_base)==10:
            figure.axes[ax_idx].set_xscale('log', base=10, nonpositive='clip')
            figure.axes[ax_idx].set_xlim(float(c1_min))    #Define limit data type first cast it on the Y axis

        else:
            f_min=float(c1_min)
            f_max=float(c1_max)
            figure.axes[ax_idx].set_xlim(f_max, f_min)
        if c1_norm=='True':
            figure.axes[ax_idx].set(title =f'Normalized Histogram of {crv1}. Press h for help')
        else:
            figure.axes[ax_idx].set(title =f'Histogram of {crv1}. Press h for help')

        # Make depth plot
        top=cd1.index[0]
        base=cd1.index[-1]
        cd2.loc[top:base]=cd1.loc[top:base]

        if crv1 in marklist:
            figure.axes[ax_idx+1].scatter(cd2, cd2.index, color='fuchsia', marker='o', linewidth=1)
        else:
            figure.axes[ax_idx+1].plot(cd2, cd2.index, color='fuchsia',  linewidth=1)
        figure.axes[ax_idx+1].figure.canvas.draw()
    return
