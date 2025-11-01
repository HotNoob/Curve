'''facies_scripts'''

import os
import numpy as np
from enumerables import Dir, ErrorMessage
import global_vars
from defs import alert, excel, las, prompt

from classes.Plot.DepthPlot import DepthPlot

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Script

#-------------------------------------------------------------------------------------------------------
def Facies(self : 'Script'):
    '''
    Calculate Facies.  Output curve= FCCN
    '''
    global_vars.ui.Root.window.iconify()

    mmessage='Is this a trial run (Yes) or the Final run (No)'
    mytry=prompt.yesno(mmessage)
    if mytry==False:
        if global_vars.fc_fn.empty == 'True':       #if globals.fc_fn is still empty
            alert.RaiseException("First select globals.fc_fn in trial run")

    fcrvs=[]                  # curves for dpt plt fills

    # Get Zone Data
    excel.get_zone()

    #Load Facies Criteria from spreadsheet
    mpath='databases/PETROFAC.xlsx'
    df=excel.get_exceldata(mpath)
    if df.empty==True:              #if file not opened
        return

    #read facies criteria
    fmins=[]
    fmaxs=[]
    for idf in range(2,7):
        for row in range(1,6):
            myminmax=df.loc[row][idf]
            if myminmax==myminmax:
                mymin=myminmax.index(',')
                fmins.append(float(myminmax[:mymin]))
                fmaxs.append(float(myminmax[mymin+1:]))
            '''
            else:               #if np.nan
                fmins.append('')
                fmaxs.append('')
            '''
    mzone=df.iloc[1]['OTHER']

    #For each well in list
    for well in global_vars.project.currentWellList.GetWells():
        #load load las from Outdir
        las_data = well.GetLASData(Dir.Out)
        las_start=las_data.well.STRT.value
        las_step=las_data.well.STEP.value
        mynull=float(round(las_data.well.NULL.value,2))
        global_vars.las_df=las_data.df()
                     
        zoneDepths = well.GetZoneDepths(mzone)

        if zoneDepths is None:
            alert.Error(ErrorMessage.MISSING_FORMATION_ZONE, [mzone, well])
            continue

        #set depth interval
        idx_top=int((zoneDepths.top - las_start)/las_step)
        idx_bot=int((zoneDepths.base - las_start)/las_step)+1  #get very last of array

        #Get Curves
        #Create empty PetroFacies Curve globals.fc_fn unless it already exists
        FCFN=[]
        if 'FCFN' in las_data.curves:
            FCFN=global_vars.las_df['FCFN'].tolist()
            #reset over zone keep previous values
            for idx in range(idx_top,idx_bot):
                FCFN[idx]=mynull
        else:
            #create empty las_df['FCFN']
            global_vars.las_df['FCFN']=np.nan
            FCFN=global_vars.las_df['FCFN'].to_list()

        #Initialization of logs
        GR_nm='GR_NRM'
        RHOB_nm='RHOB_NRM'
        NPHI_nm='NPHI_NRM'
        DTS_nm='DT_NRM'
        PE_nm ='PE'

        #Check for preferred input curves
        if GR_nm not in las_data.curves:
            GR_nm='GR'    #replace
        if RHOB_nm not in las_data.curves:
            RHOB_nm='RHOB'    #replace
        if NPHI_nm not in las_data.curves:
            NPHI_nm='NPHI'    #replace
        if DTS_nm not in las_data.curves:
            DTS_nm='DT'      #replace

        #get the curves from OUTDIR  NOTE
        crvs=[]      #list of data frames
        c_num=0
        c_idx=0
        if GR_nm in global_vars.las_df.columns:
            crvs.append(global_vars.las_df.iloc[idx_top:idx_bot][GR_nm].copy(deep=True))
            c_num +=1
        c_idx +=1
        if RHOB_nm in global_vars.las_df.columns:
            crvs.append(global_vars.las_df.iloc[idx_top:idx_bot][RHOB_nm].copy(deep=True))
            c_num +=1
        c_idx +=1
        if NPHI_nm in global_vars.las_df.columns:
            crvs.append(global_vars.las_df.iloc[idx_top:idx_bot][NPHI_nm].copy(deep=True))
            c_num +=1
        c_idx +=1
        if DTS_nm in global_vars.las_df.columns:
            crvs.append(global_vars.las_df.iloc[idx_top:idx_bot][DTS_nm].copy(deep=True))
            c_num +=1
        c_idx +=1
        if PE_nm in global_vars.las_df.columns:
            crvs.append(global_vars.las_df.iloc[idx_top:idx_bot][PE_nm].copy(deep=True))
            c_num +=1

        if c_num==0:            #No required curves in Well
            alert.Error(f"None of the curves required to define facies found in {well.uwi}({well.alias}) - skip well")
            continue

        #determine Petro Facies and store in FCFN list]
        pf_idx=0
        filter3=global_vars.las_df.iloc[idx_top:idx_bot]['FCFN'].copy(deep=True)
        mfacies=0
        max_idx=idx_bot-idx_top
        for mcrv in crvs:
            if mcrv.empty==False:      #if a dataframe
                while pf_idx<len(fmaxs)-1:
                    if mfacies>4:
                        mfacies=0
                    filter1 = mcrv>fmins[pf_idx]
                    filter2 = mcrv<fmaxs[pf_idx]
                    filter3 = (filter1==True) & (filter1==filter2)
                    for idx in range(0, max_idx):
                        if filter3.iloc[idx]==True :
                            FCFN[idx_top +idx]= mfacies

                    mfacies +=1
                    pf_idx +=1    #next facies

        #save output dir
        mynull=round(las_data.well.NULL.value,2)
        global_vars.las_df.fillna(mynull,inplace=True)
        global_vars.las_df['FCFN']=FCFN         #copy list into las_df['FCFN']
        las_data.set_data(global_vars.las_df)    #update las_data
        las_data.curves['FCFN'].descr='PETROFACIES CURVE'

        # Now save
        curDir = os.getcwd()
        os.chdir(global_vars.project.outDir)
        las_data.write(well.uwi + ".las", fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
        os.chdir(curDir)