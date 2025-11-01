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

from structs import CurveSource, ZoneDepths
from enumerables import Dir

if TYPE_CHECKING:
    from .. import Plot
    from classes.Project.Well import Well
    


def discrim_crv(self : 'Plot', ds1 : CurveSource, ds2 : CurveSource,crv_list, well : 'Well'):
    '''
        get series (single column dataframe) for 2 (discriminator) curves
        for specific well, with plot settings, and a minmax list for the 2 curves
    '''
    #plt_set=[]

    #get index of ds1 and ds2 as well as for CORE and/or Outdir curves in crv_list
    # Get Zone Data
    excel.get_zone()

    # get wells with core (i.e. have cas files in Indir)
    curDir = os.getcwd()
    os.chdir(global_vars.project.inDir)
    list1 = glob.glob("*.cas")
    os.chdir(curDir)

    zoneDepths = None
    zone = self.zoneDepths.name

    #Set measured, core or formation depth interval interval
    if zoneDepths is None:                      #If dpt_int empty
        zoneDepths = well.GetZoneDepths(zone)
        
        if zoneDepths is None:
            alert.Error(f'Zone {zone} not in {well.uwi}({well.alias}) - remove from well list')
            return

    #check if crvs are in cdescrvs
    #load Alias settings with previous selected path or default path

    #crv_list=[]
    crv1 = 'None'
    crv2 = 'None'

    if ds1 is not None:
        crv1=ds1.name

    if ds2 is not None:
        crv2=ds2.name

    if (crv1 in global_vars.cdescrvs) or (crv2 in global_vars.cdescrvs):  #load cas and set DPT interval
        #ensure well is also in Well List
        wname=well.uwi+'.cas'
        if wname in list1:
            #get cas_data and create core_df
            curDir=os.getcwd()
            os.chdir(global_vars.project.inDir)
            cas_data = global_vars.LASCache.GetLASData(wname)
            os.chdir(curDir)
            core_df=cas_data.df()
            core_df.replace(-999.25, np.NaN, inplace=True)
            #get cas_data and create core_df
            cr_shft=cas_data.params.csh.value
            c_start=cas_data.well.strt.value
            c_stop=cas_data.well.stop.value
            cr_shft=cas_data.params.csh.value
            # shift core in df
            cshift=round(round(cr_shft/0.1,0)*0.1,1)
            core_df.index=core_df.index+cshift

            if zoneDepths.top < c_start and zoneDepths.base >c_start:  #If core in selected zone
                zone='CORE'
                zoneDepths = ZoneDepths(top=c_start+cshift, base=c_stop+cshift, name=zone)
            else:     #core not in selected zone Next Well
                alert.Error(f'Tops not in {well.uwi}({well.alias}) - remove from well list')
                return

    #load plot data from LAS
    las_data = well.GetLASData(Dir.In)

    step=las_data.well.step.value
    ls_strt=las_data.well.strt.value
    ls_stop=las_data.well.stop.value

    if zone != 'CORE':         #if not core then set LAS depth interval
        #set depth interval
        zone=self.settings.Get('zone')

        if zone=='WELL':
            zoneDepths = ZoneDepths(top=ls_strt, base=ls_stop, name=zone)

    #set depth interval
    idx_top=int((zoneDepths.top - ls_strt)/step)
    idx_bot=int((zoneDepths.base - ls_strt)/step)+1  #get very last of array

    #initialize dfs
    c1=pd.DataFrame(None)
    c2=pd.DataFrame(None)
    '''
    c3=pd.DataFrame(None)
    c4=pd.DataFrame(None)
    '''
    idx=1                           #loop through curves
    found_fl=[0,0]              # if crv1, crv2 not core data
    core_flag=[0,0]
    maxdat=idx_bot-idx_top          #maxdat to synchronize Las with Cas data

    new_list = global_vars.project.curveNameTranslator.GetNames()
    las_data = well.GetLASData(Dir.In)
    while idx<3:                    #check the non_core curves
        idx=1
        while idx<3:
            if idx==1:
                if ds1.source == Dir.Out:       #Outdir
                    las_data = well.GetLASData(Dir.Out)
                    new_list=global_vars.CalcCurveNames.copy()
                    opt=2
                else:               #Indir
                    opt=0
                crv=crv1
            if idx==2:
                if ds1.source == Dir.Out:       #Outdir
                    las_data = well.GetLASData(Dir.Out)
                    crv_list=global_vars.CalcCurveNames
                    opt=2
                else:
                    opt=0
                crv=crv2

            df=las_data.df()
            df.replace(-999.25, np.NaN, inplace=True)
            if crv not in global_vars.cdescrvs:                   #find alias name of aka
                for c in crv_list:                        #check list of alias curves
                    if idx==1:
                        if crv1=='None':
                            found_fl[0]=1
                            break
                        else:
                            if crv1==c:                           # Found alias name of 1st curve name to be plotted (crv1)
                                if opt==0:                        #INDIR with alias array
                                    c1,found_fl[0]=main.find_aka(c,crv_list,1,las_data,0,zoneDepths)
                                if opt==2:      #OUTDIR
                                    #for depth interval in df index
                                    c1=df.iloc[idx_top:idx_bot][crv1]
                                    found_fl[0]=1
                    if idx==2:
                        if crv2=='None':
                            found_fl[1]=2
                            break
                        else:
                            if crv2==c:                         # Found alias name of 2nd curve name to be plotted (crv2)
                                if opt==0:                          #from INDIR
                                    c2,found_fl[1]=main.find_aka(c,crv_list,2,las_data,0,zoneDepths)
                                if opt==2:      #OUTDIR
                                    #for depth interval in df index
                                    c2=df.iloc[idx_top:idx_bot][crv2]
                                    found_fl[1]=2

                    if 0 not in found_fl[:2]:
                        #done
                        idx=3  # last of loop
                        break #the final loop
                    if (idx==1 and found_fl[0]!=0) or (idx==2 and found_fl[1]!=0) :
                        break
            else:
                #ensure same core curve df and las curve df length
                maxdat=len(core_df.index)
                cr_idx_top=0
                cr_idx_bot=maxdat  #get very last of array
                if idx==1:
                    c1=core_df.iloc[cr_idx_top:][crv]
                    found_fl[0]=1
                    core_flag[0]=1
                if idx==2:
                    c2=core_df.iloc[cr_idx_top:][crv]
                    found_fl[1]=2
                    core_flag[1]=1

            idx +=1        # go to next curve
        #if core curves used ensure it is of same len as other curves
        if core_flag[0]==0 and maxdat < len(c1):
            c1=c1.iloc[cr_idx_top:cr_idx_bot]
        if core_flag[1]==0 and maxdat < len(c2):
            c2=c2.iloc[cr_idx_top:cr_idx_bot]

    if found_fl[0]!=1 and crv1!='None':                   # crv1 was NOT found
        alert.Error(f"{crv1} was not in {well.uwi}({well.alias})")
        main.show_las(well.uwi+'.las')
        return     # go back to graphs and start over
    if found_fl[1]!=2 and crv2!='None':                   # crv1 was NOT found
        alert.Error(f"{crv2} was not in {well.uwi}({well.alias})")
        main.show_las(well.uwi+'.las')
        return     # go back to graphs and start over
    return c1, c2
