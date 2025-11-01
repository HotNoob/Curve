'''RIT_SW_scripts'''

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

def RITWaterSaturation(self : 'Script'):
    '''
    Re-iterative Watersaturation calculations for Simandoux and Dual Water

    '''

    global_vars.ui.Root.window.iconify()

    mmessage='Is this a trial run (Yes) or the Final run (No)'
    mytry=prompt.yesno(mmessage)
    if mytry==False:
        if self.SW_Fn is None:
            alert.RaiseException("First select SW_Fn in trial run")
    fcrvs=[]                  # curves for dpt plt fills

    #input curves
    crv_list=[]
    input_list=['PHI_FN','PHIE_FN','VCL_FN','RT','ILM','SFL','TEMP']
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
        #load load las from Outdir
        las_data = well.GetLASData(Dir.Out)
        if las_data is None:
            alert.Error(ErrorMessage.FAILED_LOAD_LAS, [Dir.Out, well])
            continue

        las_start=las_data.well.STRT.value
        las_stop=las_data.well.STOP.value
        global_vars.las_df=las_data.df()

        if 'PHI_FN' not in las_data.curves:
            alert.Error(ErrorMessage.MISSING_POROSITY_CURVE_SKIP, ['PHI_FN', well])
            continue
        if 'PHIE_FN'not in las_data.curves:
            alert.Error(ErrorMessage.MISSING_POROSITY_CURVE_SKIP, ['PHIE_FN', well])
            continue
        if 'VCL_FN'not in las_data.curves:
            alert.Error(ErrorMessage.MISSING_POROSITY_CURVE_SKIP, ['VCL_FN', well])
            continue

        #Initialization of logs

        #for Watersaturarion CalCulations
        global_vars.las_df['SW_DW']=np.nan
        global_vars.las_df['SW_SIM']=np.nan
        global_vars.las_df['RWC']=np.nan
        global_vars.las_df['MEST']=np.nan
        global_vars.las_df['NRT']=np.nan
        global_vars.las_df['NRT_DW']=np.nan
        #secondary curves
        global_vars.las_df['sec']=np.nan

        fn_list=['SW_SIM','SW_DW', 'SW_FN']

        #set depth interval
        cstep=0.1
        idx_top=0
        idx_bot=len(global_vars.las_df)  #get very last of array
        POR=global_vars.las_df.iloc[idx_top:idx_bot]['PHI_FN'].copy()
        PRE=global_vars.las_df.iloc[idx_top:idx_bot]['PHIE_FN'].copy()
        RTD=global_vars.las_df.iloc[idx_top:idx_bot]['RT'].copy()
        NRTD=global_vars.las_df.iloc[idx_top:idx_bot]['NRT'].copy()
        NRT_DW=global_vars.las_df.iloc[idx_top:idx_bot]['NRT_DW'].copy()
        VCL=global_vars.las_df.iloc[idx_top:idx_bot]['VCL_FN'].copy()
        MSW=global_vars.las_df.iloc[idx_top:idx_bot]['SW_SIM'].copy()
        SW_DW=global_vars.las_df.iloc[idx_top:idx_bot]['SW_DW'].copy()
        SW_FN=global_vars.las_df.iloc[idx_top:idx_bot]['SW_FN'].copy()
        TMPC=global_vars.las_df.iloc[idx_top:idx_bot]['TEMP'].copy()
        RWC=global_vars.las_df.iloc[idx_top:idx_bot]['RWC'].copy()

        #secondary curves
        MEST=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        MEST_DW=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        qv=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        porpow=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        mpow=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        swipow=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        swipow1=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        x1=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        x2=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        cti=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        filter1=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        filter2=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        tmpd=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        tmpc=global_vars.las_df.iloc[idx_top:idx_bot]['sec'].copy()
        #POR.clip(0,1)
        #PRE.clip(0,1)
        RTD.clip(0.1,1000)
        VCL.clip(0,1)

        #loop through default and zone types/levels 1-4
        for zone in ZoneParameter.GetZones(exclude=['OCDZ']):
            params = global_vars.project.formationZoneParameters.GetCalculatedZoneParameters(zone)
            cstep=0.1
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
            my_a = params['A']
            my_m = params['M']
            my_n = params['N']
            my_rw = params['RW']
            my_phidsh = params['PHIDSH']
            my_rsh = params['RSH']
            #hlm_a=para_df.iloc[29]['DEFAULT']
            #hlm_m=para_df.iloc[30]['DEFAULT']
            m_sh = params['M_SH']

            #Calculate RW curve = RWC using TEMP (in C) curve
            RWC=my_rw*(25+21.5)/(TMPC+21.5)

            #Re-iterate Simandoux SW and Dual Water  NEEDS MORE TESTING
            myTOL = RTD * 0.1             # An error of 10% in RT is allowed
            myTOL_DW =RTD * 0.1       # An error of 10% in Conductivity is allowed
            #Reiterative loop to find SW with Simandoux and Dual Water
            #if mcol my_n, my_m and my_rw empty skip reiteration
            if not all((my_n, my_m, my_rw, m_sh)):
                continue

            porpow=np.power(POR, my_m)
            qv=VCL*my_phidsh/POR
            x1=porpow.iloc[idx_top:idx_bot]/my_a
            x2=(1000/my_rsh)/pow(my_phidsh,m_sh)
            cw=1000/my_rw
            for mySW in range(120,1,-1):
                mSW=mySW/100           #Convert SW to fractions
                swipow=np.power(mSW,my_n)
                swipow1=np.power(mSW,(my_n-1))
                #DW calc
                cti=x1*(cw*swipow+qv*(x2-cw)*swipow1)
                MEST_DW= 1000/cti
                #Simandoux
                mpow=pow((mSW), my_n)
                MEST = (mpow * porpow) / RWC
                MEST = VCL * mSW / my_rsh + MEST
                MEST = 1 / MEST
                tmpc=RTD-MEST
                tmpd=RTD-MEST_DW
                tmpc=tmpc.abs()
                tmpd=tmpd.abs()
                filter1=tmpc>myTOL
                filter2=tmpd >myTOL_DW
                MSW.where(filter1,mSW,inplace=True)
                NRTD.where(filter1,other=MEST,inplace=True)
                SW_DW.where(filter2,mSW,inplace=True)
                NRT_DW.where(filter2,other=MEST_DW,inplace=True)

        MSW=MSW.clip(0,1)
        SW_DW=SW_DW.clip(0,1)

        if mytry==True:
            #plot results in Dpt_plot for each well with 6 tracks
            #Define top and bottom of plot
            zoneDepths = ZoneDepths(top=las_start, base=las_stop, name="WELL")

            # PHI_FN = c1, PHIE_FN = c2, VCL_FN=c3, SW_SIM = c4, SW_DW = c5, SW_DW2 = c6, RTD = c7, NRTD=c8 , NRTD_DW=c8
            c1=POR
            c1.name='PHI_FN'
            c2=PRE
            c2.name='PHIE_FN'
            c3=VCL
            c3.name='VCL_FN'
            c4=MSW
            c4.name='SW_SIM'
            c5=SW_DW
            c5.name='SW_DW'
            c6=SW_FN
            c6.name='SW_FN'
            c7=NRTD
            c7.name='NRT'
            c8=NRT_DW
            c8.name='NRT_DW'
            c9=RTD
            c9.name='RT'

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
            #TRACK1
            cp.append([5,1,2,0,11,1,'','','','','',''])
            cp.append([7,2,2,0,11,1,'','','','','',''])
            cp.append([4,1,3,0,11,1,'','','','','',''])
            #TRACK2
            cp.append([5,1,3,0,11,2,'','','','','',''])
            cp.append([2,1,3,0,11,2,'','','','','',''])
            cp.append([7,2,3,0,11,2,'','','','','',''])
            #TRACK3
            cp.append([11,2,8,1,11,3,'','','','','',''])
            cp.append([7,2,8,1,11,3,'','','','','',''])
            cp.append([0,2,8,1,11,3,'','','','','',''])

            curvs=[c1, c2, c3, c4, c5, c6, c7, c8, c9]

            #Create a list of FMs and tops to be displayed in DptPlt

            props=[cp[0],cp[1],cp[2],cp[3],cp[4],cp[5],cp[6],cp[7],cp[8]]
            wellname = las_data.well.WELL.value
            # Dpt_plt(wellname, curvs, fcrvs, props, trcks, pltype=0, Fms)
            depthPlot = DepthPlot()
            depthPlot.depthPlot(wellname, curvs, fcrvs, props, 3, DepthPlot.DepthPlotType.DepthPlot, well.formations, zoneDepths)
            #DepthPlot.newDepthPlot(wellname, curvs, fcrvs, props, 3, 0, fm_list)
            if well == global_vars.project.currentWellList[-1]:    # only ask in final well of trial run
                self.SW_Fn=self.selectFinalCurve(well, fn_list)

        #Save calculated final curve
        if mytry==False:      #SW_Fn only set in trial run as global
            if self.SW_Fn is None:
                alert.RaiseException("First select SW_Fn in trial run")

            #update las_df
            if self.SW_Fn=='SW_DW':
                global_vars.las_df['SW_DW']=SW_DW
            if self.SW_Fn=='SW_SIM':
                global_vars.las_df['SW_SIM']=MSW

            las_data.set_data(global_vars.las_df)    #update las_data
            filename=well.uwi + ".las"
            las.save_curves(filename, self.SW_Fn, 'SW_FN')                # save curve in las with curvename = SW_Fn

    global_vars.ui.Root.window.deiconify()