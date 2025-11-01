'''multimin'''
import os
from typing import TYPE_CHECKING

import numpy as np

import defs.alert as alert
import defs.excel as excel
import defs.las as las
import defs.prompt as prompt
from enumerables import Dir
import global_vars
from classes.Plot.DepthPlot import DepthPlot
from structs import ZoneDepths

if TYPE_CHECKING:
    from .. import MultiMineral

#Multimineral Analysis
def analyze(self : 'MultiMineral'):
    '''
    Execute multimineral analysis from multiple log input
    '''

    global_vars.ui.Root.window.iconify()

    mmessage='Is this a trial run (Yes) or the Final run (No)'
    mytry=prompt.yesno(mmessage)

    fcrvs=[]                  # curves for dpt plt fills

    '''    Default Parameters
    GR_CL           = 150                # GR OF CLAY
    GR_QRZ          = 30                # GR OF QURTZ
    GR_LIM          = 8                 # GR OF LIMESTONE
    GR_DOL          = 11                  # GR OF DOLOMITE
    GR_FELD         = 350                # GR OF FELDSPAR
    GR_WAT          = 0                  # GR OF FLUIDS
    PEF_CL          = 4.01              # PEF OF CLAY
    PEF_QRZ         = 2.75               # PEF OF QUARTZ
    PEF_LIM         = 8.5               # PEF OF LIMESTONE
    PEF_DOL         = 4.5               # PEF OF DOLOMITE
    PEF_FELD        = 3.35               # PEF OF FELDSPAR
    PEF_WAT         = 0.30               # PEF OF FLUIDS
    RHOM_CL         = 2.79               # DENSITY MATRIX OF DRY CLAY
    RHOM_QRZ        = 2.65               # DENSITY MATRIX OF QUARTZ
    RHOM_LIM        = 2.71               # DENSITY MATRIX OF LIMESTONE
    RHOM_DOL        = 2.87               # DENSITY MATRIX OF DOLOMITE
    RHOM_FELD       = 2.57               # DENSITY MATRIX OF FELDSPAR
    RHO_WAT         = 1.0               # DENSITY OF FLUIDS
    NPHI_CL         = 0.37               # NEUTRON MATRIX OF DRY CLAY
    NPHI_QRZ        = -0.035              # NEUTRON MATRIX OF QUARTZ
    NPHI_LIM        = 0.00               # NEUTRON MATRIX OF LIMESTONE
    NPHI_DOL        = 0.03               # NEUTRON MATRIX OF DOLOMITE
    NPHI_FELD       = 0               # NEUTRON MATRIX OF FELDSPAR
    NPHI_WAT        = 1.00               # NEUTRON OF FLUIDS
    DT_CL           = 290                # DT OF DRY CLAY
    DT_QRZ          = 172                # DT OF QUARTZ
    DT_LIM          = 145                # DT OF LIMESTONE
    DT_DOL          = 144                # DT OF DOLOMITE
    DT_FELD         = 150                # DT OF FELDSPAR
    DT_WAT          = 620                # DT OF FLUIDS
    '''
    # load .mlt settings
    zone = self.settings.Get('zone') #get zone from mlt_set (first item)
    for well in global_vars.project.currentWellList.GetWells():
        zoneDepths = None
        #load load las from Outdir
        las_data = well.GetLASData(Dir.Out)
        las_start=las_data.well.STRT.value
        las_stop=las_data.well.STOP.value
        cstep=las_data.well.STEP.value
        
        self.las_df=las_data.df()
        self.las_df.replace(-999.25, np.NaN, inplace=True)

        # determine depth or stratigraphic interval
        #set depth interval
        if zone=='CORE':
            if maxdat>len(global_vars.core_df.index):         # ensure length of plot curves are the same
                idx_bot=idx_bot-(maxdat-len(global_vars.core_df.index))
                maxdat=idx_bot-idx_top

        if zone=='WELL':
            zoneDepths = ZoneDepths(top=las_start, base=las_stop, name=zone )
        
        #Set measured, core or formation depth interval interval
        if zoneDepths is None:                     
            zoneDepths = well.GetZoneDepths(zone)

            if zoneDepths is None:
                alert.RaiseException(f'Zone "{zone}" not in {well.uwi}({well.alias}) - remove from well list')

        #set depth interval
        idx_top=int((zoneDepths.top - las_start)/cstep)
        idx_bot=int((zoneDepths.base - las_start)/cstep)+1  #get very last of array

        # determine analysis type
        mycurve=[]

        for c in range(1,6):
            curveName = self.settings.Get('Curve' + str(c))
            if curveName != 'None' and curveName != '':
                mycurve.append(curveName)

        crv_count = len(mycurve)

        #Select model
        if crv_count==3:
            #4 minerals
            self.min_4(mycurve, mytry,idx_top, idx_bot,las_data, well)

        if crv_count==4:
            #5 minerals
            self.min_5(mycurve, mytry,idx_top, idx_bot,las_data, well)

        if crv_count==5:
            #                   6 MINERALS (min_6)
            #                   DATA PREPARATION
            # INITIALIZATION OF OUTPUT CURVES USED IN MODEL
            # ---------------------------------------------------------
            self.las_df['VCL_MM']   = np.nan
            self.las_df['VQRZ_MM']  = np.nan
            self.las_df['VLIM_MM']  = np.nan
            self.las_df['VDOL_MM']  = np.nan
            self.las_df['VFELD_MM'] = np.nan
            self.las_df['VWAT_MM']  = np.nan

            V1 = self.las_df.iloc[idx_top:idx_bot ]['VCL_MM']
            V2 = self.las_df.iloc[idx_top:idx_bot ]['VQRZ_MM']
            V3 = self.las_df.iloc[idx_top:idx_bot ]['VLIM_MM']
            V4 = self.las_df.iloc[idx_top:idx_bot ]['VDOL_MM']
            V5 = self.las_df.iloc[idx_top:idx_bot ]['VFELD_MM']
            V6 = self.las_df.iloc[idx_top:idx_bot ]['VWAT_MM']

            #input curves
            CRV1=self.las_df[mycurve[0]].iloc[idx_top:idx_bot ]
            CRV2=self.las_df[mycurve[1]].iloc[idx_top:idx_bot ]
            CRV3=self.las_df[mycurve[2]].iloc[idx_top:idx_bot ]
            CRV4=self.las_df[mycurve[3]].iloc[idx_top:idx_bot ]
            CRV5=self.las_df[mycurve[4]].iloc[idx_top:idx_bot ]

            # Now do all calculations
            self.parameters = self.parameters.set_index('PAR')

            # CRV1
            # ------------------------
            G  = CRV1      # Raw curve

            G1 = self.getParameter(CRV1,'_CL')        # read parameter from Multi-Mineral spreadsheet
            G2 = self.getParameter(CRV1,'_QRZ')
            G3 = self.getParameter(CRV1,'_LIM')
            G4 = self.getParameter(CRV1,'_DOL')
            G5 = self.getParameter(CRV1,'_FELD')
            G6 = self.getParameter(CRV1,'_WAT')

            #  CRV2
            # -----------------------
            P  = CRV2   #Raw curve
            P1 = self.getParameter(CRV2,'_CL')        # read parameter from Multi-Mineral spreadsheet
            P2 = self.getParameter(CRV2,'_QRZ')
            P3 = self.getParameter(CRV2,'_LIM')
            P4 = self.getParameter(CRV2,'_DOL')
            P5 = self.getParameter(CRV2,'_FELD')
            P6 = self.getParameter(CRV2,'_WAT')

            # CRV3
            # -----------------------
            R  = CRV3   #Raw curve
            R1 = self.getParameter(CRV3,'_CL')        # read parameter from Multi-Mineral spreadsheet
            R2 = self.getParameter(CRV3,'_QRZ')
            R3 = self.getParameter(CRV3,'_LIM')
            R4 = self.getParameter(CRV3,'_DOL')
            R5 = self.getParameter(CRV3,'_FELD')
            R6 = self.getParameter(CRV3,'_WAT')

            # CRV4
            #----------------------
            N  = CRV4   #Raw curve
            N1 = self.getParameter(CRV4,'_CL')        # read parameter from Multi-Mineral spreadsheet
            N2 = self.getParameter(CRV4,'_QRZ')
            N3 = self.getParameter(CRV4,'_LIM')
            N4 = self.getParameter(CRV4,'_DOL')
            N5 = self.getParameter(CRV4,'_FELD')
            N6 = self.getParameter(CRV4,'_WAT')

            # CRV5
            #---------------------
            T  = CRV5 #Raw curve
            T1 = self.getParameter(CRV5,'_CL')        # read parameter from Multi-Mineral spreadsheet
            T2 = self.getParameter(CRV5,'_QRZ')
            T3 = self.getParameter(CRV5,'_LIM')
            T4 = self.getParameter(CRV5,'_DOL')
            T5 = self.getParameter(CRV5,'_FELD')
            T6 = self.getParameter(CRV5,'_WAT')

            #--------------------------------------------------------------------
            # THE LINEAR EQUATIONS TO BE SOLVED
            #--------------------------------------------------------------------
            # GR   = G1*VCL + G2*VQRZ + G3*VLIM + G4*VDOL + G5*VFELD + G6*VWAT
            # PEF  = P1*VCL + P2*VQRZ + P3*VLIM + P4*VDOL + P5*VFELD + P6*VWAT
            # RHOB = R1*VCL + R2*VQRZ + R3*VLIM + R4*VDOL + R5*VFELD + R6*VWAT
            # NPHI = N1*VCL + N2*VQRZ + N3*VLIM + N4*VDOL + N5*VFELD + N6*VWAT
            # DT   = T1*VCL + T2*VQRZ + T3*VLIM + T4*VDOL + T5*VFELD + T6*VWAT
            # 1    =    VCL +    VQRZ +    VLIM +    VDOL +    VFELD +    VWAT
            #-------------------------------------------------------------------

            # Selected Logs  Calculation
            # ---------------------------------
            #  GR Calculation
            # ---------------------------------

            A  = G - G6
            A1 = G1 - G6
            A2 = G2 - G6
            A3 = G3 - G6
            A4 = G4 - G6
            A5 = G5 - G6

            A6 = A /A1
            A7 = A2/A1
            A8 = A3/A1
            A9 = A4/A1
            A10= A5/A1

            # PEF Calculation
            #--------------------------------
            B  = P - P6
            B1 = P1  - P6
            B2 = P2  - P6
            B3 = P3  - P6
            B4 = P4  - P6
            B5 = P5  - P6

            B6  = B  - A6*B1
            B7  = B2 - A7*B1
            B8  = B3 - A8*B1
            B9  = B4 - A9*B1
            B10 = B5 - A10*B1

            B11 = B6/B7
            B12 = B8/B7
            B13 = B9/B7
            B14 = B10/B7

            # RHOB Calculation
            #-------------------------------
            C  = R  - R6
            C1 = R1 - R6
            C2 = R2 - R6
            C3 = R3 - R6
            C4 = R4 - R6
            C5 = R5 - R6

            C6 = C  -  A6*C1
            C7 = C2 -  A7*C1
            C8 = C3 -  A8*C1
            C9 = C4 -  A9*C1
            C10= C5 - A10*C1

            C11 = C6  - B11*C7
            C12 = C8  - B12*C7
            C13 = C9  - B13*C7
            C14 = C10 - B14*C7

            C15 = C11/C12
            C16 = C13/C12
            C17 = C14/C12

            # NPHI Calculation
            # --------------------------------
            H  = N  - N6
            H1 = N1 - N6
            H2 = N2 - N6
            H3 = N3 - N6
            H4 = N4 - N6
            H5 = N5 - N6

            H6 = H  - A6*H1
            H7 = H2 - A7*H1
            H8 = H3 - A8*H1
            H9 = H4 - A9*H1
            H10= H5 - A10*H1

            H11 = H6 - B11*H7
            H12 = H8 - B12*H7
            H13 = H9 - B13*H7
            H14 = H10- B14*H7

            H15 = H11 - C15*H12
            H16 = H13 - C16*H12
            H17 = H14 - C17*H12

            H18 = H15/H16
            H19 = H17/H16

            # DT Calculation
            # -------------------------------
            D  =  T - T6
            D1 = T1 - T6
            D2 = T2 - T6
            D3 = T3 - T6
            D4 = T4 - T6
            D5 = T5 - T6

            D6 = D  - A6*D1
            D7 = D2 - A7*D1
            D8 = D3 - A8*D1
            D9 = D4 - A9*D1
            D10= D5 - A10*D1

            D11 = D6 - B11*D7
            D12 = D8 - B12*D7
            D13 = D9 - B13*D7
            D14 = D10- B14*D7

            D15 = D11 - C15*D12
            D16 = D13 - C16*D12
            D17 = D14 - C17*D12

            # *************************************
            # MINERALS COMPUTATIONS
            #
            # VOLUME OF FELDSPAR
            #-----------------------------
            V5 = (D15 - H18*D16)/(D17 - H19*D16)
            self.las_df['VFELD_MM'] = V5.clip(0,1)

            # VOLUME OF DOLOMITE
            # ----------------------------
            V4 = H18 - H19*V5
            self.las_df['VDOL_MM'] = V4.clip(0,1)

            # VOLUME OF LIMESTONE
            #-----------------------------
            V3 = C15 - C16*V4 - C17*V5
            self.las_df['VLIM_MM'] = V3.clip(0,1)

            # VOLUME OF QUARTZ
            #-----------------------------
            V2 = B11 - B12*V3 - B13*V4 - B14*V5
            self.las_df['VQRZ_MM'] = V2.clip(0,1)

            # VOLUME OF CLAY
            # ------------------------------
            V1 = A6 - A7*V2 - A8*V3 - A9*V4 - A10*V5
            self.las_df['VCL_MM'] = V1.clip(0,1)

            # VOLUME OF FLUIDS
            # ---------------------------
            V6 = 1 - self.las_df['VCL_MM'] - self.las_df['VQRZ_MM'] - self.las_df['VDOL_MM'] - self.las_df['VLIM_MM'] - self.las_df['VFELD_MM']
            self.las_df['VWAT_MM'] = V6.clip(0,1)

            self.las_df['PHIT_MM']= self.las_df['VWAT_MM']

            if mytry==True:
                #plot results in Dpt_plot for each well
                #Calculate cumulative curve in new df NOT in las_df

                '''
                Defined in depth plot
                color_list=['green', 'palegreen','red','lightcoral','olive','blue','cyan' ,'magenta','purple','gold','lightgrey', 'black', 'darkblue', 'lightblue', 'gray','yellow','orange']
                line_list=['dotted','solid','dashed','dashdot',(0,(3,1,1,1)),(0,(4, 2, 1, 2)),(0,(3,1,1,1,1,1))]
                tick_list=[[0, 50, 100, 150, 200],[0.45, 0.3, 0.15, 0, -0.15],[0.60, 0.45, 0.30, 0.15, 0],[0.0, 0.25, 0.5, 0.75, 1.0],[1.95, 2.2, 2.45, 2.7, 2.95],[500,400,300,200,100],[-0.15,0.15,0.45,0.75,1.05],[1000,750,500,250,0.0],[0.1,1,10,100,1000],[0.2,2,20,200,2000],[0, 0.15, 0.30, 0.45, 0.60],
                [-0.75,-0.50,-0.25,0.0,0.25],[0,5,10,15,20],[300,200,100,0,-100],[150,200,250,350,400],[0,0.5,1,1.5,2],[1000,100,10,1,0.1],[2000,200,20,2,0.2,[1.65, 1.90, 2.15, 2.4, 2.65],[-2,0,2,4,6]]
                scale (0=default or 'lin', 1='log')
                marker_list=['o','O','s','d','D','x','X','h','+','*','^','']

                props[color, linestyle, ticks, scale , marker, track, ---- empty fill parms]
                '''

                wellname = las_data.well.WELL.value
                c1 = G
                c2 = P
                c3 = R
                c4 = N
                c5 = T
                c6 = self.las_df['VCL_MM'].copy()
                c7 = (c6 + self.las_df['VQRZ_MM']).copy()
                c8 = (c7 + self.las_df['VFELD_MM']).copy()
                c9 = (c8 + self.las_df['VLIM_MM']).copy()
                c10 = (c9 + self.las_df['VDOL_MM']).copy()
                c11 = (c10 + self.las_df['PHIT_MM']).copy()

                c7.name='VSS_CM'
                c8.name='VFELD_CM'
                c9.name='VLIM_CM'
                c10.name='VDOL_CM'
                c11.name='VPOR_CM'

                curvs=[c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11 ]

                trcks=3
                cp=[]       #empty list for curve properties

                for c in curvs:
                    if c.name == 'GR' or c.name == 'GR_NRM':
                        cp.append([0,1,0,0,11,1,'','','','','',''])
                    if c.name=='PEF':
                        cp.append([11,1,12,0,11,2,'','','','','',''])
                    if c.name=='RHOB' or c.name == 'RHOB_NRM':
                        if self.settings.Get('Lithology') =='SS':
                            cp.append([2,1,18,0,11,2,'','','','','',''])
                        else:
                            cp.append([2,1,4,0,11,2,'','','','','',''])
                    if c.name=='DT' or c.name == 'DT_NRM':
                        cp.append([0,1,5,0,11,2,'','','','','',''])
                    if c.name=='NPHI' or c.name=='PHIT':
                        cp.append([5,1,2,0,11,2,'','','','','',''])
                    if c.name=='VCL_MM':
                        cp.append([0,1,3,0,11,3,'','','','','',''])
                    if c.name=='VSS_CM':
                        cp.append([11,1,3,0,11,3,'','','','','',''])
                    if c.name=='VFELD_CM':
                        cp.append([5,1,3,0,11,3,'','','','','',''])
                    if c.name=='VLIM_CM':
                        cp.append([3,1,3,0,11,3,'','','','','',''])
                    if c.name=='VDOL_CM':
                        cp.append([8,1,3,0,11,3,'','','','','',''])
                    if c.name=='VCARB_CM':
                        cp.append([8,1,3,0,11,3,'','','','','',''])
                    if c.name=='VPOR_CM':
                        cp.append([2,1,3,0,11,3,'','','','','',''])

                #[color, linestyle, ticks, scale , marker, track --- empty Fill parms]
                props=[cp[0],cp[1],cp[2],cp[3],cp[4],cp[5],cp[6],cp[7],cp[8],cp[9],cp[10]]

                # Dpt_plt(wellname, curvs, fcrvs, props, trcks, pltype=0, Fms)
                depthPlot = DepthPlot()
                depthPlot.depthPlot(wellname, curvs, fcrvs, props, trcks, DepthPlot.DepthPlotType.DepthPlot, well.formations, zoneDepths)
                #DepthPlot.newDepthPlot(wellname, curvs, fcrvs, props, trcks, 0, fm_list)

            #Save calculated curves
            if mytry==False:
                las_data.set_data(self.las_df)    #update las_data
                fn_curves=['VCL_MM', 'VQRZ_MM', 'VLIM_MM','VDOL_MM','VFELD_MM','VWAT_MM','PHIT_MM']
                #update curve units and descriptions
                for fn in fn_curves:
                    for crvs in las_data.curves:
                        if fn==crvs.mnemonic:
                            crvs.unit='V/V'
                            crvs.descr=f'{fn} BY EUCALYPTUS CONSULTING INC'
                filename=well.uwi + '.las'
                # save curve in las with curvename = Phie_Fn and/or Phi_Fn
                curDir = os.getcwd()
                os.chdir(global_vars.project.outDir)                #directory for calculated curves
                las_data.write(filename, fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
                os.chdir(curDir)

    global_vars.ui.Root.window.deiconify()