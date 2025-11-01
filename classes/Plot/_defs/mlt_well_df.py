import glob
import os
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from classes.Project.WellList import WellList

import defs.alert as alert
import defs.excel as excel
import defs.las as las
import defs.main as main
import global_vars
from enumerables import Dir, PlotType
from structs import ZoneDepths


if TYPE_CHECKING:
    from .. import Plot


def mlt_well_df(self : 'Plot', wellList : WellList):
    '''
    Load multi_well data frames for plotting or scripts

    '''
    # Get Zone Data
    excel.get_zone()

    # get wells with core  (i.e. have cas files in Indir)
    curDir = os.getcwd()
    os.chdir(global_vars.project.inDir)
    casFiles = glob.glob("*.cas")
    os.chdir(curDir)

    numberOfCurves : int = 1
    curveNames = []
    curveDataFrames=[] #: list [str, pd.DataFrame] = []
    curveDataFrame=[] #Lists : list [str, list[pd.DataFrame]] = []

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

    for i in range(numberOfCurves):
        curveNames.append(self.settings.Get('curve'+str(i+1)))
        curveDataFrames.append(pd.DataFrame(None)) #empty dictionary
    
    curveDataFrameLists = []     #empty dictionary
    core_df = pd.DataFrame(None)

    cr_idx_top=0 #this appears to be always 0
    cr_idx_bot=0    # intialize end core

    def LoadCas():
        #ensure well is also in Well List
        wname=well.uwi+'.cas'
        if wname in casFiles:
            curDir=os.getcwd()
            #get cas_data and create core_df
            cas_data = well.GetLASData(Dir.In, '.cas')
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


    for well in wellList.GetWells():        #cycle through well UWILAS
        self.zoneDepths = None
        core_df = pd.DataFrame(None)

        #Set measured, core or formation depth interval interval
        if (self.zoneDepths is None):   #If dpt_int empty
            zone=self.settings.Get('zone')

            self.zoneDepths = well.GetZoneDepths(zone)
            print(f"Zone top: {self.zoneDepths.top} bottom: {self.zoneDepths.base}")

        #load plot data from LAS and/or core
        las_data = well.GetLASData(Dir.In)

        #clear previous dataframe or create dataframe
        df = pd.DataFrame(None)
        # get las data frame
        df = las_data.df()
        df.replace(-999.25, np.NaN, inplace=True)
        step=las_data.well.step.value
        ls_strt=las_data.well.strt.value
        ls_stop=las_data.well.stop.value
        #well_loc=las_data.well.loc.value

        #set depth interval
        if zone != 'CORE':         #if not core then set LAS depth interval
            #set depth interval
            zone=self.settings.Get('zone')

        if zone=='WELL':
            self.zoneDepths = ZoneDepths(top=ls_strt, base=ls_stop, name=zone)

        #set depth interval
        idx_top=int((self.zoneDepths.top - ls_strt)/step)
        idx_bot=int((self.zoneDepths.base - ls_strt)/step)+1  #get very last of array
        maxdat=idx_bot-idx_top
        if zone=='CORE':
            if maxdat>len(core_df.index):         # ensure length of plot curves are the same
                idx_bot=idx_bot-(maxdat-len(core_df.index))
                maxdat=idx_bot-idx_top

        lasDataFrames = {}
        lasDataFrames[Dir.Out] = pd.DataFrame(None)
        lasDataFrames[Dir.In] =  pd.DataFrame(None)

        ccrv=[]   #list of core curves in plot

        #load las data
        for i in range(numberOfCurves ):
            #curveDataFrame[i] = pd.DataFrame(None) #temporary variable to hold the dataframe
            #ensure same core curve df and las curve df length and start
            if curveNames[i] in global_vars.cdescrvs: #use cas data     #CORES
                #ensure same core curve df and las curve df length and start
                ccrv.append(i)
                if core_df.empty :
                    core_df, cr_idx_top,cr_idx_bot=LoadCas() #load here, so we dont load it if we dont need too
                curveDataFrames[i] = core_df[curveNames[i]] #.iloc[idx_top:idx_bot]
                if cr_idx_bot-cr_idx_top > idx_bot - idx_top:   #If core interval larger than log interval
                    cr_idx_bot=idx_bot
                    curveDataFrames[i] = curveDataFrames[i].iloc[cr_idx_top:cr_idx_bot]
                
            else:          #IN or OUTDIR
                if os.path.realpath(self.settings.Get('curve'+str(i+1)+'_dir'))==os.path.realpath(global_vars.project.outDir):
                    #OUTDIR with calculated curves. no aliases
                    if lasDataFrames[Dir.Out].empty:
                        crv_list=global_vars.CalcCurveNames

                        lasDataFrames[Dir.Out]=well.GetLASData(Dir.Out).df()
                        lasDataFrames[Dir.Out].replace(-999.25, np.NaN, inplace=True)
                        lasDataFrames[Dir.Out] = lasDataFrames[Dir.Out].iloc[idx_top:idx_bot] #because idx_top and bottom never change we can trim this ONCE
                    df = lasDataFrames[Dir.Out]
                    name = curveNames[i]
                    curveDataFrames[i] = df[curveNames[i]] #lasDataFrames[Dir.Out][curveNames[i]]
                elif os.path.realpath(self.settings.Get('curve'+str(i+1)+'_dir'))==os.path.realpath(global_vars.project.inDir):
                    #INDIR
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
                    curveDataFrames[i] = df[name]
                else: 
                    mDir=os.path.realpath(self.settings.Get('ZCURVE_DIR')) #if ZCURVE
                    if 'LAS_OUT'in mDir:
                        mDir=Dir.Out
                    else:
                        mDir=Dir.In
                    if lasDataFrames[mDir].empty:
                        lasDataFrames[mDir]=well.GetLASData(mDir).df()
                        lasDataFrames[mDir].replace(-999.25, np.NaN, inplace=True)
                        lasDataFrames[mDir] = lasDataFrames[mDir].iloc[idx_top:idx_bot] #because idx_top and bottom never change we can trim this ONCE
                    df = lasDataFrames[mDir]
                    name = curveNames[i]
                    curveDataFrames[i]=df[name]

                if curveDataFrames[i].empty:
                    alert.Error(f"{curveNames[i]} ({name}) was not in {well.uwi}({well.alias})")
                    main.show_las(well.uwi+'.las')
                    global_vars.perfTest.Stop("mtp_well_df_total")
                    return
        for i in range(numberOfCurves):
            if len(ccrv)>0: #adjust for curve depth in dataframes
                #set all curves to core interval
                if i not in ccrv: 
                    #if not a core curve adjust depths
                    lencrvfrs=len(curveDataFrames[i])
                    for ix in range(lencrvfrs):
                        if curveDataFrames[i].index[ix]>=curveDataFrames[ccrv[0]].index[0]:
                            endix=ix+cr_idx_bot #end of core in curveFDataFrames
                            if endix>idx_bot:   #If core longer than curveFrames[i]
                                endix=idx_bot
                            
                            df=curveDataFrames[i].iloc[ix:endix].__deepcopy__()
                            df.name = curveNames[i]
                            curveDataFrames[i]=df
                            break
            curveDataFrameLists.append(curveDataFrames[i])

    #For each well  concatenate curveDataFrames
    idx=0
    c=[]
    lencrvfrmLists=len(curveDataFrameLists)
    while (idx+1)*numberOfCurves<=lencrvfrmLists:
        for i in range(numberOfCurves):
            if idx<=0:
                c.append(curveDataFrameLists[i])  #.to_frame()
            else:
                cf=curveDataFrameLists[i+idx*numberOfCurves]
                c[i]=pd.concat([c[i],cf], ignore_index=True).__deepcopy__()
        idx+=1
        
    #globals.project.outDir holds calculated curves!

    global_vars.perfTest.Stop("mtp_well_df_total")

    if self.plotType==PlotType.Histogram:
        return c[0]

    if self.plotType==PlotType.CrossPlot:
        return c[0], c[1]

    if self.plotType==PlotType.ZPlot:
        return c[0], c[1], c[2]

    if self.plotType==PlotType.PK:
        return c[0], c[1], c[2], c[3]

    if self.plotType==PlotType.ThreeDPlot:
        return c[0], c[1], c[2], c[3]

