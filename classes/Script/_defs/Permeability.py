'''perm_scripts'''


import numpy as np
from classes.Project.Parameter import ZoneParameter

import global_vars
from tkinter import messagebox
from classes.Plot.DepthPlot import DepthPlot
from defs import alert, excel, las, program, prompt
from enumerables import Dir, ErrorMessage
from structs import ZoneDepths

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Script

def Permeability(self : 'Script'):
    '''
    standard log analysis Permeability calculations using build-in scripts
    '''

    global_vars.ui.Root.window.iconify()

    mmessage='Is this a trial run (Yes) or the Final run (No)'
    mytry=prompt.yesno(mmessage)
    if mytry==False:
        if self.K_Fn is None:
            alert.RaiseException("First select K_Fn in trial run")

    fcrvs=[]                  # curves for dpt plt fills

   #input curves
    crv_list=[]
    input_list=['PHI_FN','PHIE_FN']
    mylist=""
    for x in input_list:
           mylist=mylist + x + ', '
    mylist=mylist[:-1]
    mmessage=mylist +" curves are required. Continue?"
    myYN=prompt.yesno(mmessage)
    if myYN==False: return
    
    nocurves=['DEPT', 'None']
    crv_list = program.com_crvs(nocurves,crv_list,0)

    yn=True
    for inp in input_list:
        if inp not in crv_list:
            yn=prompt.yesno(inp + " not in every well, continue yes or no")

    if yn==False:           #return to main
        return

    #crvnm contains calculatable curve lists - already defined in mainwell
    #loop through wells
    for well in global_vars.project.currentWellList.GetWells():
        fn_list=[]                #list of curve names for final selection total porosity
       
        #load load las from Outdir
        las_data = well.GetLASData(Dir.Out)
        if las_data is None:
            alert.Error(ErrorMessage.FAILED_LOAD_LAS, [Dir.Out, well])
            continue

        las_start=las_data.well.STRT.value
        las_stop=las_data.well.STOP.value
        global_vars.las_df=las_data.df()

        if 'PHI_FN' not in las_data.curves and 'PHIE_FN' not in las_data.curves:
            alert.Error(f"Missing porosity curves PHI_FN and PHIE_FN in {well.uwi}({well.alias}) - well skipped")
            continue

        #Initialization of curves
        #for PERM CalCulations
        global_vars.las_df['PERM_COAT']=np.nan
        PERM_COAT=global_vars.las_df['PERM_COAT'].copy()
        global_vars.las_df['PERM_TIM']=np.nan
        PERM_TIM=global_vars.las_df['PERM_TIM'].copy()
        global_vars.las_df['PERM_TIX']=np.nan
        PERM_TIX=global_vars.las_df['PERM_TIX'].copy()
        global_vars.las_df['PERM_COR']=np.nan
        PERM_COR=global_vars.las_df['PERM_COR'].copy()
        global_vars.las_df['SWIRR']=np.nan
        SWIR=global_vars.las_df['SWIRR'].copy()
        PHI_FN=global_vars.las_df['PHI_FN'].copy()
        PHIE_FN=global_vars.las_df['PHIE_FN'].copy()

        fn_list=['PERM_COR','PERM_COAT','PERM_TIM','PERM_TIX']

        mzones=global_vars.project.formationZoneParameters.Zone_list()
        old_Ps=[]     # list of parameters that may need to be restored based on Zonetypes
        for zone in mzones:
            #params = global_vars.project.formationZoneParameters.GetCalculatedZoneParameters(zone)
            #old_Ps=[]       # list of parameters that may need to be restored based on Zonetypes
            cstep=0.1
            if zone == 'DEFAULT':
                #set depth interval
                idx_top=0
                idx_bot=int((las_stop - las_start)/cstep)+1  #get very last of array
            else:
                zoneDepths = well.GetZoneDepths(zone)

                if zoneDepths is None:
                    alert.Error(ErrorMessage.MISSING_FORMATION_ZONE, [zone, well])
                    global_vars.ui.Root.window.deiconify()
                    continue

                #set depth interval
                idx_top=int((zoneDepths.top - las_start)/cstep)
                idx_bot=int((zoneDepths.base - las_start)/cstep)+1  #get very last of array

            # Now do all calculations using updated params
            #Set the Params for calculation
            # Porosity parameters
            Pa=4
            Kslope,old_Ps  = global_vars.project.formationZoneParameters.CalculateZoneParameters('KMAX_SLOPE',zone, old_Ps, Pa)    #KMAX - PHI_Fn slope
            Kint,old_Ps    = global_vars.project.formationZoneParameters.CalculateZoneParameters('KMAX_INTPT',zone, old_Ps, Pa)     #KMAX - PHI_Fn intercept
            hlm_a,old_Ps   = global_vars.project.formationZoneParameters.CalculateZoneParameters('HLM_A', zone, old_Ps, Pa)        # Holmes constant
            hlm_m,old_Ps   = global_vars.project.formationZoneParameters.CalculateZoneParameters('HLM_M', zone, old_Ps, Pa)        # Holmes  Porosity exponent

            # Calculate Permeability
            # Irriduciable Water Saturation
            SWIR.iloc[idx_top:idx_bot] = ((hlm_a/PHI_FN.iloc[idx_top:idx_bot])**(hlm_m)).clip(0,1)

            #CORE PERMEABILITY
            PERM_COR.iloc[idx_top:idx_bot] = (10**(Kslope*PHI_FN.iloc[idx_top:idx_bot]+Kint)).clip(0.1,2000)

            # COATES PERMEABILITY
            PERM_COAT.iloc[idx_top:idx_bot] = (( 70 * (PHIE_FN.iloc[idx_top:idx_bot]**2) * ( 1-SWIR.iloc[idx_top:idx_bot])/SWIR.iloc[idx_top:idx_bot])**2).clip(0.1,2000)

            #TIMUR PERMEABILITY
            PERM_TIM.iloc[idx_top:idx_bot]= (( 100 * (PHIE_FN.iloc[idx_top:idx_bot]**2.25) / SWIR.iloc[idx_top:idx_bot])**2).clip(0.1,2000)

            #TIXIER PERMEABILITY
            PERM_TIX.iloc[idx_top:idx_bot] = (( 250 * (PHIE_FN.iloc[idx_top:idx_bot]**3) / SWIR.iloc[idx_top:idx_bot] )**2).clip(0.1,2000)

        if mytry==True:
            #plot results in Dpt_plot for each well with 6 tracks
            #Define top and bottom of plot
            zoneDepths = ZoneDepths(top=las_start, base=las_stop, name="WELL")
            # PHI_FN = c1, PHIE_FN = c2, PERM_COAT = c3, PERM_TIM = c4, PERM_TIX = c5, PERM_CORE = c6

            c1=PHI_FN
            c1.name='PHI_FN'
            c2=PHIE_FN
            c2.name='PHIE_FN'
            c3=PERM_COAT
            c3.name='PERM_COAT'
            c4=PERM_TIM
            c4.name='PERM_TIM'
            c5=PERM_TIX
            c5.name='PERM_TIX'
            c6=PERM_COR
            c6.name='PERM_COR'

            curvs=[c1, c2, c3, c4, c5, c6 ]
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

            props=[[2,1,2,0,11,1,'','','','','',''],[7,1,2,0,11,1,'','','','','',''],[11,1,8,1,11,2,'','','','','',''],[5,2,8,1,11,2,'','','','','',''],[2,0,8,1,11,2,'','','','','',''],[6,1,8,1,11,2,'','','','','','']]
            wellname = las_data.well.WELL.value
            if wellname == '':
                message=f"Wellname not in las or cas file of {well.uwi} well, please correct'"
                messagebox.showinfo(message=message)
                return

            depthPlot = DepthPlot()
            depthPlot.depthPlot(wellname, curvs, fcrvs, props, 2, DepthPlot.DepthPlotType.DepthPlot, well.formations, zoneDepths)
            #DepthPlot.newDepthPlot(wellname, curvs, fcrvs, props, 2, 0, fm_list)
            if well.uwi == global_vars.project.currentWellList[-1]:    # only ask in final well of trial run
                #self.K_Fn=self.selectFinalCurve(fn_list)
                self.K_Fn=self.selectFinalCurve( fn_list)
                mytry=False
                

        #Save calculated curves
        if mytry==False:      #K_Fn only set in trial run as global
            if self.K_Fn is None:
                alert.RaiseException("First select K_FN in trial run")

            #'PERM_COR','PERM_COAT','PERM_TIM','PERM_TIX'
            if self.K_Fn=='PERM_TIX':
                global_vars.las_df['K_FN']=PERM_TIX
            if self.K_Fn=='PERM_TIM':
                global_vars.las_df['K_FN']=PERM_TIM
            if self.K_Fn=='PERM_COAT':
                global_vars.las_df['K_FN']=PERM_COAT
            if self.K_Fn=='PERM_COR':
                global_vars.las_df['K_FN']=PERM_COR

            #cull unused curve in las.
            for fn in fn_list:
                if fn in global_vars.las_df:
                    global_vars.las_df.drop(fn,axis=1, inplace=True)


            las_data.set_data(global_vars.las_df)    #update las_data
            las.save_curves(well.uwi+'.las', 'K_FN',self.K_Fn)                # save curve in las with curvename = Phit_Fn

    global_vars.ui.Root.window.deiconify()