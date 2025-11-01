import traceback
import warnings
from typing import TYPE_CHECKING

import matplotlib.axes
import matplotlib.cm
import matplotlib.figure
import matplotlib.pyplot as pyplot
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.widgets import RectangleSelector
from mpl_toolkits.axes_grid1.axes_divider import \
    make_axes_locatable  # for color bar

import defs.alert as alert
import defs.main as main
import global_vars
from classes.MinMaxScale import MinMaxScale
from classes.SelectFromCollection import SelectFromCollection
from defs.strtobool import strtobool
from enumerables import PlotType

if TYPE_CHECKING:
    from .. import Plot


def singleWellZPlot(self : 'Plot'):
    #Single Cross plot with Z axis


    global_vars.PF=[]
    global_vars.facies=0
    global_vars.tmp.append(0)
    self.axes.clear()

    # minimize graphs window
    self.graphingWindow.iconify()
    self.plotType = PlotType.ZPlot

    self.loadOrCreateSettings()

    #Get Image file
    overlayImageFile=self.settings.Get('overlay')
    for well in self.wellList.GetWells():
        self.resetDataFrames.clear()
        self.figures.clear()
        self.points.clear()


        #initialize dfs
        c1=pd.DataFrame(None)
        c2=pd.DataFrame(None)
        zc=pd.DataFrame(None)

        try:
            c1, c2, zc, well_loc = self.mtp_well_df(well)
        except Exception:
            print(traceback.format_exc())
            self.graphingWindow.deiconify()
            return
        
        #load plot data from LAS and/or core
        crv1=self.settings.Get('curve1')
        crv2=self.settings.Get('curve2')
        zcrv=self.settings.Get('zcurve')

        #set curves that need markers
        marklist=['KMAX','KVRT','K90',
        'CPOR','GDEN','BDEN','RSO','RSW']

        #check if c1 not empty
        if  c1.empty==True:
            continue            #skip to next well
        elif  c2.empty==True:
            continue            #skip to next well
        elif  zc.empty==True:
            continue            #skip to next well

        #zcolmap=Zplot_colors()      # get default colors for Z-axis scale
        zcolmap=matplotlib.cm.get_cmap('viridis_r')

        c1_scale=MinMaxScale.FromString(self.settings.Get('c1_scale'))
        c2_scale=MinMaxScale.FromString(self.settings.Get('c2_scale'))
        z_scale=MinMaxScale.FromString(self.settings.Get('z_scale'))

        #prepare for rect_selector
         #prepare for rect_selector
        def RctOnselect(eventClick, erelease):
            '''
            Obtain (xmin, xmax, ymin, ymax) values
            '''
            figure = eventClick.canvas.figure
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
            self.annotations[figure.number].set_text(f"Petrofacies {global_vars.facies}")
            #my_ann=ax[0].annotate(mtxt,xy=(0.1, 0.95), xycoords='axes fraction',xytext=(0.1, 0.95), textcoords='axes fraction')
            #my_anns[fignum-1]=my_ann
            #ax.figure.canvas.draw()

        #Create figure with subplots
        fig=pyplot.figure(f"{well.uwi}({well.alias}) - Curve {global_vars.SoftwareVersion}")       #not compatible with tight_layout? , constrained_layout=True
        self.figures.append(fig)
        self.resetDataFrames[fig.number] = [c1, c2, zc]

        widths = [3, 1, 1]
        heights = [1]
        spec = fig.add_gridspec(ncols=3, nrows=1, width_ratios=widths, height_ratios=heights)


        if self.axes:      # if ax was set clear them first
            self.axes.clear()                    #clear axes
        #Create a list of 3 axes
        self.axes= [                                         #Create a list of axes
            fig.add_subplot(spec[0,0]),
            fig.add_subplot(spec[0,1]),
            fig.add_subplot(spec[0,2])
        ]

        # NaN to zero in zc
        try:
            self.points[fig.number] = self.axes[0].scatter(c1, c2, c=zc, marker='o', cmap=zcolmap, vmin=z_scale.min, vmax=z_scale.max)           # Xplot  pts is needed to connect to colorbar
        except  Exception:
            Err_txt=f'{crv1} and {crv2} of {well.uwi}({well.alias}) have a different number of data points. Skip Well'
            alert.Error(Err_txt)
            continue      #skip well

        self.axes[0].set_xlabel(crv1)
        self.axes[0].set_ylabel(crv2)

        if c1_scale.base==10:
            self.axes[0].set_xscale('log', base=10, nonpositive='clip')
        if c2_scale.base==10:
            self.axes[0].set_yscale('log', base=10, nonpositive='clip')
            self.axes[0].set_ylim(float(c2_scale.min))    #Define limit data type first cast it on the Y axis
        if c2_scale.base==0:                 #linear scale
            self.axes[0].set_ylim(float(c2_scale.min), float(c2_scale.max))

        self.axes[0].set_xlim(c1_scale.min, c1_scale.max)
        #ax[0].set_xlim(left=-300, right=100)
        self.axes[0].set(title = f'Crossplot of {crv2} versus {crv1} with {zcrv} on z-axis. Press h for help')

        tl_deg=0
        t_line=()       #Empty tuple
        my_ann=self.axes[0].annotate('',xy=(0.05, 0.95), xycoords='axes fraction',xytext=(0.2, 0.95), textcoords='axes fraction')
        self.annotations[fig.number] = my_ann

        if self.settings.Get('trend') != 'none':
            t_line, = self.axes[0].plot(0,0, color='red')
            if self.settings.Get('trend')=='2nd':
                tl_deg=2
            elif self.settings.Get('trend')=='3rd':
                tl_deg=3
            else:
                tl_deg=1

            #trend analysis
            #drop_frame=DataFrame(None)
            drop_frame=c1.to_frame()
            drop_frame[crv2]=c2

            drop_df=drop_frame.dropna()
            x=drop_df[crv1].to_numpy()
            y=drop_df[crv2].to_numpy()
            #y=np.log(y)
            #obtain m (slope) and b(intercept) of linear regression line
            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    if tl_deg==1 and x.any():                #linear regression
                        slop, interc = np.polyfit(x, y, tl_deg)
                        x1=np.min(x)
                        x2=np.max(x)
                        y1=slop*x1+interc
                        y2=slop*x2+interc
                        t_line.set_data([x1,x2],[y1,y2])
                        slope=round(slop,3)
                        intercept=round(interc,3)
                        mytxt=f"{c1.name}x{slope:.3f} + {intercept:.2f}"
                    elif tl_deg==2  and x.any():              #Squared regression
                        p = np.polyfit(x, y, tl_deg)
                        predict = np.poly1d(p)
                        myx=[]
                        myy=[]
                        myx.append(np.min(x))
                        myy.append(np.max(x))
                        mystep=(myy[0]-myx[0])/10
                        myy[0]=predict(myx[0])
                        for id in range(1,11):
                            myx.append(myx[id-1]+mystep)
                            myy.append(predict(myx[id]))
                            t_line.set_data(myx,myy)
                        #y=ax**2+bx+c
                        mytxt=f"{p[0]:.1f}x{c1.name}^2 + {p[1]:.1f}x{c1.name} + {p[2]:.1f}"
                    elif tl_deg==3 and x.any():              #Squared regression
                        p = np.polyfit(x, y, tl_deg)
                        predict = np.poly1d(p)
                        myx=[]
                        myy=[]
                        myx.append(np.min(x))
                        myy.append(np.max(x))
                        mystep=(myy[0]-myx[0])/10
                        myy[0]=predict(myx[0])
                        for id in range(1,11):
                            myx.append(myx[id-1]+mystep)
                            myy.append(predict(myx[id]))
                            t_line.set_data(myx,myy)
                        #y=ax**3+bx**2+cx+d
                        mytxt=f"{p[0]:.1f}x{c1.name}^3 + {p[1]:.1f}x{c1.name}^2 + {p[2]:.1f}x{c1.name}+{p[2]:.1f}"
                except np.RankWarning:
                    alert.Error("lower polyfit degree")
                except Exception:
                    alert.Error("polyfit problem - try lower degree")
            #update annotation
            my_ann.set_text(mytxt)

        # create an colorbar on the right side of ax.
        divider = make_axes_locatable(self.axes[0])
        cax = divider.append_axes("right", size="5%", pad=.05)
        cb = fig.colorbar(self.points[fig.number],ax=self.axes[0],cax=cax)
        cb.set_label(label=zcrv)
        cb.ax.tick_params(axis='y', direction='in')

        # Make two depth plots
        self.axes[2].sharey=self.axes[1]        #in case two depth tracks are require

        if c1_scale.base==10:
            self.axes[1].set_xscale('log', base=10, nonpositive='clip')
            self.axes[1].set_xlim(c1_scale.min, c1_scale.max)

        if c1_scale.base==0:                 #linear scale
            self.axes[1].set_xlim(c1_scale.min, c1_scale.max)

        if c2_scale.base==10:
            self.axes[2].set_xscale('log', base=10, nonpositive='clip')
            self.axes[2].set_xlim(c2_scale.min, c2_scale.max)    #Define limit data type first cast it on the Y axis
        if c2_scale.base==0:                 #linear scale
            self.axes[2].set_xlim(c2_scale.min, c2_scale.max)

        if crv1 in marklist:
            self.axes[1].scatter(c1, c1.index, color=self.settings.Get('c1_col'), marker='o')
            dpt_line, =self.axes[1].plot([0], [0], color=self.settings.Get('c2_col'), marker='o')  # empty line for polygon point locator
        else:
            self.axes[1].plot(c1, c1.index, color=self.settings.Get('c1_col'), linestyle= self.settings.Get('c1_type'), linewidth=self.settings.Get('c1_width'))
            dpt_line, =self.axes[1].plot([0], [0], color=self.settings.Get('c2_col'))  # empty line for polygon point locator

        self.axes[1].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        self.axes[1].set(title = "Track 1", xlabel = crv1, ylabel='DPT')      #
        self.axes[1].tick_params(labelleft=False, labelright=False)

        if crv2 in marklist:
            self.axes[2].scatter(c2, c2.index, color=self.settings.Get('c2_col'), marker='o')
        else:
            self.axes[2].plot(c2, c2.index, color=self.settings.Get('c2_col'), linestyle= self.settings.Get('c2_type'), linewidth=self.settings.Get('c2_width'))
        self.axes[2].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        self.axes[2].set(title = "Track 2", xlabel = crv2)

        # Grids on
        self.axes[0].grid(True)
        self.axes[1].grid(True)
        self.axes[2].grid(True)

        if overlayImageFile != '':
            img = pyplot.imread(overlayImageFile)
            self.axes[0].imshow(img, extent= [c1_scale.min,c1_scale.max,c2_scale.min,c2_scale.max])                  #, extent=[-5, 80, -5, 30]




        # add extra column to displayed polygon on depth plot
        c1_df=c1.to_frame()
        c1_df['HI']=np.nan

        self.rect_selectors[fig.number] = RectangleSelector(self.axes[0], RctOnselect,  button=[1])
        self.rect_selectors[fig.number].set_active(False)

        self.selectors[fig.number]  = SelectFromCollection(self.axes, self.points[fig.number], t_line, c1_df, dpt_line ,tl_deg, my_ann, self.settings.Get('c1_col'))\
        
        fig.canvas.mpl_connect('button_press_event', lambda e: self.plotOnClick(e))
        fig.canvas.mpl_connect('key_release_event', lambda k: self.plotOnKey(k, zc, well))

        fig.tight_layout()
        self.axes[0].set_aspect('auto')

        pyplot.show(block=True)
        main.PetroFacies(crv1, crv2, self.settings.Get('zone'))     #load, update and save PetroFacies
        #selectors[0].disconnect()

    #restore graphs window
    global_vars.tmp=[]          #reset tmp
    self.graphingWindow.deiconify()
