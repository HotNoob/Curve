# pylint: disable=no-name-in-module
'''Dpt_plt'''
from typing import TYPE_CHECKING

import matplotlib.pyplot as pyplot
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.widgets import MultiCursor


import defs.excel as excel
import global_vars
from classes.LineBuilder import LineBuilder
from classes.Project.FormationInfo import FormationInfo
from structs import ZoneDepths

from . import _enumerables

if TYPE_CHECKING:
    from .. import DepthPlot

#============================================================================================
def depthPlot(self : 'DepthPlot', title, curvs : list, fcrvs, props, trcks, pltype : _enumerables.DepthPlotType, formations : dict[str, FormationInfo], zoneDepths : ZoneDepths):
    '''
    modified dept plots and A.McDonald
    pltype=0 regular plot.  pltype=1 depth shift plt_type=2 allows for multiple depth plots
    props[color, linestyle, ticks, scale (0=default, 1='log'), marker, track, fill, crv, constant,GT/LT, Col,alp ]

    ******* Choose how many curves are from Indir in the curve boxes and the rest is from Outdir
    '''

    f_idx=0                 #fill curve index
    marklist=['KMAX','KVRT','K90','CPOR','GDEN','BDEN','RSO','RSW']
    #get settings
    #num_tracks=plt_set['tracks'][]
    #get alias curve names
    #get zones and depth interval
    excel.get_zone()


    min_y = zoneDepths.top
    max_y = zoneDepths.base
                # dolomite, limestone, shale sandstone
    myhatches = ['/-', '\\', '-|-|-', '--------', '+-+', 'x', 'o', 'O', '..', '*', '//',
             '\\\\', '||', '-|-', '~~', 'xx', 'oo', 'OO', '..', '**']
    color_list=['green', 'palegreen','red','lightcoral','olive','blue','cyan' ,'magenta','purple','gold','lightgrey', 'black', 'darkblue', 'lightblue', 'gray','yellow','orange']
    '''
    character description
    '-'       solid line style
    '--'      dashed line style
    '-.'      dash-dot line style
    ':'       dotted line style
    '.'       point marker
    ','       pixel marker
    'o'       circle marker
    'v'       triangle_down marker
    '^'       triangle_up marker
    '<'       triangle_left marker
    '>'       triangle_right marker
    '1'       tri_down marker
    '2'       tri_up marker
    '3'       tri_left marker
    '4'       tri_right marker
    's'       square marker
    'p'       pentagon marker
    '*'       star marker
    'h'       hexagon1 marker
    'H'       hexagon2 marker
    '+'       plus marker
    'x'       x marker
    'D'       diamond marker
    'd'       thin_diamond marker
    '|'       vline marker
    '_'       hline marker

    custom line tupple: (offset, (on, off, on, off...))
    The first value, offset, is the length before the pattern starts.
    This will usually be zero.
    The second parameter is a tuple of on/off values.
    So for example, if the value is (5, 2, 1, 2) the line will consist of
    a dash of 5 units, a gap of 2 units, a dash of 1 unit, a gap of 2 units.
    This pattern repeats for the length of the line.
    A "unit" in this case is equal to the width of the line.
    '''
    # get parameters from Depth Plot Settings
    line_list=['dotted','solid','dashed','dashdot',(0,(3,1,1,1)),(0,(4, 2, 1, 2)),(0,(3,1,1,1,1,1))]
    marker_list=['o','O','s','d','D','x','X','h','+','*','^','']
    tick_list=[ [0, 50, 100, 150, 200],[0.45, 0.3, 0.15, 0, -0.15],[0.60, 0.45, 0.30, 0.15, 0],[0.0, 0.25, 0.5, 0.75, 1.0],[1.95, 2.2, 2.45, 2.7, 2.95],[500,400,300,200,100],[-0.15,0.15,0.45,0.75,1.05],[1000,750,500,250,0.0],[0.1,1,10,100,1000],[0.2,2,20,200,2000],[0, 0.15, 0.30, 0.45, 0.60],
                [-0.75,-0.50,-0.25,0.0,0.25],[0,5,10,15,20],[300,200,100,0,-100],[150,200,250,350,400],[0,0.5,1,1.5,2],[1000,100,10,1,0.1],[2000,200,20,2,0.2],[1.65, 1.90, 2.15, 2.4, 2.65],[-2,0,2,4,6]]

    #create figure
    fig, axs  = pyplot.subplots(nrows=1, ncols=trcks , figsize=(13,20), sharey=True, num=title)
    fig.suptitle(title, fontsize=15)

    #General setting for all axis
    for axes in axs:
        axes.set_ylim(max_y,min_y)
        axes.yaxis.grid(True)
        axes.get_xaxis().set_visible(False)

        #adding Fm Tops

        if isinstance(formations, list):
            for (i,j) in formations:
                if ((float(j)>=min_y) and (float(j)<=max_y)):
                    axes.axhline(y=float(j), linewidth=1.0, color='blue')
                    axes.text(0.01, float(j) ,i, weight='bold', horizontalalignment='left',verticalalignment='top')
        else:
            for formation in formations.values():
                if formation.depth >= min_y and formation.depth <= max_y:
                    axes.axhline(y=formation.depth, linewidth=1.0, color='blue')
                    axes.text(0.01, formation.depth , formation.name, weight='bold', horizontalalignment='left',verticalalignment='top')

    # As our curve scales will be detached from the top of the track,
    # this code adds the top border back in without dealing with splines
    mx_crv=1                #count max curves per track
    cur_trk=1
    ax : list[Axes]=[]                   #Create list for axis
    lines=[]                #create a list of lines
    crv_idx=0
    for c in curvs:         # curvs in list of curves to be plotted with corresponding props
        f_idx=0             #reset fill curve index
        if crv_idx==0:      # first curve in first track
            pos=0  #position of spines
            ax.append(axs[0].twiny())
            ax[0].set_xlim(float(tick_list[props[crv_idx][2]][0]), float(tick_list[props[crv_idx][2]][4]))
            ax[0].minorticks_on()
            ax[0].grid(which='major', linestyle='-', linewidth='0.5', color='silver')
            ax[0].grid(which='minor', linestyle=':', linewidth='0.35', color='silver')
            ax[0].grid(True)
            ax[0].spines['top'].set_position(('outward',pos))
            ax[0].spines['top'].set_color(color_list[props[0][0]])
            ax[0].set_xlabel(c.name,color=color_list[props[0][0]])
            ax[0].set_ylabel('Depth (m)',color='black')
            ax[0].tick_params(axis='x', colors=color_list[props[0][0]])
            ax[crv_idx].title.set_color(color_list[props[crv_idx][0]])
            ax[crv_idx].set_xticks(tick_list[props[crv_idx][2]])

        else:
            #track as specified in property
            if props[crv_idx][5]!=cur_trk:  #next track
                cur_trk=int(props[crv_idx][5])
                pos=0  #position of spines
                ax.append(axs[cur_trk-1].twiny())
                ax[crv_idx].set_xlim(float(tick_list[props[crv_idx][2]][0]), float(tick_list[props[crv_idx][2]][4]))
                ax[crv_idx].minorticks_on()
                ax[crv_idx].grid(True)
                ax[crv_idx].grid(which='major', linestyle='-', linewidth='0.5', color='silver')
                ax[crv_idx].grid(which='minor', linestyle=':', linewidth='0.35', color='silver')
                ax[crv_idx].spines['top'].set_position(('outward',pos))
                ax[crv_idx].spines['top'].set_color(color_list[props[crv_idx][0]])
                ax[crv_idx].set_xlabel(c.name, color=color_list[props[crv_idx][0]])
                ax[crv_idx].tick_params(axis='x', colors=color_list[props[crv_idx][0]])
                ax[crv_idx].title.set_color(color_list[props[crv_idx][0]])
                ax[crv_idx].set_xticks(tick_list[props[crv_idx][2]])
            else:
                ax.append(axs[cur_trk-1].twiny())
                pos=pos+40
                if int(pos)>mx_crv:
                    mx_crv=pos
                ax[crv_idx].set_xlim(float(tick_list[props[crv_idx][2]][0]), float(tick_list[props[crv_idx][2]][4]))
                ax[crv_idx].spines['top'].set_position(('outward',pos))
                ax[crv_idx].spines['top'].set_color(color_list[props[crv_idx][0]])
                ax[crv_idx].set_xlabel(c.name, color=color_list[props[crv_idx][0]])
                ax[crv_idx].tick_params(axis='x', colors=color_list[props[crv_idx][0]])
                ax[crv_idx].title.set_color(color_list[props[crv_idx][0]])
                ax[crv_idx].set_xticks(tick_list[props[crv_idx][2]])

        if props[crv_idx][3]==1:
            ax[crv_idx].set_xscale('log',base=10, nonpositive='clip')

        if c.name in marklist:
            lines.append([0])
            lines[crv_idx] = ax[crv_idx].scatter(c,c.index, color = color_list[props[crv_idx][0]],label=c.name,marker=marker_list[props[crv_idx][4]])
        else:
            lines.append(0)
            if props[crv_idx][4]!=11:
                lines[crv_idx], = ax[crv_idx].plot(c,c.index, linestyle=line_list[props[crv_idx][1]] ,label=c.name, color = color_list[props[crv_idx][0]], marker=marker_list[props[crv_idx][4]])
            else:
                lines[crv_idx], = ax[crv_idx].plot(c,c.index, linestyle=line_list[props[crv_idx][1]] ,label=c.name, color = color_list[props[crv_idx][0]])

        #if fills are required

        if c.name=='FCFN':    #use default facies fills
            y1 = c
            fill_min=float(tick_list[props[crv_idx][2]][0])
            fill_max=float(tick_list[props[crv_idx][2]][4])
            y2=fill_min
            ax[crv_idx].fill_betweenx(c.index, y1,y2, where=(y1>y2) & (y1==0), interpolate=True, color='brown', alpha =0.3,linewidth=0)
            ax[crv_idx].fill_betweenx(c.index, y1,y2, where=(y1>y2) & (y1==1), interpolate=True, color='olive', alpha =0.3,linewidth=0)
            ax[crv_idx].fill_betweenx(c.index, y1,y2, where=(y1>y2) & (y1==2), interpolate=True, color='green', hatch=myhatches[3],alpha =0.3,linewidth=0)
            ax[crv_idx].fill_betweenx(c.index, y1,y2, where=(y1>y2) & (y1==3), interpolate=True, color='orange', alpha =0.3,linewidth=0)
            ax[crv_idx].fill_betweenx(c.index, y1,y2, where=(y1>y2) & (y1==4), interpolate=True, facecolor='yellow', hatch=myhatches[8], alpha =0.3,linewidth=0)

        c_flag = 0          # y2 is a curve Not a constant
        if props[crv_idx][6]==0:  #create fills
            y1 = c
            fill_min=float(tick_list[props[crv_idx][2]][0])
            fill_max=float(tick_list[props[crv_idx][2]][4])
            if props[crv_idx][7]== 'None':   #constant
                y2 = float(props[crv_idx][8])
                c_flag=1               #y2 is a constant
            else:                      # if curve
                #find AKA
                #y2=las_df[props[crv_idx][9]]
                y2=fcrvs[f_idx]

            if props[crv_idx][9]==0:     #if None
                ax[crv_idx].fill_betweenx(c.index, y1,y2, where=None, interpolate=True, color=props[crv_idx][10], alpha =float(props[crv_idx][11]),linewidth=0)
            if props[crv_idx][9]==1:   #if greater than
                y1.replace(fill_max)
                if c_flag==0:
                    y2.replace(fill_max)
                f_idx +=1
                f_idx +=1
                ax[crv_idx].fill_betweenx(c.index, y1,y2, where=(y1>=y2), interpolate=True, color=props[crv_idx][10], alpha =float(props[crv_idx][11]),linewidth=0)
            if props[crv_idx][9]==2:     #if Less than
                y1.replace(fill_min)
                if c_flag==0:
                    y2.replace(fill_min)
                ax[crv_idx].fill_betweenx(c.index, y1,y2, where=(y1< y2), interpolate=True, color=props[crv_idx][10], alpha =float(props[crv_idx][11]), linewidth=0)

        crv_idx +=1             #next curve

    # Start line interaction
    if pltype== _enumerables.DepthPlotType.DepthShift:               #enable coreshift
        global_vars.cr_shft.append(0)
        sh_line, =ax[1].plot([0], [0])  # empty line
        #fig.canvas.mpl_connect('button_press_event', lambda e: sh_onclick(e,sh_line))
        my_ann=ax[0].annotate('         To shift left click on GR track.',xy=(0.1, 0.95), xycoords='axes fraction',xytext=(0.1, 0.95), textcoords='axes fraction')
        multi = MultiCursor(fig.canvas, (ax), color='c', lw=2, horizOn=True, vertOn=False)
        linebuilder = LineBuilder(sh_line, curvs, lines, my_ann, props[4][0],marker_list[props[4][4]])

        #multi_cursor.active = False
        #multi.active=False
        #cursor accross several tracks

    #Create header space
    tp=0.85-(0.15/5*(mx_crv/40 + 1))      #Calculate header room
    fig.subplots_adjust(top=tp,hspace=0.5, wspace=0.2)

    if pltype != _enumerables.DepthPlotType.MutlipleDepthPlot:
        pyplot.show(block=True)
    elif pltype==_enumerables.DepthPlotType.MutlipleDepthPlot:
        fig.canvas.mpl_connect('button_press_event', lambda e: self.plotOnClick(e))

    #allows for user interaction
    if pltype==_enumerables.DepthPlotType.DepthShift:
        fig.canvas.mpl_disconnect(linebuilder)