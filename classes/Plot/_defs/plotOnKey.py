
from typing import TYPE_CHECKING

import matplotlib.cm
import matplotlib.pyplot as pyplot
from matplotlib.backend_bases import KeyEvent


import defs.main as main
import defs.alert as alert

from classes.MinMaxScale import MinMaxScale
import global_vars
from enumerables import PlotType, Help


if TYPE_CHECKING:
    from .. import Plot
    from classes.Project.Well import Well
    from classes.SelectFromCollection import SelectFromCollection
    from matplotlib.widgets import RectangleSelector

def plotOnKey(self : 'Plot', event : KeyEvent, zc = '', well : 'Well' = None):
    '''
    On Key press
    Graph manipulation keys    e = event    l= draw line   d= set discriminators  b = bracket PetroFacies

    parms:e,fg, ax, pts, selectors, rect_selectors, zc, plt_set
    '''
    figure = event.canvas.figure

    if event.key=='h':
        #open help file.
        main.c_help(Help.Graph)
        return

    #Set active figure
    if figure.number>len(global_vars.project.currentWellList):   #more figures than there are wells in the Well_List
        print('WARNING: CLOSING FIGURES, more figures than wells')
        pyplot.close('all')
        return
    
    pyplot.figure(figure)                  #set active figure
    ax_idx=(figure.number-1)*3
    pts=self.points[figure.number]
    #find well number of selected figure

    
    if event.key=='d' and self.mlti_f == False:          #mlti flag = on:                   #discriminator selected
        c1 = self.resetDataFrames[figure.number][0]
        c2 = self.resetDataFrames[figure.number][1]

        if self.plotType==PlotType.ZPlot:
            zc = self.resetDataFrames[figure.number][2]

        #get discriminator
        disc1, disc2, min1, max1, min2, max2 = self.get_discriminator(well)

        ax_idx=(figure.number)*3   #get axis
        #Reset
        if global_vars.tmp!=[]:
            global_vars.tmp=[]

            pts=self.points[figure.number]
            if pts.axes!=None:
                pts.remove()
            if self.plotType==PlotType.ZPlot:
                zcolmap=matplotlib.cm.get_cmap('viridis_r')

                z_scale=self.settings.Get('z_scale')
                z_scale = MinMaxScale.FromString(z_scale)

                pts=self.axes[ax_idx].scatter(c1, c2, c=zc, marker='o', cmap=zcolmap, vmin=z_scale.min, vmax=z_scale.max)
            else:
                pts=self.axes[ax_idx].scatter(c1,c2, marker='o', color=self.settings.Get('c1_col'))
            self.axes[ax_idx].figure.canvas.draw()
            return

        cd1=c1.copy()     #original c1
        cd2=c2.copy()     #original c2
        if self.plotType==PlotType.ZPlot:           # get zc colors
            zc1=zc.copy()   #original zc

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
            cd2=cd2[disc1>min1]
            cd2=cd2[disc1<max1]
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
            cd2=cd2[disc2>min2]
            cd2=cd2[disc2<max2]

        if cd1.empty==True:             #if all data points are filtered out
            alert.Error(f"All data points in {well.uwi}({well.alias}) have been filtered out. Select other discriminators")
            return

        #update the graph
        #axs=pyplot.gca()
        pts=self.points[figure.number]
        if self.axes[ax_idx]!=None:
            pts.remove()
        if self.plotType==PlotType.ZPlot:
            #zcolmap=Zplot_colors()      # get default colors for Z-axis scale
            zcolmap=matplotlib.cm.get_cmap('viridis_r')
            z_scale=MinMaxScale.FromString(self.settings.Get('z_scale'))

            if disc1.empty==False:
                zc1=zc1[disc1>min1]
                zc1=zc1[disc1<max1]
            if disc2.empty==False:
                zc1=zc1[disc2>min2]
                zc1=zc1[disc2<max2]
            if len(cd1)!=len(cd2) or len(cd1)!=len(zc1):
                alert.Error(f"{cd1.name}, {cd2.name} or {zc1.name} have not the same number of data points")
                return
            pts=self.axes[ax_idx].scatter(cd1, cd2, c=zc1, marker='o', cmap=zcolmap, vmin=z_scale.min, vmax=z_scale.max)
        else:
            if len(cd1)!=len(cd2):
                alert.Error(f"{cd1.name} and {cd2.name} have not the same number of data points")
                return
            pts=self.axes[ax_idx].scatter(cd1,cd2, marker='o', color=self.settings.Get('c1_col'))
        figure.canvas.draw()

    elif event.key=='l':                  #line drawer selected
        
        if figure.number in self.selectors and self.selectors[figure.number] is not None: 
            self.selectors[figure.number].disconnect()

        my_ann=self.annotations[figure.number]
        my_ann.set_text('click on start and end of line')
        #figure.canvas.draw()
        #self.axes[ax_idx].figure.canvas.draw()

        #xy = self.drawLine(self.axes[ax_idx], figure.number)
        xy = self.drawLine(figure.axes[0], figure.number)
        if xy == []:
            return
        #calculate line algortihm
        x = [p[0] for p in xy]
        y = [p[1] for p in xy]
        mslope=(y[1]-y[0])/(x[1]-x[0])
        mintc=y[1]-mslope*x[1]
        mtxt=f" Y = {round(mslope,6)}X + {round(mintc,6)}"
        my_ann.set_text(mtxt)
        figure.canvas.draw()
        #ax[ax_idx].figure.canvas.draw()
        #tmp[0]=1

        #c1_df=c1.to_frame()
        #selectors[fignum-1].connect()

    elif event.key=='b':

        global_vars.PF=[]               #Reset Petro Facies
        global_vars.facies=0            #Petrofacies index

        self.annotations[figure.number].set_text("Select upper corner;\n drag and release mouse")
        figure.canvas.draw()
        if figure.number in self.selectors and self.selectors[figure.number] is not None: 
            self.selectors[figure.number].disconnect()

        self.rect_selectors[figure.number].set_active(True)
    return