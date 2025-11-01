'''por_scripts'''

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

#-------------------------------------------------------------------------------------------------------
def Porosity(self : 'Script'):
    '''
    Standard log analysis porosity calculations using build-in scripts

    '''

    global_vars.ui.Root.window.iconify()

    mmessage='Is this a trial run (Yes) or the Final run (No)'
    mytry=prompt.yesno(mmessage)
    if mytry==False:
        if self.Phie_Fn is None and self.Phi_Fn is None:
            alert.RaiseException("First select Phie_Fn and/or Phi_Fn in trial run")
    else:
        self.Phie_Fn = None

    fcrvs=[]                  # curves for dpt plt fills

    #input curves
    crv_list=[]
    input_list=['RHOB', 'DPSS','NPSS','DT', 'VCL_FN']
    mylist=""
    for x in input_list:
        mylist=mylist + x + ', '
    mylist="These " + mylist[:-1]
    mmessage=mylist +" curves are often required. Continue?"
    myYN=prompt.yesno(mmessage)
    if myYN==False: return

    nocurves=['DEPT', 'None']
    crv_list = program.com_crvs(nocurves,crv_list,0)
    crv_list = program.com_crvs(nocurves,crv_list,3)

    yn=True
    for inp in input_list:
        if inp not in crv_list:
            yn=prompt.yesno(inp + " not in every well, continue yes or no")

        if yn==False:           #return to main
            global_vars.ui.Root.window.deiconify()
            return

    #crvnm contains calculatable curve lists - already defined in mainwell
    #loop through wells
    WellList= global_vars.project.currentWellList.GetWells()
    for well in WellList :
        fn1_list=[]                #list of curve names for final selection total porosity
        fn2_list=[]                #list of curve names for final selection effective porosity

        #load load las from Outdir
        las_data = well.GetLASData(Dir.Out)
        if las_data is None:
            alert.Error(ErrorMessage.FAILED_LOAD_LAS, [Dir.Out, well])
            continue
    
        las_start=las_data.well.STRT.value
        las_stop=las_data.well.STOP.value
        global_vars.las_df=las_data.df()

        lascurves=las_data.curves

        #Initialization of curves
        RHB='RHOB_NRM'
        DPS='DPSS_NRM'
        NPS='NPSS_NRM'
        DTS='DT_NRM'

        #Check for preferred input curves
        if RHB not in lascurves:
            RHB='RHOB'    #replace
        if DPS not in lascurves:
            DPS='DPSS'    #replace
        if NPS not in lascurves:
            NPS='NPSS'    #replace
        if DTS not in lascurves:
            DTS='DT'      #replace

        #flags
        fl_RHOB=0   #RHOB flag
        fl_XP=0     #Crossplot flag
        fl_DT=0     #Sonic flag

        # select porosity calculations
        if RHB not in lascurves:                   #If no RHOB in LAS file
            if DPS in lascurves:                   #But if there is a SS scale density porosity curve
                global_vars.las_df[RHB]=2.650-1.650*global_vars.las_df[DPS]     # create a RHOB curve
        if DPS not in lascurves:                   #If no DPSS in LAS file
            if RHB in lascurves:                   #But if there is a Bulk density curve
                global_vars.las_df[DPS]=(2.650-global_vars.las_df[RHB])/1.650   # create a DPSS curve
        #Get and obtain curves and flags
        #Neutron Density Xplot
                
        #VCL_FN for shale corrections
        if 'VCL_FN' in lascurves:
            VCLFn=global_vars.las_df['VCL_FN'].copy()
        else:
            alert.Error.ErrorMessage.MISSING_CURVE_CREATE, [zone, well]
            return
                
        if RHB in lascurves:
            fn1_list.append('PHISH')
            fn1_list.append('PHID')
            fn2_list.append('PHIE_D')
            RHOB =global_vars.las_df[RHB].copy()
            global_vars.las_df['PHISH']=np.nan        #Shale correction curve for PHIE_D
            PHISH=global_vars.las_df['PHISH'].copy()
            global_vars.las_df['PHID']=np.nan
            PHID=global_vars.las_df['PHID'].copy()
            NPSS=global_vars.las_df['NPSS'].copy()
            global_vars.las_df['PHIE_D']=np.nan
            PHIE_D=global_vars.las_df['PHIE_D'].copy()
            CSE = 1
            fl_RHOB=1

        if NPS in lascurves:
            fn1_list.append('PHIT_GAS')
            fn1_list.append('PHIND')
            fn2_list.append('PHIE_ND')
            fn2_list.append('PHIE_GAS')
            global_vars.las_df['PHIT_GAS']=np.nan
            PHIT_GAS=global_vars.las_df['PHIT_GAS'].copy()
            global_vars.las_df['PHIND']=np.nan
            PHIND=global_vars.las_df['PHIND'].copy()
            global_vars.las_df['PHIE_ND']=np.nan
            PHIE_ND=global_vars.las_df['PHIE_ND'].copy()
            global_vars.las_df['PHIE_GAS']=np.nan
            PHIE_GAS=global_vars.las_df['PHIE_GAS'].copy()
            CSE = 2
            fl_XP=1

        # Sonic porosities
        if DTS in lascurves:
            fn1_list.append('PHIS_WTA')
            fn1_list.append('PHIS_RHG')
            fn1_list.append('PHIS_RC')
            fn1_list.append('PHIS_FO')
            DT = global_vars.las_df[DTS].copy()
            global_vars.las_df['PHIS_WTA']=np.nan

            PHIS_WTA=global_vars.las_df['PHIS_WTA'].copy()
            global_vars.las_df['PHIS_GAS']=np.nan
            PHIE_GAS=global_vars.las_df['PHIE_GAS'].copy()
            global_vars.las_df['PHIS_RHG']=np.nan
            PHIS_RHG=global_vars.las_df['PHIS_RHG'].copy()
            global_vars.las_df['PHIS_RC']=np.nan

            PHIS_RC=global_vars.las_df['PHIS_RC'].copy()
            global_vars.las_df['PHIS_FO']=np.nan
            PHIS_FO=global_vars.las_df['PHIS_FO'].copy()
            CSE = 3
            fl_DT=1

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
                zoneDepths = well.GetZoneDepths(zone)

                if zoneDepths is None:
                    alert.Error(ErrorMessage.MISSING_FORMATION_ZONE_SKIP, [zone, well])
                    #global_vars.ui.Root.window.deiconify()
                    continue

                #set depth interval
                idx_top=int((zoneDepths.top - las_start)/cstep)
                idx_bot=int((zoneDepths.base - las_start)/cstep)+1  #get very last of array


            # Now do all calculations using updated params
            
            #Set the Params for calculation
            # Porosity parameters
            Pa=9
            #old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('GRCL', zone, old_Ps,Pa)
            RHOMA,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('RHOMA', zone, old_Ps,Pa)  # Sandstone matrix density
            RHOFL,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('RHOFL', zone, old_Ps,Pa)   # Fluid matrix density
            RHOSH,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('RHOSH', zone, old_Ps,Pa)   # Density of ale
            PHIDSH,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('PHIDSH', zone, old_Ps,Pa) # Shale porosity
            DTFL,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('DTFL', zone, old_Ps,Pa)     # Dt of Fluid
            DTMA,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('DTMA', zone, old_Ps,Pa)     # Dt of matrix
            DTSH,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('DTSH', zone, old_Ps,Pa)     # Dt of Shale (matrix)
            cp,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('CP', zone, old_Ps,Pa)         # compaction coeficient of Willi Time Average
            alpha,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('ALPHA', zone, old_Ps,Pa)   # coeficient of Raymer-Hunt-Gardner
            # CPOR slope, intercept and dependant porosity curve
            #cslope
            #cintercpt
            #depcrv
            # (the alpha(5/8) ranges from 0.625-0.70, 0.67-most, 0.60-gas reservoirs)
            cp_rc,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('CP_RC', zone, old_Ps,Pa)   # coeficient of Raiga-Clemenceau
            x=1/cp_rc                                                                                                     #
            cp_fo,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('CP_FO', zone, old_Ps,Pa)    # Field observation coeficient

            if fl_RHOB==1:
                    # Calculated Effective Density Porosity 
                    #fl_RHOB==1:
                    #Density Porosity for reservoirs
                    def den(RHOB, RHOMA, RHOFL):
                        return (RHOMA-RHOB)/(RHOMA-RHOFL)
                    
                    if not RHOB.iloc[idx_top:idx_bot].empty:   #if not empty
                        PHID.iloc[idx_top:idx_bot] =den(RHOB.iloc[idx_top:idx_bot], RHOMA, RHOFL).clip(0.6, 0)

                    #Effective Density Porosity
                    if not RHOB.iloc[idx_top:idx_bot].empty:   #if not empty
                        PHIE_D.iloc[idx_top:idx_bot]= PHID.iloc[idx_top:idx_bot] - VCLFn.iloc[idx_top:idx_bot]*PHIDSH

            if fl_XP==1:
                    '''
                    crv1 NPSS.iloc[idx_top:idx_bot]
                    crv2 PHID.iloc[idx_top:idx_bot]
                    crv3 VCLFn.iloc[idx_top:idx_bot]
                    '''
                    #if both RHOB and NPSS available
                    #
                    #Cross-Plot Neutron Density Porosity
                    def phixnd(PHID, NPSS):
                        return (PHID+NPSS)/2
                    if not PHIND.iloc[idx_top:idx_bot].empty:   #if not empty
                        PHIND.iloc[idx_top:idx_bot]=phixnd(PHID.iloc[idx_top:idx_bot],NPSS.iloc[idx_top:idx_bot]).clip(0.6, 0)

                    # Gas correction Neutron Density cross plot
                    def phind_gas(PHID, NPSS):
                        return ((np.power(PHID,2)+np.power(NPSS,2))/2)**(0.5)
                    if not PHIT_GAS.iloc[idx_top:idx_bot].empty:   #if not empty
                        PHIT_GAS.iloc[idx_top:idx_bot]=phind_gas(PHID.iloc[idx_top:idx_bot],NPSS.iloc[idx_top:idx_bot]).clip(0.6, 0)
                    
                    # Shale Corrected porosity - PHIE
                    if not PHIE_ND.iloc[idx_top:idx_bot].empty and not PHIND.empty :   #if not empty
                        PHIE_ND.iloc[idx_top:idx_bot]= PHIND.iloc[idx_top:idx_bot] - VCLFn.iloc[idx_top:idx_bot]*PHIDSH
                    if not PHIE_GAS.iloc[idx_top:idx_bot].empty:   #if not empty
                        PHIE_GAS.iloc[idx_top:idx_bot]= PHIT_GAS.iloc[idx_top:idx_bot] - VCLFn.iloc[idx_top:idx_bot]*PHIDSH

            if fl_DT==1:
                    #fl_DT==1
                    # Willie-Time Average
                    def phis_wta(DT, DTMA, DTFL, cp):
                        ans= (1/cp)*(DT-DTMA)/(DTFL-DTMA)
                        return ans
                    if not  PHIS_WTA.iloc[idx_top:idx_bot].empty:   #if not empty
                        PHIS_WTA.iloc[idx_top:idx_bot]= phis_wta(DT.iloc[idx_top:idx_bot], DTMA, DTFL, cp)

                    # Raymer-Hunt-Gardner (the alpha(5/8) ranges from 0.625-0.70, 0.67-most, 0.60-gas reservoirs)
                    def phis_rhg(DT, DTMA, alpha):
                        return (alpha)*(DT-DTMA)/(DT)
                    if not  PHIS_RHG.iloc[idx_top:idx_bot].empty:   #if not empty
                        PHIS_RHG.iloc[idx_top:idx_bot]=phis_rhg(DT.iloc[idx_top:idx_bot], DTMA, alpha)

                    # Sonic Porosity Raiga-Clemenceau
                    def phis_rc(DT, DTMA, cp_rc,x):
                        return np.power(1-(DTMA/DT),x)
                    if not  PHIS_RC.iloc[idx_top:idx_bot].empty:   #if not empty
                        PHIS_RC.iloc[idx_top:idx_bot]=phis_rc(DT.iloc[idx_top:idx_bot], DTMA, cp_rc, x)

                    # Sonic Porosity from Field observation
                    def phis_fo(DT, DTMA, cp_fo):
                        return cp_fo*(DT-DTMA)/DT
                    if not  PHIS_FO.iloc[idx_top:idx_bot].empty:   #if not empty
                        PHIS_FO.iloc[idx_top:idx_bot] = phis_fo(DT.iloc[idx_top:idx_bot], DTMA, cp_fo)
                                
            if CSE==4:    #calculate core porosity
                    pass
                                                                                             
                                                                                                            
        if mytry==True:
            #plot results in Dpt_plot for each well

            '''
            Defined in depth plot
            color_list=['green', 'palegreen','red','lightcoral','olive','blue','cyan' ,'magenta','purple','gold','lightgrey', 'black', 'darkblue', 'lightblue', 'gray','yellow','orange']
            line_list=['dotted','solid','dashed','dashdot',(0,(3,1,1,1)),(0,(4, 2, 1, 2)),(0,(3,1,1,1,1,1))]
            tick_list=[[0, 50, 100, 150, 200],[0.45, 0.3, 0.15, 0, -0.15],[0.60, 0.45, 0.30, 0.15, 0],[0.0, 0.25, 0.5, 0.75, 1.0],[1.95, 2.2, 2.45, 2.7, 2.95],[500,400,300,200,100],[-0.15,0.15,0.45,0.75,1.05],[1000,750,500,250,0.0],[0.1,1,10,100,1000],[0.2,2,20,200,2000],[0, 0.15, 0.30, 0.45, 0.60],
            [-0.75,-0.50,-0.25,0.0,0.25],[0,5,10,15,20],[300,200,100,0,-100],[150,200,250,350,400],[0,0.5,1,1.5,2],[1000,100,10,1,0.1],[2000,200,20,2,0.2],[1.65, 1.90, 2.15, 2.4, 2.65],[-2,0,2,4,6]]
            scale (0=default or 'lin', 1='log')
            marker_list=['o','O','s','d','D','x','X','h','+','*','^','']

            props[color, linestyle, ticks, scale , marker, track, ---- empty fill parms]
            '''
            #Define top and bottom of plot
            zoneDepths = ZoneDepths(top=las_start, base=las_stop, name="WELL")
            wellname = las_data.well.WELL.value
            if wellname=='':
                wellname=las_data.well.uwi

            if fl_DT==1 and fl_XP>=1:      # if fl_XP=1 then fl_RHOB is also set
                # GR_NRM = c1, c1 = DT, NPSS = c3, DPSS = c4,  VCL_FN = c5, PHIND = c6, PHID= c7, PHIE_D = c8, PHIE_ND = c9
                # PHIE_GAS = c10, PHIS_WTA = c11, PHIS_RHG = c12, PHIS_RC =c13, PHIS_FO =c14

                c1=global_vars.las_df['GR_NRM']     #NRM GR
                c2=DT         #SONIC
                c3=global_vars.las_df[NPS]          #NEUTRON POR
                c4=global_vars.las_df[DPS]          #DENSITY POR
                c5=global_vars.las_df['VCL_FN']     #FINAL VCLAY
                c6=PHIND            #NEUTRON-DENSITY XPLOT POR
                c7=PHID             #DENSITY POR
                c8=PHIE_D           #SHALE CORRECTED DENSITY POR
                c9=PHIE_ND          #SHALE CORRECTED NEUTRON-DENSITY XPLOT POR
                c10=PHIT_GAS        #GAS CORRECTED TOTAL POROSITY   
                c11=PHIS_WTA        #SONIC WTA
                c12=PHIS_RHG        #SONIC RHG
                c13=PHIS_RC         #SONIC RC
                c14=PHIS_FO         #SONIC FO

                trcks=5
                curvs=[c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14]
                #[color, linestyle, ticks, scale , marker, track --- empty Fill parms]
                props=[[0,1,0,0,11,1,'','','','','',''],[8,1,5,0,11,1,'','','','','',''],[5,2,2,0,11,2,'','','','','',''],[2,1,2,0,11,2,'','','','','',''],[0,1,3,0,11,3,'','','','','',''],[6,2,2,0,11,4,'','','','','',''],[5,1,2,0,11,4,'','','','','',''],
                        [14,1,2,0,11,4,'','','','','',''],[8,1,2,0,11,4,'','','','','',''],[2,1,2,0,11,4,'','','','','',''],[7,1,2,0,11,5,'','','','','',''],[11,1,2,0,11,5,'','','','','',''],[5,1,2,0,11,5,'','','','','',''],[2,1,2,0,11,5,'','','','','','']]

            if fl_DT==0 and fl_XP>=1:    # if fl_XP=1 then fl_RHOB is also set
                # GR_NRM = c1, NPSS = c2, DPSS = c3,  VCL_FN = c4, PHIND = c5, PHID= c6, PHIE_D = c7, PHIE_ND = c8
                # PHIE_GAS = c9

                c1=global_vars.las_df['GR_NRM']
                c2=global_vars.las_df[NPS]
                c3=global_vars.las_df[DPS]
                c4=global_vars.las_df['VCL_FN']
                c5=PHIND            #NEUTRON-DENSITY XPLOT POR
                c6=PHID             #DENSITY POR
                c7=PHIE_D           #SHALE CORRECTED DENSITY POR
                c8=PHIE_ND          #SHALE CORRECTED NEUTRON-DENSITY XPLOT POR
                c9=PHIE_GAS          #SHALE and gas CORRECTED NEUTRON-DENSITY

                trcks=4
                curvs=[c1, c2, c3, c4, c5, c6, c7, c8, c9]
                #[color, linestyle, ticks, scale , marker, track --- empty Fill parms]
                props=[[0,1,0,0,11,1,'','','','','',''],[5,2,2,0,11,2,'','','','','',''],[2,1,2,0,11,2,'','','','','',''],[0,1,3,0,11,3,'','','','','',''],[5,2,2,0,11,4,'','','','','',''],[11,1,2,0,11,4,'','','','','',''],
                        [7,1,2,0,11,4,'','','','','',''],[6,1,2,0,11,4,'','','','','',''],[2,1,2,0,11,4,'','','','','','']]

            if fl_RHOB==1 and fl_XP==0 and fl_DT==0:                     #If only RHOB but no PNSS
                # GR_NRM = c1, DPSS = c2,  VCL_FN = c3, PHID= c4, PHIE_D = c5
                # PHIE_GAS = c9

                c1=global_vars.las_df['GR_NRM']
                c2=global_vars.las_df[RHB]
                c3=global_vars.las_df['VCL_FN']
                c4=global_vars.las_df['PHID']
                c5=global_vars.las_df['PHIE_D']

                trcks=4
                curvs=[c1, c2, c3, c4, c5]
                props=[[0,1,0,0,11,1,'','','','','',''],[5,2,4,0,11,2,'','','','','',''],[0,1,3,0,11,3,'','','','','',''],[7,1,2,0,11,4,'','','','','',''],
                    [2,1,2,0,11,4,'','','','','','']]

            if fl_DT==1 and fl_RHOB==1 and fl_XP==0:
                # GR_NRM = c1, VCL_FN = c2, DT = c3, PHID = c4, PHIE_D = c5, PHIS_WTA = c6, PHIS_RHG = c7, PHIS_RC =c8, PHIS_FO =c9
                c1=global_vars.las_df['GR_NRM']
                c2=global_vars.las_df['VCL_FN']
                c3=global_vars.las_df[DTS]
                c4=global_vars.las_df['PHID']
                c5=global_vars.las_df['PHIE_D']
                c6=global_vars.las_df['PHIS_WTA']
                c7=global_vars.las_df['PHIS_RHG']
                c8=global_vars.las_df['PHIS_RC']
                c9=global_vars.las_df['PHIS_FO']

                trcks=3
                curvs=[c1, c2, c3, c4, c5, c6, c7, c8, c9]
                props=[[0,1,0,0,11,1,'','','','','',''],[4,1,3,0,11,1,'','','','','',''],[8,1,5,0,11,1,'','','','','',''],[7,1,2,0,11,2,'','','','','',''],[4,1,2,0,11,2,'','','','','',''],[6,1,2,0,11,3,'','','','','',''],[11,1,2,0,11,3,'','','','','',''],[5,1,2,0,11,3,'','','','','',''],[2,1,2,0,11,3,'','','','','','']]

            if fl_DT==1 and fl_RHOB==0 and fl_XP==0:
                # GR_NRM = c1,DT = c2, PHIS_WTA = c3, PHIS_RHG = c4, PHIS_RC =c5, PHIS_FO =c6
                c1=global_vars.las_df['GR_NRM']
                c2=global_vars.las_df[DTS]
                c3=global_vars.las_df['PHIS_WTA']
                c4=global_vars.las_df['PHIS_RHG']
                c5=global_vars.las_df['PHIS_RC']
                c6=global_vars.las_df['PHIS_FO']

                trcks=2
                curvs=[c1, c2, c3, c4, c5, c6 ]
                props=[[0,1,0,0,11,1,'','','','','',''],[7,1,5,0,11,1,'','','','','',''], [2,1,2,0,11,2,'','','','','',''],[11,1,2,0,11,2,'','','','','',''],[4,1,2,0,11,2,'','','','','',''],[7,1,2,0,11,2,'','','','','','']]
            # Dpt_plt(wellname, curvs, fcrvs, props, trcks, pltype=0, Fms)
            depthPlot = DepthPlot()
            depthPlot.depthPlot(wellname, curvs, fcrvs, props, trcks, DepthPlot.DepthPlotType.DepthPlot, well.formations, zoneDepths)
            #DepthPlot.newDepthPlot(wellname, curvs, fcrvs, props, trcks, 0, fm_list)
            if well == WellList[-1]:    # only ask in final well of trial run
                if not (fl_DT==1 and fl_RHOB==0 and fl_XP==0):
                    self.Phie_Fn=self.selectFinalCurve(fn2_list)
                self.Phi_Fn=self.selectFinalCurve(fn1_list)
                mytry=False

    #Select and save calculated curves
    if mytry==False:      #Phi_Fn and Phie_Fn only set in trial run as global

        if self.Phi_Fn is None or self.Phie_Fn is None:
            alert.RaiseException("First select Phi_Fn and/or PHIE_fn in trial run")

        #select Final Well List and start new WellList loop
        if global_vars.project.loadWellListPrompt()==False:
            return
        #global_vars.ui.Root.Update()
        WellList=global_vars.project.currentWellList.GetWells()
        total_wells = len(WellList) 
        count = 0   # for well counter on Root
        for well in WellList:
            #load load las from Outdir
            las_data=well.GetLASData(Dir.Out)
            
            if las_data is None:
                alert.Error(ErrorMessage.FAILED_LOAD_LAS, [Dir.Out, well])
                continue

            las_start=las_data.well.STRT.value
            las_stop=las_data.well.STOP.value
            global_vars.las_df=las_data.df()

            lascurves=las_data.curves

            #Initialization of logs
            NPS='NPSS_NRM'
            RHB='RHOB_NRM'

            #Check for preferred input curves    
            if RHB not in lascurves:
                RHB='RHOB'    #replace
            if DPS not in lascurves:
                DPS='DPSS'    #replace
            if NPS not in lascurves:
                NPS='NPSS'    #replace
            if DTS not in lascurves:
                DTS='DT'      #replace

            #flags
            fl_RHOB=0   #RHOB flag
            fl_XP=0     #Crossplot flag
            fl_DT=0     #Sonic flag

            # select porosity calculations
            if RHB not in lascurves:                   #If no RHOB in LAS file
                if DPS in lascurves:                   #But if there is a SS scale density porosity curve
                    global_vars.las_df[RHB]=2.650-1.650*global_vars.las_df[DPS]     # create a RHOB curve
            if DPS not in lascurves:                   #If no DPSS in LAS file
                if RHB in lascurves:                   #But if there is a Bulk density curve
                    global_vars.las_df[DPS]=(2.650-global_vars.las_df[RHB])/1.650   # create a DPSS curve
                #else
            #Get and obtain curves and flags
            #Neutron Density Xplot
                    
            #VCL_FN for shale corrections
            if 'VCL_FN' in lascurves:
                VCLFn=global_vars.las_df['VCL_FN'].copy()
            else:
                alert.Error.ErrorMessage.MISSING_CURVE_CREATE, [zone, well]
                return
                    
            if RHB in lascurves:
                fn1_list.append('PHISH')
                fn1_list.append('PHID')
                fn2_list.append('PHIE_D')
                RHOB =global_vars.las_df[RHB].copy()
                global_vars.las_df['PHISH']=np.nan        #Shale correction curve for PHIE_D
                PHISH=global_vars.las_df['PHISH'].copy()
                global_vars.las_df['PHID']=np.nan
                PHID=global_vars.las_df['PHID'].copy()
                NPSS=global_vars.las_df['NPSS'].copy()
                global_vars.las_df['PHIE_D']=np.nan
                PHIE_D=global_vars.las_df['PHIE_D'].copy()
                CSE = 1
                fl_RHOB=1

            if NPS in lascurves:
                fn1_list.append('PHIT_GAS')
                fn1_list.append('PHIND')
                fn2_list.append('PHIE_ND')
                fn2_list.append('PHIE_GAS')
                global_vars.las_df['PHIT_GAS']=np.nan
                PHIT_GAS=global_vars.las_df['PHIT_GAS'].copy()
                global_vars.las_df['PHIND']=np.nan
                PHIND=global_vars.las_df['PHIND'].copy()
                global_vars.las_df['PHIE_ND']=np.nan
                PHIE_ND=global_vars.las_df['PHIE_ND'].copy()
                global_vars.las_df['PHIE_GAS']=np.nan
                PHIE_GAS=global_vars.las_df['PHIE_GAS'].copy()
                CSE = 2
                fl_XP=1

            # Sonic porosities
            if DTS in lascurves:
                fn1_list.append('PHIS_WTA')
                fn1_list.append('PHIS_RHG')
                fn1_list.append('PHIS_RC')
                fn1_list.append('PHIS_FO')
                DT = global_vars.las_df[DTS].copy()
                global_vars.las_df['PHIS_WTA']=np.nan

                PHIS_WTA=global_vars.las_df['PHIS_WTA'].copy()
                global_vars.las_df['PHIS_GAS']=np.nan
                PHIE_GAS=global_vars.las_df['PHIE_GAS'].copy()
                global_vars.las_df['PHIS_RHG']=np.nan
                PHIS_RHG=global_vars.las_df['PHIS_RHG'].copy()
                global_vars.las_df['PHIS_RC']=np.nan
                PHIS_RC=global_vars.las_df['PHIS_RC'].copy()
                global_vars.las_df['PHIS_FO']=np.nan
                PHIS_FO=global_vars.las_df['PHIS_FO'].copy()
                CSE = 3
                fl_DT=1

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
                    zoneDepths = well.GetZoneDepths(zone)

                    if zoneDepths is None:
                        alert.Error(ErrorMessage.MISSING_FORMATION_ZONE_SKIP, [zone, well])
                        #global_vars.ui.Root.window.deiconify()

                        continue

                    #set depth interval
                    idx_top=int((zoneDepths.top - las_start)/cstep)
                    idx_bot=int((zoneDepths.base - las_start)/cstep)+1  #get very last of array

                # Now do all calculations using updated params
                #Set the Params for calculation
                # Porosity parameters
                Pa=11
                #old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('GRCL', zone, old_Ps,Pa)
                RHOMA,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('RHOMA', zone, old_Ps,Pa)  # Sandstone matrix density
                RHOFL,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('RHOFL', zone, old_Ps,Pa)   # Fluid matrix density
                RHOSH,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('RHOSH', zone, old_Ps,Pa)   # Density of ale
                PHIDSH,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('PHIDSH', zone, old_Ps,Pa) # Shale porosity
                DTFL,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('DTFL', zone, old_Ps,Pa)     # Dt of Fluid
                DTMA,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('DTMA', zone, old_Ps,Pa)     # Dt of matrix
                DTSH,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('DTSH', zone, old_Ps,Pa)     # Dt of Shale (matrix)
                cp,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('CP', zone, old_Ps,Pa)         # compaction coeficient of Willi Time Average
                alpha,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('ALPHA', zone, old_Ps,Pa)   # coeficient of Raymer-Hunt-Gardner
                # CPOR slope, intercept and dependant porosity curve
                #cslope
                #cintercpt
                #depcrv
                                                                                                                    # (the alpha(5/8) ranges from 0.625-0.70, 0.67-most, 0.60-gas reservoirs)
                cp_rc,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('CP_RC', zone, old_Ps,Pa)   # coeficient of Raiga-Clemenceau
                x=1/cp_rc                                                                                                     #
                cp_fo,old_Ps= global_vars.project.formationZoneParameters.CalculateZoneParameters('CP_FO', zone, old_Ps,Pa)    # Field observation coeficient
            
                if fl_RHOB==1:        
                        #Density Porosity for reservoirs
                        if not RHOB.empty:   #if not empty self.Phie_Fn
                            #RHOB.iloc[idx_top:idx_bot]=RHOB.iloc[idx_top:idx_bot].clip(4,0)
                            #print(RHOB.iloc[idx_top:idx_bot])
                            PHID.iloc[idx_top:idx_bot] =den(RHOB.iloc[idx_top:idx_bot], RHOMA, RHOFL) #.clip(0.6, 0)

                        #Effective Density Porosity
                        if not RHOB.empty:   #if not empty
                            PHIE_D.iloc[idx_top:idx_bot]= PHID.iloc[idx_top:idx_bot] - VCLFn.iloc[idx_top:idx_bot]*PHIDSH
                            PHIE_D.iloc[idx_top:idx_bot].clip(0.6, 0)

                if fl_XP==1:
                #if self.Phi_Fn=='PHIND' or self.Phi_Fn=='PHIT_GAS' or self.Phi_Fn=='PHIND' or self.Phie_Fn=='PHIE_ND' or self.Phie_Fn=='PHIE_GAS':
                        '''
                        NPSS.iloc[idx_top:idx_bot]
                        PHID.iloc[idx_top:idx_bot]
                        VCLFn.iloc[idx_top:idx_bot]
                        '''
                        #if both RHOB and NPSS available
                        #fl_XP==1
                        #Cross-Plot Neutron Density Porosity
                        if not PHIND.empty:   #if not empty
                            PHIND.iloc[idx_top:idx_bot]=phixnd(PHID.iloc[idx_top:idx_bot],NPSS.iloc[idx_top:idx_bot]).clip(0.6, 0)

                        # Gas correction Neutron Density cross plot
                        if not PHIT_GAS.empty:   #if not empty
                            PHIT_GAS.iloc[idx_top:idx_bot]=phind_gas(PHID.iloc[idx_top:idx_bot],NPSS.iloc[idx_top:idx_bot]).clip(0.6, 0)
                        
                        # Shale Corrected porosity - PHIE
                        if not  PHIE_ND.empty and not PHIND.empty :   #if not empty
                            PHIE_ND.iloc[idx_top:idx_bot]= PHIND.iloc[idx_top:idx_bot] - VCLFn.iloc[idx_top:idx_bot]*PHIDSH
                        if not PHIE_GAS.empty:   #if not empty
                            PHIE_GAS.iloc[idx_top:idx_bot]= PHIT_GAS.iloc[idx_top:idx_bot] - VCLFn.iloc[idx_top:idx_bot]*PHIDSH

                if fl_DT==1:
                #if self.Phi_Fn=='PHIS_WTA' or self.Phi_Fn=='PHIS_RGH' or self.Phi_Fn=='PHIS_RC' or self.Phi_Fn=='PHIS_FO':
                        #fl_DT==1
                        # Willie-Time Average
                        if not  PHIS_WTA.iloc[idx_top:idx_bot].empty:   #if not empty
                            PHIS_WTA.iloc[idx_top:idx_bot]= phis_wta(DT.iloc[idx_top:idx_bot], DTMA, DTFL, cp)

                        # Raymer-Hunt-Gardner (the alpha(5/8) ranges from 0.625-0.70, 0.67-most, 0.60-gas reservoirs)
                        if not  PHIS_RHG.iloc[idx_top:idx_bot].empty:   #if not empty
                            PHIS_RHG.iloc[idx_top:idx_bot]=phis_rhg(DT.iloc[idx_top:idx_bot], DTMA, alpha)

                        # Sonic Porosity Raiga-Clemenceau
                        if not  PHIS_RC.iloc[idx_top:idx_bot].empty:   #if not empty
                            PHIS_RC.iloc[idx_top:idx_bot]=phis_rc(DT.iloc[idx_top:idx_bot], DTMA,cp_rc, x)

                        # Sonic Porosity from Field observation
                        if not  PHIS_FO.iloc[idx_top:idx_bot].empty:   #if not empty
                            PHIS_FO.iloc[idx_top:idx_bot] = phis_fo(DT.iloc[idx_top:idx_bot], DTMA, cp_fo)

                if CSE==4:    #calculate core porosity
                        pass

            #update las_df
            c=''
            if self.Phi_Fn=='PHISH':
                c=PHISH
            elif self.Phi_Fn=='PHID':
                c=PHID
            elif self.Phi_Fn=='PHIT_GAS':
                c=PHIT_GAS
            elif self.Phi_Fn=='PHIND':
                c=PHIND
            elif self.Phi_Fn=='PHIS_WTA':
                c=PHIS_WTA
            elif self.Phi_Fn=='PHIS_RHG':
                c=PHIS_RHG
            elif self.Phi_Fn=='PHIS_RC':
                c=PHIS_RC
            elif self.Phi_Fn=='PHIS_FO':
                c=PHIS_FO

            global_vars.las_df['PHI_FN']=c

            if self.Phie_Fn=='PHIE_D':
                c=PHIE_D
            elif self.Phie_Fn=='PHIE_ND':
                c=PHIE_ND
            elif self.Phie_Fn=='PHIE_GAS':
                c=PHIE_GAS
            
            global_vars.las_df['PHIE_FN']=c
            
            filename=well.uwi + ".las"

            #cull unused curve in las.
            for fn in fn1_list:
                if fn in global_vars.las_df:
                    global_vars.las_df.drop(fn,axis=1, inplace=True)
            for fn in fn2_list:
                if fn in global_vars.las_df:
                    global_vars.las_df.drop(fn,axis=1, inplace=True)
            
            # save curve in las with curvename = Phie_Fn and/or Phi_Fn
            if self.Phie_Fn is not None:            #if Phie_Fn has been selected
                las.save_curves(filename, 'PHIE_FN', self.Phie_Fn)
            if self.Phi_Fn is not None:                # save Phi_Fn has been selected
                las.save_curves(filename, 'PHI_FN', self.Phi_Fn)

            count +=1
            '''
            global_vars.ui.Root.window.deiconify()
            global_vars.ui.Root.c_mylabel.configure(text='Well '+str(count) + ' of ' + total_wells)
            global_vars.ui.Root.window.update_idletasks()
            '''
            
        #Done with interpreter calculations    
        alert.Message("Scan")   
        global_vars.project.Scan ()
        alert.Message("Updating Project")
        global_vars.ui.Root.Update()  
        global_vars.ui.Root.window.deiconify()



