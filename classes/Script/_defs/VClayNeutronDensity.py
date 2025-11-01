'''nd_scripts'''
import numpy as np
from classes.Project.Parameter import ZoneParameter

import global_vars
from classes.Plot.DepthPlot import DepthPlot
from defs import alert, excel, las, prompt, program
from enumerables import Dir, ErrorMessage
from structs import ZoneDepths

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Script

def VClayNeutronDensity(self : 'Script'):
    '''
    standard VCL calculations using build-in scripts for Neutron Density
    '''

    global_vars.ui.Root.window.iconify()

    mmessage='Is this a trial run (Yes) or the Final run (No)'
    mytry=prompt.yesno(mmessage)
    if mytry==False:
        if self.VCL_Fn is None:
            alert.RaiseException("First select VCL_Fn in trial run")
    else:
        self.VCL_Fn = None

    fcrvs=[]                  # curves for dpt plt fills

    #input curves
    crv_list=[]
    input_list=['RHOB','DRHO','NPSS','CALY','CALI']
    nocurves=['DEPT', 'None']
    crv_list = program.com_crvs(nocurves,crv_list,0)
    yn=True
    for inp in input_list:
        if inp not in crv_list:
            yn=prompt.yesno(inp + " not in every well, continue yes or no")

    if yn==False:           #return to main
        global_vars.ui.Root.window.deiconify()
        return

    #crvnm contains calculatable curve lists - already defined in mainwell
    #loop through wells
    WellList=global_vars.project.currentWellList.GetWells()
    for well in WellList:
        fn_list=[]          #list of curve names for final selection

        #load load las from Outdir
        las_data = well.GetLASData(Dir.Out)
        if las_data is None:
            alert.Error(ErrorMessage.FAILED_LOAD_LAS, [Dir.Out, well])
            continue
        
        las_start=las_data.well.STRT.value
        las_stop=las_data.well.STOP.value
        global_vars.las_df=las_data.df()

        #Initialization of logs
        fl_XP = 0
        fl_NP = 0
        NPS='NPSS_NRM'
        RHB='RHOB_NRM'

        #Check for preferred input curves
        if NPS not in las_data.curves:
            NPS='NPSS'    #replaces:         # if still not in las file
            if NPS not in las_data.curves:
                alert.Error(ErrorMessage.MISSING_CURVE_SKIP, ["NPSS and NPSS_NRM", well])
                continue
        if NPS in las_data.curves:         # if in las file
            fl_NP=1

        if RHB not in las_data.curves:
            RHB='RHOB'    #replace
        if RHB in las_data.curves:         # if in las file
            if 'DRHO' not in las_data.curves:       #If no density correction return and add to LAS
                yn=prompt.yesno(f"DRHO not in {well.uwi}({well.alias}) - skip curve in well(Y) or add to Outdir Lasfile(N)")
                if yn==False:
                    global_vars.ui.Root.window.deiconify()
                    return
            fl_XP=2

        #for VCLAY Calculation from Neutron Density curves
        if fl_XP>=1:
            fn_list.append('VCL_ND')
            global_vars.las_df['VCL_ND']=np.nan
            VCL_ND=global_vars.las_df['VCL_ND'].copy()
        global_vars.las_df['VCL_NEU']=np.nan
        VCL_NEU=global_vars.las_df['VCL_NEU'].copy()
        fn_list.append('VCL_NEU')

        mycol=1   # Set to default column of param_df
        #loop through default and zone types/levels 1-4
        mzones=global_vars.project.formationZoneParameters.Zone_list()
        old_Ps=[]       # list of parameters that may need to be restored based on Zonetypes
        for zone in mzones:
            #Read zone parameters
            #params = global_vars.project.formationZoneParameters.GetCalculatedZoneParameters(zone)
            cstep=0.1
            if zone == 'DEFAULT':
                #set depth interval
                idx_top=0
                idx_bot=int((las_stop - las_start)/cstep)+1  #get very last of array
            else:
                if zone in global_vars.project.formationZones:
                    zoneDepths = well.GetZoneDepths(zone)

                if zoneDepths is None:
                    alert.Error(ErrorMessage.MISSING_FORMATION_ZONE_SKIP, [zone, well])
                    global_vars.ui.Root.window.deiconify()
                    continue

                #set depth interval
                idx_top=int((zoneDepths.top - las_start)/cstep)
                idx_bot=int((zoneDepths.base - las_start)/cstep)+1  #get very last of array

            # Now do all calculations using updated params
            # Clay Volume from Linear Method and Crossplot method
            # RHOMA, RHOFL, RHOSH, NEUMA, NEUSH, NEUFL NPcl NPsh

            #set the Params for NP_DP shale calculation
            #PN instead of NP. fix in params.xlsx?
            Pa=8  #number of parameters
            NPcl, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('PNCL', zone, old_Ps,Pa)
            NPsh, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('PNSH', zone, old_Ps,Pa) 
            RHOMA, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('RHOMA', zone, old_Ps,Pa)
            RHOFL, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('RHOFL', zone, old_Ps,Pa)
            RHOSH, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('RHOSH', zone, old_Ps,Pa)
            NEUMA, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('NEUMA', zone, old_Ps,Pa)
            NEUSH, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('NEUSH', zone, old_Ps,Pa)
            NEUFL, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('NEUFL', zone, old_Ps,Pa)

            if not global_vars.las_df.iloc[idx_top:idx_bot][NPS].empty:
                mNPS=global_vars.las_df.iloc[idx_top:idx_bot][NPS].copy()
                if fl_XP>=1:
                    if not global_vars.las_df.iloc[idx_top:idx_bot][RHB].empty:
                        mRHB=global_vars.las_df.iloc[idx_top:idx_bot][RHB].copy()
                    VCL_ND.iloc[idx_top:idx_bot]=NDcalcs(mNPS, mRHB, 'VCL_ND',NPcl, NPsh, RHOMA, RHOFL, RHOSH, NEUMA,NEUSH, NEUFL)
                #Neutron shale volume is always calculated
                VCL_NEU.iloc[idx_top:idx_bot]= NDcalcs(mNPS, mRHB,'VCL_NEU',NPcl, NPsh, RHOMA, RHOFL, RHOSH, NEUMA,NEUSH, NEUFL)
        
            mycol +=1 #check next zone

        if mytry==True:
            #plot results in Dpt_plot for each well with 6 tracks
            '''
            Defined in depth plot
            color_list=['green', 'palegreen','red','lightcoral','olive','blue','cyan' ,'magenta','purple','gold','lightgrey', 'black', 'darkblue', 'lightblue', 'gray','yellow','orange']
            line_list=['dotted','solid','dashed','dashdot',(0,(3,1,1,1)),(0,(4, 2, 1, 2)),(0,(3,1,1,1,1,1))]
            [[0, 50, 100, 150, 200],[0.45, 0.3, 0.15, 0, -0.15],[0.60, 0.45, 0.30, 0.15, 0],[0.0, 0.25, 0.5, 0.75, 1.0],[1.95, 2.2, 2.45, 2.7, 2.95],[500,400,300,200,100],[-0.15,0.15,0.45,0.75,1.05],[1000,750,500,250,0.0],[0.1,1,10,100,1000],[0.2,2,20,200,2000],[0, 0.15, 0.30, 0.45, 0.60],
            [-0.75,-0.50,-0.25,0.0,0.25],[0,5,10,15,20],[300,200,100,0,-100],[150,200,250,350,400]]
            scale (0=default or 'lin', 1='log')
            marker_list=['o','O','s','d','D','x','X','h','+','*','^','']

            props[color, linestyle, ticks, scale , marker, track]
            '''
            global_vars.ui.Root.window.iconify()

            #Define top and bottom of plot
            zoneDepths = ZoneDepths(top=las_start, base=las_stop, name="WELL")

            if fl_XP==1:
                #NPSS = c1 RHOB = c2  DRHO = c3 VCL_ND = c4 VCL_NEU = c5
                c1=global_vars.las_df[NPS]
                c2=global_vars.las_df[RHB]
                c3=global_vars.las_df['DRHO']                   #What if no DRHO
                c4=VCL_ND
                c5=VCL_NEU

                curvs=[c1, c2, c3, c4, c5]

                props=[[5,2,2,0,11,1,'','','','','',''],[2,1,4,0,11,1,'','','','','',''],[7,0,6,0,11,1,'','','','','',''],[0,0,3,0,11,2,'','','','','',''],[5,1,3,0,11,2,'','','','','','']]
            elif fl_XP==2:     #No DRHO

                #NPSS = c1 RHOB = c2  DRHO = c3 VCL_ND = c4 VCL_NEU = c5
                c1=global_vars.las_df[NPS]
                c2=global_vars.las_df[RHB]
                #c3=las_df['DRHO']                   #What if no DRHO
                c4=VCL_ND
                c5=VCL_NEU

                curvs=[c1, c2, c4, c5]

                props=[[5,2,2,0,11,1,'','','','','',''],[2,1,4,0,11,1,'','','','','',''],[0,0,3,0,11,2,'','','','','',''],[5,1,3,0,11,2,'','','','','','']]

            if fl_NP==1 and fl_XP==0:
                #NPSS = c1 VCL_NEU = c2
                c1=global_vars.las_df[NPS]
                c2=VCL_NEU
                curvs=[c1, c2]

                props=[[5,2,2,0,11,1,'','','','','',''],[0,0,2,0,11,2,'','','','','','']]

            wellname = las_data.well.WELL.value
            # Dpt_plt(wellname, curvs, props, trcks, pltype=0, Fms)
            depthPlot = DepthPlot()
            depthPlot.depthPlot(wellname, curvs, fcrvs, props, 2, DepthPlot.DepthPlotType.DepthPlot,well.formations, zoneDepths)
            if well.uwi == global_vars.project.currentWellList[-1]:    # only ask in final well of trial run
                VCL_Fn=self.selectFinalCurve(fn_list)
                mytry=False
            
    global_vars.ui.Root.window.deiconify()

    #select Final Well List and start new WellList loop
    global_vars.project.loadWellListPrompt()
    global_vars.ui.Root.Update()
    WellList=global_vars.project.currentWellList.GetWells() 
    for well in WellList:
        if mytry==False:      #VCL_Fn set in trial run as global
            if VCL_Fn is None:
                alert.RaiseException("First select VCL_Fn in trial run")

            #load load las from Outdir
            las_data=well.GetLASData(Dir.Out)
            
            if las_data is None:
                alert.Error(ErrorMessage.FAILED_LOAD_LAS, [Dir.Out, well])
                continue

            las_start=las_data.well.STRT.value
            las_stop=las_data.well.STOP.value
            global_vars.las_df=las_data.df()

            #Initialization of logs
            fl_XP = 0
            fl_NP = 0
            NPS='NPSS_NRM'
            RHB='RHOB_NRM'

            #Check for preferred input curves
            if NPS not in las_data.curves:
                NPS='NPSS'    #replace
                if NPS not in las_data.curves:         # if still not in las file
                    alert.Error(ErrorMessage.MISSING_CURVE_SKIP, ["NPSS and NPSS_NRM", well])
                    continue
            #if NPS in las_data.curves:         # if in las file
                fl_NP=1

            if RHB not in las_data.curves:
                RHB='RHOB'    #replace
            if RHB in las_data.curves:         # if in las file
                if 'DRHO' not in las_data.curves:       #If no density correction return and add to LAS
                    yn=prompt.yesno(f"DRHO not in {well.uwi}({well.alias}) - skip curve in well(Y) or add to Outdir Lasfile(N)")
                    if yn==False:
                        global_vars.ui.Root.window.deiconify()
                        return
                fl_XP=2

            #loop through default and zone types/levels 1-
            #for VCLAY Calculation from Neutron Density curves
        if fl_XP>=1:
            global_vars.las_df['VCL_ND']=np.nan
            self.VCL_ND=global_vars.las_df['VCL_ND'].copy()
        global_vars.las_df['VCL_NEU']=np.nan
        self.VCL_NEU=global_vars.las_df['VCL_NEU'].copy()
        #initialize VCL_FN
        global_vars.las_df['VCL_FN']=np.nan
        mVCLFn=global_vars.las_df['VCL_FN'].copy(deep=True)

        mycol=1   # Set to default column of param_df
        #loop through default and zone types/levels 1-4
        mzones=global_vars.project.formationZoneParameters.Zone_list()
        old_Ps=[]       # list of parameters that may need to be restored based on Zonetypes
        for zone in mzones:
            #Read zone parameters
            #params = global_vars.project.formationZoneParameters.GetCalculatedZoneParameters(zone)
            cstep=0.1
            if zone == 'DEFAULT':
                #set depth interval
                idx_top=0
                idx_bot=int((las_stop - las_start)/cstep)+1  #get very last of array
            else:
                if zone in global_vars.project.formationZones:
                    zoneDepths = well.GetZoneDepths(zone)

                if zoneDepths is None:
                    #alert.Error(ErrorMessage.MISSING_FORMATION_ZONE_SKIP, [zone, well])
                    continue

                #set depth interval
                idx_top=int((zoneDepths.top - las_start)/cstep)
                idx_bot=int((zoneDepths.base - las_start)/cstep)+1  #get very last of array

            # Now do all calculations using updated params
            # Clay Volume from Linear Method and Crossplot method
            # RHOMA, RHOFL, RHOSH, NEUMA, NEUSH, NEUFL NPcl NPsh

            #set the Params for NP_DP shale calculation
            #PN instead of NP. fix in params.xlsx?
            Pa=8  #number of parameters
            NPcl, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('PNCL', zone, old_Ps,Pa)
            NPsh, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('PNSH', zone, old_Ps,Pa) 
            RHOMA, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('RHOMA', zone, old_Ps,Pa)
            RHOFL, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('RHOFL', zone, old_Ps,Pa)
            RHOSH, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('RHOSH', zone, old_Ps,Pa)
            NEUMA, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('NEUMA', zone, old_Ps,Pa)
            NEUSH, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('NEUSH', zone, old_Ps,Pa)
            NEUFL, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('NEUFL', zone, old_Ps,Pa)

            if not global_vars.las_df.iloc[idx_top:idx_bot][NPS].empty and not global_vars.las_df.iloc[idx_top:idx_bot][RHB].empty:
                mNPS=global_vars.las_df.iloc[idx_top:idx_bot][NPS].copy()
                mRHB=global_vars.las_df.iloc[idx_top:idx_bot][RHB].copy()
                mVCLFn.iloc[idx_top:idx_bot]=NDcalcs(mNPS, mRHB, VCL_Fn, NPcl, NPsh, RHOMA, RHOFL, RHOSH, NEUMA,NEUSH, NEUFL)
            mycol +=1 #check next zone

        #update las_df 
        global_vars.las_df['VCL_Fn']=mVCLFn
        global_vars.las_df['VCL_Fn'].descr=f'{VCL_Fn} BY EUCALYPTUS CONSULTING INC'
        las_data.set_data(global_vars.las_df)    #update las_data
        las.save_curves(well.uwi + ".las", VCL_Fn, 'VCL_FN')
    
    #close script and update project
    global_vars.project.Scan()
    global_vars.ui.Root.window.deiconify()

