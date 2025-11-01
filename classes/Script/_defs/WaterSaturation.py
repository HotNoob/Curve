'''SW_scripts'''

import numpy as np
from classes.Project.Parameter import ZoneParameter

from enumerables import Dir, ErrorMessage
import global_vars
from defs import alert, excel, las, prompt, program
from classes.Plot.DepthPlot import DepthPlot
from structs import ZoneDepths

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Script

#-------------------------------------------------------------------------------------------------------
def WaterSaturation(self : 'Script'):
    '''
    Standard log analysis Watersaturation calculations using build-in scripts
    Archie, Tixier Swir from Permeability-holmes
    Re-iterated Simandoux and Dual Water

    '''

    global_vars.ui.Root.window.iconify()

    mmessage='Is this a trial run (Yes) or the Final run (No)'
    mytry=prompt.yesno(mmessage)
    if mytry==False:
        if self.SW_Fn is None:
            alert.RaiseException("First select SW_Fn in trial run")
    else:
        self.SW_Fn = None     #Clear SW_Fn
    
    
    fcrvs=[]                  # curves for dpt plt fills

    #input curves
    crv_list=[]
    input_list=['PHI_FN','PHIE_FN','VCL_FN','RT','TEMP']
    mylist=""
    for x in input_list:
        mylist=mylist + x + ', '
    mylist="These " + mylist[:-1]
    mmessage=mylist +" curves are often required. Continue?"
    myYN=prompt.yesno(mmessage)
    if myYN==False: return

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
        fn_list=[]                #list of curve names for final selection for Water saturation
        
        #load load las from Outdir
        las_data = well.GetLASData(Dir.Out)
        if las_data is None:
            alert.Error(ErrorMessage.FAILED_LOAD_LAS, [Dir.Out, well])
            continue

        #top and bottom of log interval
        las_start=las_data.well.STRT.value
        las_stop=las_data.well.STOP.value
        #data frame default
        global_vars.las_df=las_data.df()

        lascurves=las_data.curves
        if 'PHI_FN' not in lascurves:
            alert.Error(ErrorMessage.MISSING_POROSITY_CURVE_SKIP, ['PHI_FN', well])
            continue    #Next well
        
        if 'PHIE_FN'not in lascurves:
            alert.Error(ErrorMessage.MISSING_POROSITY_CURVE_SKIP, ['PHIE_FN', well])
            continue    #Next well

        if 'VCL_FN'not in lascurves:
            alert.Error(ErrorMessage.MISSING_POROSITY_CURVE_SKIP, ['VCL_FN', well])
            continue     #Next well

        #Initialization of new logs in default data frame
        #for Watersaturarion CalCulations
        global_vars.las_df['SW_TIX']=np.nan
        global_vars.las_df['SW_ARC']=np.nan
        global_vars.las_df['SW_DW2']=np.nan
        global_vars.las_df['RWC']=np.nan
        global_vars.las_df['SW_SIM_MOD']=np.nan

        #secondary curves default dataframe
        global_vars.las_df['sec']=np.nan 

        fn_list=['SW_SIM_MOD','SW_TIX','SW_ARC','SW_DW2']     #list of answer curves

        POR=global_vars.las_df['PHI_FN'].copy()
        PRE=global_vars.las_df['PHIE_FN'].copy()
        RTD=global_vars.las_df['RT'].copy()
        VCL=global_vars.las_df['VCL_FN'].copy()
        SW_SMOD=global_vars.las_df['SW_SIM_MOD'].copy()
        SW_ARC=global_vars.las_df['SW_ARC'].copy()
        SW_DW2=global_vars.las_df['SW_DW2'].copy()
        SW_TIX=global_vars.las_df['SW_TIX'].copy()
        TMPC=global_vars.las_df['TEMP'].copy()
        RWC=global_vars.las_df['RWC'].copy()

        #secondary curves
        b=global_vars.las_df['sec'].copy()
        rwa=global_vars.las_df['sec'].copy()
        sb=global_vars.las_df['sec'].copy()
        porpow1=global_vars.las_df['sec'].copy()
        x1=global_vars.las_df['sec'].copy()
        x2=global_vars.las_df['sec'].copy()
        x3=global_vars.las_df['sec'].copy()
        delta=global_vars.las_df['sec'].copy()
        #POR.clip(0,1)
        #PRE.clip(0,1)
        RTD.clip(0.1,1000)
        VCL.clip(0,1)

        mycol=1   # Set to default column
        #loop through default and zone types/levels 1-4
        mzones=global_vars.project.formationZoneParameters.Zone_list()
        old_Ps=[]       # list of parameters that may need to be restored based on Zonetypes 
        cstep=0.1   
        for zone in mzones:
            #params = global_vars.project.formationZoneParameters.GetCalculatedZoneParameters(zone)
            if zone == 'DEFAULT':
                #set depth interval
                idx_top=0
                idx_bot=int((las_stop - las_start)/cstep)+1  #get very last of array
            else:
                zoneDepths = well.GetZoneDepths(zone)

                if zoneDepths is None:
                    alert.Error(ErrorMessage.MISSING_FORMATION_ZONE_SKIP, [zone, well])
                    global_vars.ui.Root.window.deiconify()
                    continue

                #set depth interval
                idx_top=int((zoneDepths.top - las_start)/cstep)
                idx_bot=int((zoneDepths.base - las_start)/cstep)+1  #get very last of array


            # Now do all calculations using updated params
            Pa=7
            my_a,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('A', zone, old_Ps,Pa)  # A  for Archie. Activity
            my_m,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('M', zone, old_Ps,Pa)  # m  for Archie. Cementation exponent
            my_n,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('N', zone, old_Ps,Pa)  # m  for Archie. Tortuosity/Saturation exponent
            my_rw,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('RW', zone, old_Ps,Pa)  # RW formation water resistivity
            my_phidsh,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('PHIDSH', zone, old_Ps,Pa)  # Density Porosity of shale
            my_rsh,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('RSH', zone, old_Ps,Pa)  # Resistivity of shale
            m_sh,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('M_SH', zone, old_Ps,Pa)  # CementationExponent for shale in DW

            #hlm_a=para_df.iloc[29]['DEFAULT']
            #hlm_m=para_df.iloc[30]['DEFAULT']
            #m_sh = params['M_SH']

            #Calculate RW curve = RWC using TEMP (in C) curve
            RWC.iloc[idx_top:idx_bot]=my_rw*(25+21.5)/(TMPC.iloc[idx_top:idx_bot]+21.5)

            #SW_DW2
            #---------------------------------------------------
            #Clay Bound Water Saturation - CBW
            sb.iloc[idx_top:idx_bot]=(VCL.iloc[idx_top:idx_bot]*my_phidsh)/POR.iloc[idx_top:idx_bot]
            porpow1.iloc[idx_top:idx_bot]=np.power(POR.iloc[idx_top:idx_bot], my_m)
            rwa.iloc[idx_top:idx_bot]=RTD.iloc[idx_top:idx_bot]*porpow1.iloc[idx_top:idx_bot]
            rb = my_rsh*(my_phidsh**m_sh)

            # The Bound Water Resistivity
            b.iloc[idx_top:idx_bot]= sb.iloc[idx_top:idx_bot]*(1-my_rw/rb)/2
            SW_DW2.iloc[idx_top:idx_bot] = b.iloc[idx_top:idx_bot] +np.power(np.power(b.iloc[idx_top:idx_bot],2)+my_rw/rwa.iloc[idx_top:idx_bot],0.5)   #.clip(0,1)
            SW_DW2.iloc[idx_top:idx_bot]=SW_DW2.iloc[idx_top:idx_bot].clip(0,1)

            # Modified Simandoux
            #---------------------------------------------------
            #Intialized more dfs
            x1.iloc[idx_top:idx_bot] = (POR.iloc[idx_top:idx_bot]**my_m)/(my_a*my_rw*(1-VCL.iloc[idx_top:idx_bot]))
            x2.iloc[idx_top:idx_bot] = VCL.iloc[idx_top:idx_bot]/my_rsh
            x3.iloc[idx_top:idx_bot] = -1/RTD.iloc[idx_top:idx_bot]
            delta.iloc[idx_top:idx_bot] = (x2.iloc[idx_top:idx_bot]**2 - 4*x1.iloc[idx_top:idx_bot]*x3.iloc[idx_top:idx_bot])**(0.5)
            SW_SMOD.iloc[idx_top:idx_bot] = ((-1)*x2.iloc[idx_top:idx_bot] + delta.iloc[idx_top:idx_bot]) / (2*x1.iloc[idx_top:idx_bot])
            SW_SMOD.iloc[idx_top:idx_bot] = SW_SMOD.iloc[idx_top:idx_bot].clip(0,1)

            # Archie saturation
            porpow1.iloc[idx_top:idx_bot]=np.power(POR.iloc[idx_top:idx_bot], my_m)                               #if not Nan
            SW_ARC.iloc[idx_top:idx_bot]=np.power(((my_a*my_rw)/(RTD.iloc[idx_top:idx_bot]*porpow1.iloc[idx_top:idx_bot])),(1/my_n))
            SW_ARC.iloc[idx_top:idx_bot]=SW_ARC.iloc[idx_top:idx_bot].clip(0,1)

            # regular Tixier m=2 n=1.8 a=0.81
            SW_TIX.iloc[idx_top:idx_bot]=0.9/POR.iloc[idx_top:idx_bot]*np.power((1/RTD.iloc[idx_top:idx_bot]-VCL.iloc[idx_top:idx_bot]/my_rsh)*(RWC.iloc[idx_top:idx_bot]/(1-VCL.iloc[idx_top:idx_bot])),0.5)
            SW_TIX.iloc[idx_top:idx_bot]=SW_TIX.iloc[idx_top:idx_bot].clip(0,1)
            mycol +=1 #check next zone

        if mytry==True:
            global_vars.ui.Root.window.iconify()
            #plot results in Dpt_plot for each well with 6 tracks
            #Define top and bottom of plot
            zoneDepths = ZoneDepths(top=las_start, base=las_stop, name="WELL")

            # PHI_FN = c1, PHIE_FN = c2, VCL_FN=c3, SW_SIM = c4, SW_DW2 = c5, SW_TIX = c6, RTD = c7,
            c1=POR
            c1.name='PHI_FN'
            c2=PRE
            c2.name='PHIE_FN'
            c3=VCL
            c3.name='VCL_FN'
            c4=SW_SMOD
            c4.name='SW_SIM_MOD'
            c5=SW_DW2
            c5.name='SW_DW2'
            c6=SW_TIX
            c6.name='SW_TIX'
            c7=SW_ARC
            c7.name='SW_ARC'
            c8=RTD
            c8.name='RT'

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
            cp=[]       #empty list
            #TRACK1   [0,1,0,0,11,1,'','','','','','']
            cp.append([5,1,2,0,11,1,'','','','','',''])
            cp.append([7,2,2,0,11,1,'','','','','',''])
            cp.append([0,1,3,0,11,1,'','','','','',''])
            #TRACK2
            cp.append([5,1,3,0,11,2,'','','','','',''])
            cp.append([2,1,3,0,11,2,'','','','','',''])
            cp.append([7,2,3,0,11,2,'','','','','',''])
            cp.append([8,2,3,0,11,2,'','','','','',''])
            #TRACK3
            cp.append([11,2,9,1,11,3,'','','','','',''])

            curvs=[c1, c2, c3, c4, c5, c6, c7, c8]

            props=[cp[0],cp[1],cp[2],cp[3],cp[4],cp[5],cp[6],cp[7]]
            wellname = las_data.well.uwi.value
            if wellname=='':
                wellname=las_data.well.uwi
            # Dpt_plt(wellname, curvs, fcrvs, props, trcks, pltype=0, Fms)
            depthPlot = DepthPlot()
            depthPlot.depthPlot(wellname, curvs, fcrvs, props, 3, DepthPlot.DepthPlotType.DepthPlot, well.formations, zoneDepths)
            #DepthPlot.newDepthPlot(wellname, curvs, fcrvs, props, 3, 0, fm_list)
            if well == WellList[-1]:    # only ask in final well of trial run
                self.SW_Fn=self.selectFinalCurve(fn_list)
                mytry=False


    #calculate final curve and save    
    if mytry==False:      #SW_Fn only set in trial run as global
        global_vars.ui.Root.window.deiconify()
        if self.SW_Fn is None:
            alert.RaiseException("First select SW_Fn in trial run")
        #update las_df
            
        #select Final Well List and start new WellList loop
        global_vars.project.loadWellListPrompt()
        global_vars.ui.Root.Update()
        WellList=global_vars.project.currentWellList.GetWells() 
        total_wells=len(WellList)
        for well in WellList:
            #Select and save calculated curves


            #load load las from Outdir
            las_data=well.GetLASData(Dir.Out)
            
            if las_data is None:
                alert.Error(ErrorMessage.FAILED_LOAD_LAS, [Dir.Out, well])
                continue

            las_start=las_data.well.STRT.value
            las_stop=las_data.well.STOP.value
            global_vars.las_df=las_data.df()

            lascurves=las_data.curves

            if 'PHI_FN' not in lascurves:
                alert.Error(ErrorMessage.MISSING_POROSITY_CURVE_SKIP, ['PHI_FN', well])
                continue    #Next well
            
            if 'PHIE_FN'not in lascurves:
                alert.Error(ErrorMessage.MISSING_POROSITY_CURVE_SKIP, ['PHIE_FN', well])
                continue    #Next well

            if 'VCL_FN'not in lascurves:
                alert.Error(ErrorMessage.MISSING_POROSITY_CURVE_SKIP, ['VCL_FN', well])
                continue     #Next well

            #Initialization of new logs in default data frame
            #for Watersaturarion CalCulations
            global_vars.las_df['SW_TIX']=np.nan
            global_vars.las_df['SW_ARC']=np.nan
            global_vars.las_df['SW_DW2']=np.nan
            global_vars.las_df['RWC']=np.nan
            global_vars.las_df['SW_SIM_MOD']=np.nan

            #secondary curves default dataframe
            global_vars.las_df['sec']=np.nan 

            fn_list=['SW_SIM_MOD','SW_TIX','SW_ARC','SW_DW2']     #list of answer curves


            POR=global_vars.las_df['PHI_FN'].copy()
            PRE=global_vars.las_df['PHIE_FN'].copy()
            RTD=global_vars.las_df['RT'].copy()
            VCL=global_vars.las_df['VCL_FN'].copy()
            SW_SMOD=global_vars.las_df['SW_SIM_MOD'].copy()
            SW_ARC=global_vars.las_df['SW_ARC'].copy()
            SW_DW2=global_vars.las_df['SW_DW2'].copy()
            SW_TIX=global_vars.las_df['SW_TIX'].copy()
            TMPC=global_vars.las_df['TEMP'].copy()
            RWC=global_vars.las_df['RWC'].copy()

            #secondary curves
            b=global_vars.las_df['sec'].copy()
            rwa=global_vars.las_df['sec'].copy()
            sb=global_vars.las_df['sec'].copy()
            porpow1=global_vars.las_df['sec'].copy()
            x1=global_vars.las_df['sec'].copy()
            x2=global_vars.las_df['sec'].copy()
            x3=global_vars.las_df['sec'].copy()
            delta=global_vars.las_df['sec'].copy()
            #POR.clip(0,1)
            #PRE.clip(0,1)
            RTD.clip(0.1,1000)
            VCL.clip(0,1)

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
                # Watersaturation parameters
                # Now do all calculations using updated params
                Pa=7
                my_a,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('A', zone, old_Ps,Pa)  # A  for Archie. Activity
                my_m,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('M', zone, old_Ps,Pa)  # m  for Archie. Cementation exponent
                my_n,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('N', zone, old_Ps,Pa)  # m  for Archie. Tortuosity/Saturation exponent
                my_rw,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('RW', zone, old_Ps,Pa)  # RW formation water resistivity
                my_phidsh,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('PHIDSH', zone, old_Ps,Pa)  # Density Porosity of shale
                my_rsh,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('RSH', zone, old_Ps,Pa)  # Resistivity of shale
                m_sh,old_Ps=  global_vars.project.formationZoneParameters.CalculateZoneParameters('M_SH', zone, old_Ps,Pa)  # CementationExponent for shale in DW

                #Calculate RW curve = RWC using TEMP (in C) curve
                RWC.iloc[idx_top:idx_bot]=my_rw*(25+21.5)/(TMPC.iloc[idx_top:idx_bot]+21.5)

                
                #'SW_SIM_MOD','SW_TIX','SW_ARC','SW_DW2'
                if self.SW_Fn=='SW_DW2':
                    #SW_DW2
                    #---------------------------------------------------
                    #Clay Bound Water Saturation - CBW
                    sb.iloc[idx_top:idx_bot]=(VCL.iloc[idx_top:idx_bot]*my_phidsh)/POR.iloc[idx_top:idx_bot]
                    porpow1.iloc[idx_top:idx_bot]=np.power(POR.iloc[idx_top:idx_bot], my_m)
                    rwa.iloc[idx_top:idx_bot]=RTD.iloc[idx_top:idx_bot]*porpow1.iloc[idx_top:idx_bot]
                    rb = my_rsh*(my_phidsh**m_sh)

                    # The Bound Water Resistivity
                    b.iloc[idx_top:idx_bot]= sb.iloc[idx_top:idx_bot]*(1-my_rw/rb)/2
                    SW_DW2.iloc[idx_top:idx_bot] = b.iloc[idx_top:idx_bot] +np.power(np.power(b.iloc[idx_top:idx_bot],2)+my_rw/rwa.iloc[idx_top:idx_bot],0.5)   #.clip(0,1)
                    SW_DW2.iloc[idx_top:idx_bot]=SW_DW2.iloc[idx_top:idx_bot].clip(0,1)
        
                elif self.SW_Fn=='SW_SIM_MOD':
                    # Modified Simandoux
                    #---------------------------------------------------
                    #Intialized more dfs
                    x1.iloc[idx_top:idx_bot] = (POR.iloc[idx_top:idx_bot]**my_m)/(my_a*my_rw*(1-VCL.iloc[idx_top:idx_bot]))
                    x2.iloc[idx_top:idx_bot] = VCL.iloc[idx_top:idx_bot]/my_rsh
                    x3.iloc[idx_top:idx_bot] = -1/RTD.iloc[idx_top:idx_bot]
                    delta.iloc[idx_top:idx_bot] = (x2.iloc[idx_top:idx_bot]**2 - 4*x1.iloc[idx_top:idx_bot]*x3.iloc[idx_top:idx_bot])**(0.5)
                    SW_SMOD.iloc[idx_top:idx_bot] = ((-1)*x2.iloc[idx_top:idx_bot] + delta.iloc[idx_top:idx_bot]) / (2*x1.iloc[idx_top:idx_bot])
                    SW_SMOD.iloc[idx_top:idx_bot] = SW_SMOD.iloc[idx_top:idx_bot].clip(0,1)

                elif self.SW_Fn=='SW_ARC':
                    # Archie saturation
                    porpow1.iloc[idx_top:idx_bot]=np.power(POR.iloc[idx_top:idx_bot], my_m)                               #if not Nan
                    SW_ARC.iloc[idx_top:idx_bot]=np.power(((my_a*my_rw)/(RTD.iloc[idx_top:idx_bot]*porpow1.iloc[idx_top:idx_bot])),(1/my_n))
                    SW_ARC.iloc[idx_top:idx_bot]=SW_ARC.iloc[idx_top:idx_bot].clip(0,1)
                
                elif self.SW_Fn=='SW_TIX':
                    # regular Tixier m=2 n=1.8 a=0.81
                    SW_TIX.iloc[idx_top:idx_bot]=0.9/POR.iloc[idx_top:idx_bot]*np.power((1/RTD.iloc[idx_top:idx_bot]-VCL.iloc[idx_top:idx_bot]/my_rsh)*(RWC.iloc[idx_top:idx_bot]/(1-VCL.iloc[idx_top:idx_bot])),0.5)
                    SW_TIX.iloc[idx_top:idx_bot]=SW_TIX.iloc[idx_top:idx_bot].clip(0,1)
                    mycol +=1 #check next zone

                #SWs DONE

            #update las_df
            c=''
            if self.SW_Fn=='SW_DW2':
                c=SW_DW2
            elif self.SW_Fn=='SW_SIM_MOD':
                c=SW_SMOD
            elif self.SW_Fn=='SW_ARC':
                c=SW_ARC
            elif self.SW_Fn=='SW_TIX':
                c=SW_TIX
        
            global_vars.las_df['SW_FN']=c

            filename=well.uwi + ".las"
            
            #cull unused curve in las.
            fn_list.append('SEC','SWC')
            for fn in fn_list:
                if fn in global_vars.las_df:
                    global_vars.las_df.drop(fn,axis=1, inplace=True)
        
            #las_data.set_data(global_vars.las_df)    #update las_data
            las.save_curves(filename, 'SW_FN', self.SW_Fn)                # save curve in las with curvename = SW_Fn
            count +=1

    global_vars.ui.Root.window.deiconify()
    global_vars.ui.Root.c_mylabel.configure(text='Well '+str(count) + ' of ' + total_wells)
    global_vars.ui.Root.window.update_idletasks()

            
    #Done with interpreter calculations    
    alert.Message("Scan")   
    global_vars.project.Scan ()
    alert.Message("Updating Project")
    global_vars.ui.Root.Update()  
    global_vars.ui.Root.window.deiconify()

