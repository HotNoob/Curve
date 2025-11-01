import traceback
import warnings
from typing import TYPE_CHECKING

import matplotlib.pyplot as pyplot
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.widgets import RectangleSelector

import defs.alert as alert
import defs.main as main
import global_vars
from classes.MinMaxScale import MinMaxScale
from classes.SelectFromCollection import SelectFromCollection
from enumerables import PlotType

if TYPE_CHECKING:
    from .. import Plot


def multiWellCrossPlot(self : 'Plot'):
    '''
    Multi well Cross plot
    '''


    self.mlti_f = True           #mlti flag = on

    global_vars.PF=[]
    global_vars.facies=0
    global_vars.tmp.append(0)
    self.axes.clear()
    self.figures.clear()
    self.points.clear()
    self.resetDataFrames.clear()
    self.annotations.clear()

    # minimize graphs window
    self.graphingWindow.iconify()
    self.plotType = PlotType.CrossPlot


    self.loadOrCreateSettings()
    

    #initialize dfs
    c1=pd.DataFrame(None)
    c2=pd.DataFrame(None)

    try:
        c1, c2 = self.mlt_well_df(self.wellList)
    except Exception:
        print(traceback.format_exc())
        self.graphingWindow.deiconify()
        self.mlti_f=False #reset
        return

    #Get Image file
    overlayImageFile=self.settings.Get('overlay')

    #load plot data from LAS and/or core
    #check if crvs are in cdescrvs
    crv1=self.settings.Get('curve1')
    crv2=self.settings.Get('curve2')

    c1_scale=MinMaxScale.FromString(self.settings.Get('c1_scale'))
    c2_scale=MinMaxScale.FromString(self.settings.Get('c2_scale'))

    #check if c1 not empty
    if  c1.empty==True:
        return
    elif  c2.empty==True:
        return        #skip to next well

    #prepare for rect_selector
    def RctOnselect(eventClick, erelease):
        '''
        Obtain (xmin, xmax, ymin, ymax) values
        '''
        figure  = eventClick.canvas.figure

        # Obtain (xmin, xmax, ymin, ymax) values
        # for rectangle selector box using extens attribute.
        sqextent = self.rect_selectors[figure.number].extents
        fname='PF'+ str(global_vars.facies)
        global_vars.PF.append([fname,c1.name,c2.name,sqextent])
        global_vars.facies +=1

        if global_vars.facies>4:     #end of petrofacies list
            self.rect_selectors[figure.number].set_active(False)

        #Draw box
        width=sqextent[1]-sqextent[0]
        height=sqextent[3]-sqextent[2]
        rect=Rectangle((sqextent[0],sqextent[2]),width, height, fill = False)
        self.axes[0].add_patch(rect)
        mtxt=f"Petrofacies {global_vars.facies}"
        my_ann=self.annotations[figure.number]    #get last annotation
        my_ann.set_text(mtxt)
        #my_ann=ax[0].annotate(mtxt,xy=(0.1, 0.95), xycoords='axes fraction',xytext=(0.1, 0.95), textcoords='axes fraction')
        #my_anns[fignum-1]=my_ann
        #ax.figure.canvas.draw()

    # create figure
    fig = pyplot.figure('All Wells'+ ' - Curve '+global_vars.SoftwareVersion, constrained_layout=True)
    self.figures.append(fig)
    self.resetDataFrames[fig.number] = [c1,c2]


    self.axes= [                         #Create figure with one axes
            fig.add_subplot(111)
        ]

    try:
        self.points[fig.number] = self.axes[0].scatter(c1, c2, marker='o', color=self.settings.Get('c1_col'))    # Xplot
    except  Exception:
        Err_txt=f'{crv1} and {crv2} have a different number of data points.'
        alert.Error(Err_txt)
        return

    dpt_line, =self.axes[0].plot([0], [0], color=self.settings.Get('c2_col'))  # empty line for polygon point locatorNOT used here
    self.axes[0].set_xlabel(crv1)
    self.axes[0].set_ylabel(crv2)

    if c1_scale.base==10:
        self.axes[0].set_xscale('log', base=10, nonpositive='clip')
    if c2_scale.base==10:
        self.axes[0].set_yscale('log', base=10, nonpositive='clip')
        self.axes[0].set_ylim(c2_scale.min)    #Define limit data type first cast it on the Y axis
    if c2_scale.base==0:                 #linear scale
        self.axes[0].set_ylim(c2_scale.min, c2_scale.max)

    self.axes[0].set_xlim(c1_scale.min, c1_scale.max)
    self.axes[0].set(title = f'Crossplot of {crv2} versus {crv1}. Press h for help')

    #Create trendline or not
    t_line, = self.axes[0].plot(0,0, color='red')
    tl_deg=0
    my_ann=self.axes[0].annotate('',xy=(0.2, 0.95), xycoords='axes fraction',xytext=(0.2, 0.95), textcoords='axes fraction')
    self.annotations[fig.number] = my_ann
    mytxt="Use polygon to select data or press the other key commands"

    if self.settings.Get('trend') != 'none':
        if self.settings.Get('trend')=='2nd':
            tl_deg=2
        elif self.settings.Get('trend')=='3rd':
            tl_deg=3
        else:
            tl_deg=1

        #trend analysis
        x=c1.to_numpy()
        y=c2.to_numpy()
        #obtain m (slope) and b(intercept) of linear regression line
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            try:
                slop, interc = np.polyfit(x, y, tl_deg)
                t_line.set_data(x, slop*x+interc)
                slope=round(slop,2)
                intercept=round(interc,3)
                mytxt=f"{c1.name}x{slope} +{intercept}"
                my_ann.set_text(mytxt)
            except np.RankWarning:
                alert.Error("lower polyfit degree")
            except Exception:
                alert.Error("polyfit problem - try lower degree")
        #update annotation
        my_ann.set_text(mytxt)

    if overlayImageFile != '':
        img = pyplot.imread(overlayImageFile)
        self.axes[0].imshow(img, extent= [c1_scale.min,c1_scale.max,c2_scale.min,c2_scale.max])                  #, extent=[-5, 80, -5, 30]

    # add extra column to displayed polygon on depth plot
    # add extra column to displayed polygon on depth plot
    c1_df=c1.to_frame()
    c1_df['HI']=np.nan

    self.rect_selectors[fig.number] = RectangleSelector(self.axes[0], RctOnselect, button=[1])
    self.rect_selectors[fig.number].set_active(False)

    self.selectors[fig.number] = SelectFromCollection(self.axes, self.points[fig.number], t_line, c1_df, dpt_line ,tl_deg, my_ann, self.settings.Get('c1_col'))

    fig.canvas.mpl_connect('button_press_event', lambda e: self.plotOnClick(e))
    fig.canvas.mpl_connect('key_release_event', lambda k:  self.plotOnKey(k))



    
    # Grids on
    self.axes[0].grid(True)

    #ax[0].set_aspect(0.5)
    pyplot.show(block=True)
    main.PetroFacies(crv1, crv2, self.settings.Get('zone'))     #load, update and save PetroFacies
    #selector.disconnect()
    # restore graphs window
    global_vars.tmp=[]          #reset tmp
    self.mlti_f=False  #reset
    self.graphingWindow.deiconify()