def NDcalcs(mNPS, mRHB, VCL_Fn,NPcl, NPsh, RHOMA, RHOFL, RHOSH, NEUMA,NEUSH, NEUFL):
    '''
    Calculate Vclay using various methods as speficified in VCL_fin
    '''

    #if not global_vars.las_df.iloc[idx_top:idx_bot][NPS].empty:
    #    mNPS=global_vars.las_df.iloc[idx_top:idx_bot][NPS].copy()  #GR Index

    match VCL_Fn:
        case 'VCL_ND':
            #Neutron-Density shale volume
            m1 = (NEUFL - NEUMA)/ (RHOFL - RHOMA)
            x0 = NEUMA
            x1 = mNPS + m1 * (RHOMA - mRHB)
            x2 = NEUSH + m1 * (RHOMA - RHOSH)
            VCL_ND= (x1 - x0) / (x2 -x0)
            VCL_ND= VCL_ND.clip(0.6, 0)
            #global_vars.las_df['VCL_ND']=VCL_ND
            return VCL_ND
        case 'VCL_NEU':
            #  Clay Volume from Neutron log only
            VCL_NEU= (mNPS - NPcl) / (NPsh-NPcl)
            VCL_NEU =VCL_NEU.clip(0.6, 0)
            #global_vars.las_df['VCL_NEU']=VCL_NEU
            return VCL_NEU
        