'''gamma_scripts'''
from tkinter import FALSE

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

#-----------------------------------------------------------------------------------------------------
def VClayGammaRay(self : 'Script'):
    '''
    standard log analysis VClay calculations using build-in scripts
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
    nocurves=['DEPT', 'None']
    crv_list = program.com_crvs(nocurves,crv_list,0)
    yn=True
    if 'GR' not in crv_list and 'GR_NRM' not in crv_list:
        alert.Error("No GR or GR_NRM in every well ")
        yn=FALSE

    if yn==False:
        global_vars.ui.Root.window.deiconify()
        return

    #crvnm contains calculatable curve lists - already defined in mainwell
    #loop through wells
    WellList=global_vars.project.currentWellList.GetWells()
    for well in WellList:
        
        #load load las from Outdir
        las_data=well.GetLASData(Dir.Out)
        if las_data is None:
            alert.Error(ErrorMessage.FAILED_LOAD_LAS, [Dir.Out, well])
            continue

        las_start=las_data.well.STRT.value
        las_stop=las_data.well.STOP.value
        global_vars.las_df=las_data.df()

        #Initialization of logs
        GRL_N='GR_NRM'    #GRL name

        #Check for preferred input curves
        if GRL_N not in las_data.curves:
            GRL_N='GR'    #replace

        #for VCLAY CalCulations
        global_vars.las_df['IGR']=np.nan
        global_vars.las_df['VCL_LIN']=np.nan
        global_vars.las_df['VCL_CLV']=np.nan
        global_vars.las_df['VCL_TRT']=np.nan
        global_vars.las_df['VCL_OLD']=np.nan
        global_vars.las_df['VCL_STB_I']=np.nan
        global_vars.las_df['VCL_STB_II']=np.nan
        global_vars.las_df['VCL_STB_MP']=np.nan

        IGR=global_vars.las_df['IGR'].copy()
        VCL_LIN=global_vars.las_df['VCL_LIN'].copy()
        VCL_CLV=global_vars.las_df['VCL_CLV'].copy()
        VCL_TRT=global_vars.las_df['VCL_TRT'].copy()
        VCL_OLD=global_vars.las_df['VCL_OLD'].copy()
        VCL_STB_I=global_vars.las_df['VCL_STB_I'].copy()
        VCL_STB_II=global_vars.las_df['VCL_STB_II'].copy()
        VCL_STB_MP=global_vars.las_df['VCL_STB_MP'].copy()

        fn_list=['VCL_LIN','VCL_CLV','VCL_TRT','VCL_OLD', 'VCL_STB_I',
                'VCL_STB_II', 'VCL_STB_MP']

        #loop through default and zone types/levels 1-4
        mzones=global_vars.project.formationZoneParameters.Zone_list()
        old_Ps=[]       # list of parameters that may need to be restored based on Zonetypes
        for zone in mzones:
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
                    #global_vars.ui.Root.window.deiconify()
                    continue

                #set depth interval
                idx_top=int((zoneDepths.top - las_start)/cstep)
                idx_bot=int((zoneDepths.base - las_start)/cstep)+1  #get very last of array

            # Now do all calculations using updated params
            # Clay Volume from Linear Method
            #Set the Params for calculation
            Pa=2  #number of parameters
            GRcl, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('GRCL', zone, old_Ps,Pa)
            GRsh, old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('GRSH', zone, old_Ps,Pa)
            if not global_vars.las_df.iloc[idx_top:idx_bot][GRL_N].empty:
                GRL=global_vars.las_df.iloc[idx_top:idx_bot][GRL_N].copy()
                IGR.iloc[idx_top:idx_bot]= GRcalcs(GRL,'VCL_LIN',GRcl, GRsh)
                VCL_LIN=IGR.copy(deep=True)
                VCL_CLV.iloc[idx_top:idx_bot]= GRcalcs(GRL,'VCL_CLV',GRcl, GRsh)
                #print(VCL_CLV.iloc[9488:9671])
                VCL_TRT.iloc[idx_top:idx_bot]= GRcalcs(GRL,'VCL_TRT',GRcl, GRsh)
                VCL_OLD.iloc[idx_top:idx_bot]= GRcalcs(GRL,'VCL_OLD',GRcl, GRsh)
                VCL_STB_I.iloc[idx_top:idx_bot]= GRcalcs(GRL,'VCL_STB_I',GRcl, GRsh)
                VCL_STB_II.iloc[idx_top:idx_bot]= GRcalcs(GRL,'VCL_STB_II',GRcl, GRsh)
    
        # Plot or Store results in las_df

        if mytry==True:
            #plot results in Dpt_plot for each well with 6 tracks
            #Define top and bottom of plot
            zoneDepths = ZoneDepths(top=las_start, base=las_stop, name="WELL")

            # GR_NRM = c1, VCL_LIN = c2, VCL_CLV = c3, VCL_TRT = c4, VCL_OLD = c5, VCL_STB_I = c6
            #VCL_STB_II = c7, VCL_STB_MP= c8
            global_vars.las_df.pop('IGR')
            if 'IGR' in las_data.curves:             # remove from data frame if already in VCL_LIN
                las_data.delete_curve(mnemonic='IGR', ix=None)

            c1=GRL
            c2=VCL_LIN
            c3=VCL_CLV
            c4=VCL_TRT
            c5=VCL_OLD
            c6=VCL_STB_I
            c7=VCL_STB_II
            c8=VCL_STB_MP

            curvs=[c1, c2, c3, c4, c5, c6, c7, c8 ]
            '''
            Defined in depth plot
            color_list=['green', 'palegreen','red','lightcoral','olive','blue','cyan' ,'magenta','purple','gold','lightgrey', 'black', 'darkblue', 'lightblue', 'gray','yellow','orange']
            line_list=['dotted','solid','dashed','dashdot',(0,(3,1,1,1)),(0,(4, 2, 1, 2)),(0,(3,1,1,1,1,1))]
            tick_list=[[0, 50, 100, 150, 200],[0.45, 0.3, 0.15, 0, -0.15],[0.60, 0.45, 0.30, 0.15, 0],[0.0, 0.25, 0.5, 0.75, 1.0],[1.95, 2.2, 2.45, 2.7, 2.95],[500,400,300,200,100],[-0.15,0.15,0.45,0.75,1.05],[1000,750,500,250,0.0],[0.1,1,10,100,1000],[0.2,2,20,200,2000],[0, 0.15, 0.30, 0.45, 0.60],
            [-0.75,-0.50,-0.25,0.0,0.25],[0,5,10,15,20],[300,200,100,0,-100],[150,200,250,350,400],[0,0.5,1,1.5,2],[1000,100,10,1,0.1],[2000,200,20,2,0.2],[1.65, 1.90, 2.15, 2.4, 2.65],[-2,0,2,4,6]]
            scale (0=default or 'lin', 1='log')
            marker_list=['o','O','s','d','D','x','X','h','+','*','^','']

            props[color, linestyle, ticks, scale , marker, track]
            '''
            #Create a list of FMs and tops to be displayed in DptPlt

            props=[[0,1,0,0,11,1,'','','','','',''],[7,1,3,0,11,2,'','','','','',''],[11,1,3,0,11,2,'','','','','',''],[5,2,3,0,11,2,'','','','','',''],[2,0,3,0,11,2,'','','','','',''],[0,1,3,0,11,3,'','','','','',''],[2,2,3,0,11,3,'','','','','',''],[5,3,3,0,11,3,'','','','','','']]
            wellname = las_data.well.WELL.value
            # Dpt_plt(wellname, curvs, fcrvs, props, trcks, pltype=0, Fms)
            depthPlot = DepthPlot()
            depthPlot.depthPlot(wellname, curvs, fcrvs, props, 3, DepthPlot.DepthPlotType.DepthPlot,well.formations, zoneDepths)
            if well.uwi == global_vars.project.currentWellList.list[-1]:    # only ask in final well of trial run
                self.VCL_Fn=self.selectFinalCurve(fn_list)
                mytry=False

    #select Final Well List and start new WellList loop
    global_vars.project.loadWellListPrompt()
    global_vars.ui.Root.Update()
    WellList=global_vars.project.currentWellList.GetWells() 
    for well in WellList:
        if mytry==False:      #VCL_Fn set in trial run as global
            if self.VCL_Fn is None:
                alert.RaiseException("First select VCL_Fn in trial run")

            #load load las from Ou.
            # tdir
            las_data=well.GetLASData(Dir.Out)
            
            if las_data is None:
                alert.Error(ErrorMessage.FAILED_LOAD_LAS, [Dir.Out, well])
                continue

            las_start=las_data.well.STRT.value
            las_stop=las_data.well.STOP.value
            global_vars.las_df=las_data.df()

            #Initialization of logs
            GRL_N='GR_NRM'    #GRL name0
            global_vars.las_df['VCL_Fn']=np.nan

            #Check for preferred input curves
            if GRL_N not in las_data.curves:
                GRL_N='GR'    #replace

            #loop through default and zone types/levels 1-4
            mzones=global_vars.project.formationZoneParameters.Zone_list()
            for zone in mzones:
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
                        #global_vars.ui.Root.window.deiconify()
                        continue

                    #set depth interval
                    idx_top=int((zoneDepths.top - las_start)/cstep)
                    idx_bot=int((zoneDepths.base - las_start)/cstep)+1  #get very last of array

                # Now do all calculations using updated params
                # Clay Volume from Linear Method
                #Set the Params for calculation
                Pa=2  #number of parameters
                GRcl, old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('GRCL', zone, old_Ps,Pa)
                GRsh, old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('GRSH', zone, old_Ps,Pa)
                if not global_vars.las_df.iloc[idx_top:idx_bot][GRL_N].empty:
                    GRL=global_vars.las_df.iloc[idx_top:idx_bot][GRL_N]
                    XRY= GRcalcs(GRL,'VCL_CLV',GRcl, GRsh)
                    global_vars.las_df['VCL_Fn'].iloc[idx_top:idx_bot]=XRY
                    #print(global_vars.las_df['VCL_Fn'].iloc[9488:9671])
            #global_vars.las_df[self.'VCL_Fn']

            las_data.set_data(global_vars.las_df)    #update las_data
            las.save_curves(well.uwi + ".las", 'VCL_Fn', self.VCL_Fn)
    global_vars.ui.Root.window.deiconify()
    
    global_vars.project.Scan()




def GRcalcs(GRL,VCL_Fn,GRcl, GRsh):
    '''
    Calculate Vclay using various methods as speficified in VCL_fin
    '''

    IGR=(GRL-GRcl)/(GRsh-GRcl)  #GR Index

    match VCL_Fn:
        case 'VCL_LIN':
            # Clay from GR Index
            VCL_LIN=IGR
            return VCL_LIN
        case 'VCL_CLV':
            #  Clay Volume from Clavier Method
            VCL_CLV = 1.7 - (3.38 - (IGR + 0.7)**2)**(1/2)
            return VCL_CLV
        case 'VCL_TRT':
            # Clay Volume from larinov_tertiary
            VCL_TRT = 0.083 * ( 2**(3.71*IGR) - 1 )
            return VCL_TRT
        case 'VCL_OLD':
            # Clay Volume calculation larinov_Older rock
            VCL_OLD = 0.33 * ( 2**(2*IGR) - 1 )
            return VCL_OLD
        case 'VCL_STB_I':
            # Clay Volume from Steiber I
            VCL_STB_I = IGR/(2-IGR)
            return VCL_STB_I
        case 'VCL_STB_II':
            # Clay Volume from Steiber II
            VCL_STB_II = IGR/(4-3*IGR)
            return VCL_STB_II
        case 'VCL_STB_MP':
            # Clay Volume from Steiber Miocene-Pliocene
            VCL_STB_MP = IGR/(3-2*IGR)
            return VCL_STB_MP
        
   
    

    