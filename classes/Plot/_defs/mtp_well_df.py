import glob
import os
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

import defs.alert as alert
import defs.excel as excel
import defs.las as las
import defs.main as main
import global_vars
from enumerables import Dir, PlotType
from structs import ZoneDepths

if TYPE_CHECKING:
    from .. import Plot
    from classes.Project.Well import Well


def mtp_well_df(self : 'Plot', well : 'Well'):
    '''
    Load multiple_well data frames for plotting or scripts

    '''
    global_vars.perfTest.Start("mtp_well_df_total")

    # get wells with core (i.e. have cas files in Indir)
    curDir = os.getcwd()
    os.chdir(global_vars.project.inDir)
    casFiles = glob.glob("*.cas")
    os.chdir(curDir)

    #Get Default.plot type: xp, hg, 3d  zp or pk
    self.LoadDefaultSettings()
    
    zone=self.settings.Get('zone')

    self.zoneDepths = well.GetZoneDepths(zone)
    print(f"Zone top: {self.zoneDepths.top} bottom: {self.zoneDepths.base}")
    
    crv_list=[] ## used in line 146
    numberOfCurves : int = 1
    curveNames : dict[str, str] = {}
    curveDataFrames : dict [str, pd.DataFrame] = {}


    #convert settings to work with array
    if self.plotType==PlotType.ZPlot:
        self.settings.Set('curve3', self.settings.Get('zcurve'))
        numberOfCurves = 3
    elif self.plotType==PlotType.ThreeDPlot:
        self.settings.Set('curve4', self.settings.Get('zcurve'))
        numberOfCurves = 4
    elif self.plotType==PlotType.PK:
        self.settings.Set('curve3', self.settings.Get('zcurve'))
        self.settings.Set('curve3_dir', self.settings.Get('zcurve_dir'))
        self.settings.Set('curve4', self.settings.Get('cp_crv'))
        self.settings.Set('curve4_dir', self.settings.Get('cp_crv_dir')) #note this should always Dir.Out,
        numberOfCurves = 4
    elif self.plotType==PlotType.Histogram:
        numberOfCurves = 1
    else :
        numberOfCurves = 2

    #for easy of simplicity, because settings starts with 1, we are using 1 in a dict instead of 0 in a list. thus, ranges/for loops should start with 1 and len +1
    for i in range(1, numberOfCurves + 1):
        curveNames[i] = self.settings.Get('curve'+str(i))
        curveDataFrames[i] = pd.DataFrame(None)

    ''' not needed; we can just load on demand
    loadCas : bool = False
    for i in range(1, numberOfCurves + 1):
        if(curveNames[i] in globals.cdescrvs):
            loadCas = True
            break
    '''

    #load plot data from LAS
    las_data = well.GetLASData(Dir.In)

    step=las_data.well.step.value
    ls_strt=las_data.well.strt.value
    ls_stop=las_data.well.stop.value
    well_loc=las_data.well.loc.value


    if step == 0: #if for whatever reason is 0, try 0.1
        step = 0.1
        print("Warning: Invalid Step, Using 0.1 as Step")

    if zone != 'CORE':         #if not core then set LAS depth interval
        #set depth interval
        zone=self.settings.Get('zone')

    if zone=='WELL':
        self.zoneDepths = ZoneDepths(top=ls_strt, base=ls_stop, name=zone)

    #set depth interval
    idx_top=int((self.zoneDepths.top - ls_strt)/step)
    idx_bot=int((self.zoneDepths.base - ls_strt)/step)+1  #get very last of array

    core_df = pd.DataFrame(None)

    cr_idx_top=0 #this appears to be always 0
    cr_idx_bot=0    # end core

    def LoadCas():
        #ensure well is also in Well List
        wname=well.uwi+'.cas'
        if wname in casFiles:
            #get cas_data and create core_df
            curDir=os.getcwd()
            os.chdir(global_vars.project.inDir)
            cas_data = global_vars.LASCache.GetLASData(wname)
            os.chdir(curDir)
            core_df=cas_data.df()
            core_df.replace(-999.25, np.NaN, inplace=True)
            #get cas_data and create core_df
            c_start=cas_data.well.strt.value
            c_stop=cas_data.well.stop.value
            cr_shft=cas_data.params.csh.value
            # shift core in df
            cshift=round(round(cr_shft/0.1,0)*0.1,1)
            core_df.index=core_df.index+cshift

            if self.zoneDepths.top < c_start and self.zoneDepths.base>c_start:  #If core in selected zone
                zone='CORE'
                self.zoneDepths = ZoneDepths(top=c_start+cshift, base=c_stop+cshift, name=zone)
            else:     #core not in selected zone Next Well
                alert.Error(f'Tops not in {well.uwi}({well.alias}) - remove from well list')
                return

            cr_idx_bot=len(core_df.index) #get very last of array
            return core_df,cr_idx_top,cr_idx_bot

    lasDataFrames = {}        # LasDataFrames Dictionary
    lasDataFrames[Dir.Out] = pd.DataFrame(None)
    lasDataFrames[Dir.In] =  pd.DataFrame(None)

    ccrv=[]   #list of core curves in plot

    #load las data
    for i in range(1, numberOfCurves+1):
        if curveNames[i] in global_vars.cdescrvs: #Core data
            #ensure same core curve df and las curve df length and start
            ccrv.append(i)
            if core_df.empty :
                core_df, cr_idx_top,cr_idx_bot=LoadCas() #load here, so we dont load it if we dont need too
            curveDataFrames[i] = core_df[curveNames[i]] #Add to curveDataFrames
            if cr_idx_bot-cr_idx_top > idx_bot - idx_top:   #If core interval larger than log interval
                cr_idx_bot=idx_bot
                curveDataFrames[i] = curveDataFrames[i].iloc[cr_idx_top:cr_idx_bot]

        else: #Indir or Outdir data
            if os.path.realpath(self.settings.Get('curve'+str(i)+'_dir'))==os.path.realpath(global_vars.project.outDir):
                #calculated curves. no aliases
                if lasDataFrames[Dir.Out].empty:
                    crv_list=global_vars.CalcCurveNames

                    lasDataFrames[Dir.Out]=well.GetLASData(Dir.Out).df()
                    lasDataFrames[Dir.Out].replace(-999.25, np.NaN, inplace=True)
                    lasDataFrames[Dir.Out] = lasDataFrames[Dir.Out].iloc[idx_top:idx_bot] #because idx_top and bottom never change we can trim this ONCE
                df = lasDataFrames[Dir.Out]
                name = curveNames[i]
                curveDataFrames[i] = lasDataFrames[Dir.Out][curveNames[i]]
            elif os.path.realpath(self.settings.Get('curve'+str(i)+'_dir'))==os.path.realpath(global_vars.project.inDir):
                #check INDIR
                if lasDataFrames[Dir.In].empty:
                    lasDataFrames[Dir.In]=well.GetLASData(Dir.In).df()
                    lasDataFrames[Dir.In].replace(-999.25, np.NaN, inplace=True)
                    lasDataFrames[Dir.In] = lasDataFrames[Dir.In].iloc[idx_top:idx_bot] #because idx_top and bottom never change we can trim this ONCE
                df = lasDataFrames[Dir.In]
                name = curveNames[i]
                #get aka
                #name = global_vars.project.curveNameTranslator.GetName(curveNames[i]) #ensure the input name is not an alias. otherwise fetch the propper name
                aliasList = global_vars.project.curveNameTranslator.GetAliases(name)
                for alias in aliasList:
                    if alias in df.columns:
                        name = alias
                        break
                curveDataFrames[i] = lasDataFrames[Dir.In][name]
            else: 
                mDir=os.path.realpath(self.settings.Get('ZCURVE_DIR')) #if ZCURVE
                if mDir=='LAS_Out':
                    mDir=Dir.In
                else:
                    mDir=Dir.Out
                if lasDataFrames[mDir].empty:
                    lasDataFrames[mDir]=well.GetLASData(mDir).df()
                    lasDataFrames[mDir].replace(-999.25, np.NaN, inplace=True)
                    lasDataFrames[mDir] = lasDataFrames[mDir].iloc[idx_top:idx_bot] #because idx_top and bottom never change we can trim this ONCE
                df = lasDataFrames[mDir]
                name = curveNames[i]
                curveDataFrames[i] = lasDataFrames[mDir][curveNames[i]]

        if curveDataFrames[i].empty:
            alert.Error(f"{curveNames[i]} ({name}) was not in {well.uwi}({well.alias})")
            main.show_las(well.uwi + ".las")
            global_vars.perfTest.Stop("mtp_well_df_total")
            return

    if len(ccrv)>0: #adjust for curve depth in dataframes
        for i in range(1, numberOfCurves+1):
            #set all curves to core interval
            if i not in ccrv: 
                #df=curveDataFrames[i].__deepcopy__()
                for ix in range(len(curveDataFrames[i])):
                    if curveDataFrames[i].index[ix]>=curveDataFrames[ccrv[0]].index[0]:
                        endix=ix+cr_idx_bot #end of core in curveFDataFrames
                        if endix>idx_bot:   #If core longer than curveFrames[i]
                            endix=idx_bot
                        
                        df=curveDataFrames[i].iloc[ix:endix].__deepcopy__()
                        curveDataFrames[i]=df.__deepcopy__()
                        break


    #globals.project.outDir holds calculated curves!

    global_vars.perfTest.Stop("mtp_well_df_total")

    if self.plotType==PlotType.Histogram:
        return curveDataFrames[1], well_loc

    if self.plotType==PlotType.CrossPlot:
        discrep= round(curveDataFrames[1].index[0]-curveDataFrames[2].index[0],1)
        if discrep>0: #if curves have different starts then equalize
            curveDataFrames[2].index = curveDataFrames[1].index
        elif discrep<0:
            curveDataFrames[1].index = curveDataFrames[2].index
        return curveDataFrames[1], curveDataFrames[2], well_loc

    if self.plotType==PlotType.ZPlot:
        discrep= round(curveDataFrames[1].index[0]-curveDataFrames[2].index[0],1)
        if discrep>0: #if curves have different starts then equalize
            curveDataFrames[2].index = curveDataFrames[1].index
            curveDataFrames[3].index = curveDataFrames[1].index
        elif discrep<0:
            curveDataFrames[1].index = curveDataFrames[2].index
            curveDataFrames[3].index = curveDataFrames[1].index
        return curveDataFrames[1], curveDataFrames[2], curveDataFrames[3], well_loc

    if self.plotType==PlotType.PK:
        return curveDataFrames[1], curveDataFrames[2], curveDataFrames[3], curveDataFrames[4], well_loc

    if self.plotType==PlotType.ThreeDPlot:
        discrep= round(curveDataFrames[1].index[0]-curveDataFrames[2].index[0],1)
        if discrep>0: #if curves have different starts then equalize
            curveDataFrames[2].index = curveDataFrames[1].index
            curveDataFrames[3].index = curveDataFrames[1].index
        elif discrep<0:
            curveDataFrames[1].index = curveDataFrames[2].index
            curveDataFrames[3].index = curveDataFrames[2].index
        return curveDataFrames[1], curveDataFrames[2], curveDataFrames[3], curveDataFrames[4], well_loc
