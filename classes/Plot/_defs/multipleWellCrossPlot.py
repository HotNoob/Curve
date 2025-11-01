import traceback
import warnings
from typing import TYPE_CHECKING

import matplotlib.pyplot as pyplot
import numpy as np
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


def multipleWellCrossPlot(self : 'Plot'):
    '''
    Multiple well Cross plot
    '''
    global_vars.PF=[]
    global_vars.facies=0
    global_vars.tmp.append(0)
    self.axes.clear()
    self.figures.clear()
    self.points.clear()
    self.resetDataFrames.clear()
    self.annotations.clear()
    ax_idx=0
    fg_idx=1

    # minimize graphs window
    self.graphingWindow.iconify()
    self.plotType = PlotType.CrossPlot

    self.loadOrCreateSettings()

    #Get Image file
    overlayImageFile=self.settings.Get('overlay')

    for well in self.wellList.GetWells():
        try:
            c1, c2, well_loc = self.mtp_well_df(well)
        except Exception:
            print(traceback.format_exc())
            self.graphingWindow.deiconify()
            return

        #set curves that need markers
        marklist=['KMAX','KVRT','K90',
        'CPOR','GDEN','BDEN','RSO','RSW']

        #check if c1 not empty
        if  c1.isnull().all():
            continue            #skip to next well
        elif  c2.isnull().all():
            continue            #skip to next well

        c1_scale=MinMaxScale.FromString(self.settings.Get('c1_scale'))
        c2_scale=MinMaxScale.FromString(self.settings.Get('c2_scale'))

        #prepare for rect_selector(s)
        def RctOnselect(eventClick, eventRelease):

            #get annotation for current figure
            figure = eventClick.canvas.figure
            
            pyplot.figure(f'{figure.number} - Curve {global_vars.SoftwareVersion}')
            ax_idx=(figure.number-1)*3

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
            self.axes[ax_idx].add_patch(rect)

            self.annotations[figure.number].set_text(f"Petrofacies {global_vars.facies}")

        #Create figure with subplot
        fig=pyplot.figure(f"{well.uwi}({well.alias}) - Curve {global_vars.SoftwareVersion}")
        self.figures.append(fig)
        #set reset curve list
        self.resetDataFrames[fig.number] = [c1,c2]

        #create first annotation
        widths = [3, 1, 1]
        heights = [1]
        spec = self.figures[fg_idx-1].add_gridspec(ncols=3, nrows=1, width_ratios=widths, height_ratios=heights)
                #clear axes
        #Create a list of 3 axes
        self.axes.append(self.figures[fg_idx-1].add_subplot(spec[0,0]))
        self.axes.append(self.figures[fg_idx-1].add_subplot(spec[0,1]))
        self.axes.append(self.figures[fg_idx-1].add_subplot(spec[0,2]))

        crv1=c1.name
        crv2=c2.name

        try:
            self.points[fig.number] = self.axes[ax_idx].scatter(c1, c2, marker='o', color=self.settings.Get('c1_col'))           # Xplot

        except  Exception:
            Err_txt=f'{crv1} and {crv2} of {well.uwi}({well.alias}) have a different number of data points. Skip Well'
            alert.Error(Err_txt)
            continue      #skip well

        self.axes[ax_idx].set_xlabel(crv1)
        self.axes[ax_idx].set_ylabel(crv2)

        if c1_scale.base==10:
                self.axes[ax_idx].set_xscale('log', base=10, nonpositive='clip')

        if c2_scale.base==10:
            self.axes[ax_idx].set_yscale('log', base=10, nonpositive='clip')

        #Define limits
        self.axes[ax_idx].set_xlim(c1_scale.min, c1_scale.max)
        self.axes[ax_idx].set_ylim(c2_scale.min, c2_scale.max)

        self.axes[ax_idx].set(title = 'Crossplot of '+ crv2 +' versus ' + crv1)

        #trend analysis (or not)
        tl_deg=0
        t_line=()       #Empty tuple
        my_ann = self.axes[ax_idx].annotate('',xy=(0.05, 0.95), xycoords='axes fraction',xytext=(0.2, 0.95), textcoords='axes fraction')
        self.annotations[fig.number] = my_ann
        mytxt=''

        if self.settings.Get('trend') != 'none':
            t_line, = self.axes[ax_idx].plot(0,0, color='red')
            if self.settings.Get('trend')=='2nd':
                tl_deg=2
            elif self.settings.Get('trend')=='3rd':
                tl_deg=3
            else:
                tl_deg=1

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
                    elif tl_deg==2 and x.any():              #Squared regression
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
                    my_ann.set_text(mytxt)
                except np.RankWarning:
                    alert.Error("lower polyfit degree")
                except Exception:
                    alert.Error("polyfit problem - try lower degree")

        # Make two depth plots
        self.axes[ax_idx+2].sharey=self.axes[ax_idx+1]        #in case two depth tracks are required
        if crv1 in marklist:
            self.axes[ax_idx+1].scatter(c1, c1.index, color=self.settings.Get('c1_col'), marker='o')
            dpt_line, =self.axes[ax_idx+1].plot([0], [0], color=self.settings.Get('c2_col'), marker='o')  # empty line for polygon point locator
        else:
            self.axes[ax_idx+1].plot(c1, c1.index, color=self.settings.Get('c1_col'), linestyle= self.settings.Get('c1_type'), linewidth=self.settings.Get('c1_width'))
            dpt_line, =self.axes[ax_idx+1].plot([0], [0], color=self.settings.Get('c2_col'))  # empty line for polygon point locator
        self.axes[ax_idx+1].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        self.axes[ax_idx+1].set(title = "Track 1", xlabel = crv1, ylabel='DPT')
        self.axes[ax_idx+1].tick_params(labelleft=False, labelright=False)

        if crv2 in marklist:
            self.axes[ax_idx+2].scatter(c2, c2.index, color=self.settings.Get('c2_col'), marker='o')
        else:
            self.axes[ax_idx+2].plot(c2, c2.index, color=self.settings.Get('c2_col'), linestyle= self.settings.Get('c2_type'), linewidth=self.settings.Get('c2_width'))
        self.axes[ax_idx+2].set_ylim(self.zoneDepths.base, self.zoneDepths.top)   # reverses depth scale to shallow at top
        self.axes[ax_idx+2].set(title = "Track 2", xlabel = crv2)
        self.axes[ax_idx+2].tick_params(labelleft=False, labelright=True)

        if overlayImageFile != '':
            img = pyplot.imread(overlayImageFile)
            self.axes[ax_idx].imshow(img, extent= [float(c1_scale.min),float(c1_scale.max),float(c2_scale.min),float(c2_scale.max)])

        # Grids on
        self.axes[ax_idx].grid(True)
        self.axes[ax_idx+1].grid(True)
        self.axes[ax_idx+2].grid(True)

        # add extra column to displayed polygon on depth plot
        c1_df=c1.to_frame()
        c1_df['HI']=np.nan
        self.rect_selectors[fig.number] = RectangleSelector(self.axes[ax_idx], RctOnselect, button=[1])
        self.rect_selectors[fig.number].set_active(False)     #deactivate current rect_selector

        self.selectors[fig.number] = SelectFromCollection([self.axes[ax_idx],self.axes[ax_idx+1]], self.points[fig.number], t_line, c1_df, dpt_line ,tl_deg, my_ann, self.settings.Get('c1_col'))

        fig.canvas.mpl_connect('button_press_event', lambda e: self.plotOnClick(e))
        fig.canvas.mpl_connect('key_release_event', lambda k:  self.plotOnKey(k, '', well))

        self.axes[ax_idx].set_aspect('auto')

        fg_idx +=1
        ax_idx +=3

    #fig.tight_layout()
    pyplot.show(block=True)

    main.PetroFacies(crv1, crv2, self.settings.Get('zone'))     #load, update and save PetroFacies

    #for s_idx in range(fg_idx-1):
        #selectors[s_idx].disconnect()

    # restore graphs window
    self.graphingWindow.deiconify()
