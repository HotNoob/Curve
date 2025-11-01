'''min_4 for a lack of a better name, for now'''

import os

from typing import TYPE_CHECKING

import numpy as np

import defs.alert as alert
import global_vars

from classes.Plot.DepthPlot import DepthPlot
from structs import ZoneDepths

if TYPE_CHECKING:
    from ...MultiMineral import MultiMineral
    from classes.Project.Well import Well



def min_4(self : 'MultiMineral', mycurve, mytry,idx_top, idx_bot,las_data, well : 'Well'):
    '''
    3 input logs gives 4 minerals
    '''

    #only run if GR NPHI plus RHOB
    if not ('GR' in mycurve or 'GR_NRM'):
        alert.RaiseException('Requires GR or GR_NRM')
    if not ('RHOB' in mycurve or 'RHOB_NRM'):
        alert.RaiseException('Requires RHOB or RHOB_NRM')
    if not ('NPHI' in mycurve or 'NPHI_NRM'):
        alert.RaiseException('Requires NPHI or NPHI_NRM')

    las_start=las_data.well.STRT.value
    las_stop=las_data.well.STOP.value

        # DATA PREPARATION
    #
    # INITIALIZATION OF OUTPUT CURVES USED IN MODEL
    # ---------------------------------------------------------
    self.las_df['VCL_MM']   = np.nan
    self.las_df['VQRZ_MM']  = np.nan
    self.las_df['VLIM_MM']  = np.nan
    self.las_df['VWAT_MM']  = np.nan

    V1 = self.las_df.iloc[idx_top:idx_bot ]['VCL_MM']
    V2 = self.las_df.iloc[idx_top:idx_bot ]['VQRZ_MM']
    V3 = self.las_df.iloc[idx_top:idx_bot ]['VLIM_MM']
    V4 = self.las_df.iloc[idx_top:idx_bot ]['VWAT_MM']

    #INPUT CURVES
    CRV1=self.las_df[mycurve[0]].iloc[idx_top:idx_bot ]
    CRV2=self.las_df[mycurve[1]].iloc[idx_top:idx_bot ]
    CRV3=self.las_df[mycurve[2]].iloc[idx_top:idx_bot ]

    # ---------------------------------------------------------
    #  INITIALIZATION OF CONSTANTS USED IN MODEL
    # ---------------------------------------------------------
    # Now do all calculations
    if self.parameters.index.name!='PAR':
        self.parameters = self.parameters.set_index('PAR')

    # GAMMA RAY or CRV1
    # ------------------------
    G  = CRV1      # Raw curve
    
    G1 = self.getParameter(CRV1,'_CL')        # read parameter from Multi-Mineral spreadsheet starting with GR OF CLAY
    if self.settings.Get('Lithology')=='SS':
        G2 = self.getParameter(CRV1,'_QRZ')       # CRV1 OF QUARTZ
    else:
        G2 = self.getParameter(CRV1,'_DOL')       # CRV1 OF DOLOMITE
    G3 = self.getParameter(CRV1,'_LIM')       # CRV1 OF LIMESTONE
    G4 = self.getParameter(CRV1,'_WAT')       # CRV1 OF FLUIDS

    #  PEF  / CRV2
    # -----------------------
    P  = CRV2      # Raw curve
    P1 = self.getParameter(CRV2,'_CL')        # read parameter from Multi-Mineral spreadsheet starting with GR OF CLAY
    if self.settings.Get('Lithology')=='SS':
        P2 = self.getParameter(CRV2,'_QRZ')       # CRV2 OF QUARTZ
    else:
        P2 = self.getParameter(CRV2,'_DOL')       # CRV2 OF DOLOMITE
    P3 = self.getParameter(CRV2,'_LIM')       # CRV2 OF LIMESTONE
    P4 = self.getParameter(CRV2,'_WAT')       # CRV2 OF FLUIDS

    # RHOB  / CRV3
        # -----------------------
    R  = CRV3   #Raw curve
    R1 = self.getParameter(CRV3,'_CL')        # read parameter from Multi-Mineral spreadsheet
    if self.settings.Get('Lithology')=='SS':
        R2 = self.getParameter(CRV3,'_QRZ')
    else:
        R2 = self.getParameter(CRV3,'_DOL')
    R3 = self.getParameter(CRV3,'_LIM')
    R4 = self.getParameter(CRV3,'_WAT')

    #--------------------------------------------------------------------
    # THE LINEAR EQUATIONS TO BE SOLVED
    #--------------------------------------------------------------------
    # GR   = G1*VCL + G2*VQRZ + G3*VLIM + G4*VWAT
    # PEF  = P1*VCL + P2*VQRZ + P3*VLIM + P4*VWAT
    # RHOB = R1*VCL + R2*VQRZ + R3*VLIM + R4*VWAT
    # 1    =    VCL +    VQRZ +    VLIM      + VWAT
    #-------------------------------------------------------------------

    # MAIN CALCULATION
    A  = G-G4
    A1 = G1-G4
    A2 = G2-G4
    A3 = G3-G4
    A4 = A/A1
    A5 = A2/A1
    A6 = A3/A1

    B  = P-P4
    B1 = P1-P4
    B2 = P2-P4
    B3 = P3-P4
    B4 = B -A4*B1
    B5 = B2-A5*B1
    B6 = B3-A6*B1
    B7 = B4/B5
    B8 = B6/B5

    C = R-R4
    C1 = R1-R4
    C2 = R2-R4
    C3 = R3-R4
    C4 = C -A4*C1
    C5 = C2-A5*C1
    C6 = C3-A6*C1

    # *************************************
    # MINERALS COMPUTATIONS
    #************************************

    # VOLUME OF LIMESTONE
    #-----------------------------
    V3 =(C4-B7*C5)/(C6-B8*C5)               # VOLUME OF LIMESTONE
    self.las_df['VLIM_MM'] = V3
    self.las_df['VLIM_MM'] = self.las_df['VLIM_MM'].clip(0,1)

    # VOLUME OF QUARTZ or DOL
    #-----------------------------
    V2 = B7-B8*V3                          # VOLUME OF QUARTZ
    self.las_df['VQRZ_MM'] = V2
    self.las_df['VQRZ_MM'] = self.las_df['VQRZ_MM'].clip(0,1)

    # VOLUME OF CLAY
    # ------------------------------
    V1 = A4-A5*V2-A6*V3                   # VOLUME OF CLAY
    self.las_df['VCL_MM'] = V1
    self.las_df['VCL_MM'] = self.las_df['VCL_MM'] .clip(0,1)

    # VOLUME OF FLUIDS
    # ---------------------------
    V4 = 1 - self.las_df['VCL_MM'] - self.las_df['VQRZ_MM'] - self.las_df['VLIM_MM']
    self.las_df['VWAT_MM'] = V4
    self.las_df['VWAT_MM'] = self.las_df['VWAT_MM'].clip(0,1)

    self.las_df['PHIT_MM']= self.las_df['VWAT_MM']

    if mytry==True:
        #plot results in Dpt_plot for each well
        #Calculate cumulative curve in new df NOT in las_df

        #Define top and bottom of plot
        zoneDepths = ZoneDepths(top=las_start, base=las_stop, name="WELL")

        wellname = las_data.well.WELL.value

        # cumulative curves
        # do not save those curves. Those are only for depth plot presentation

        c1 = G
        c2 = P
        c3 = R
        c4 = self.las_df['VCL_MM']
        c5 = (c4 + self.las_df['VQRZ_MM']).copy()
        c6 = (c5 + self.las_df['VLIM_MM']).copy()
        c7 = (c6 + self.las_df['PHIT_MM']).copy() #= 100%
        if self.settings.Get('Lithology')=='SS':
            c5.name='VSS_CM'
            c6.name='VCARB_CM'
            c7.name='VPOR_CM'
        else:           #limestone lithology
            c5.name='VDOL_CM'
            c6.name='VLIM_CM'
            c7.name='VPOR_CM'
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
        trcks=3
        cp=[]               #curve property list
        curvs=[c1, c2, c3, c4, c5, c6, c7]
        for c in curvs:
            if c.name == 'GR' or c.name == 'GR_NRM':
                cp.append([0,1,0,0,11,1,'','','','','',''])
            if c.name=='PEF':
                cp.append([11,1,12,0,11,2,'','','','','',''])
            if c.name=='RHOB' or c.name == 'RHOB_NRM':
                if self.settings.Get('Lithology')=='SS':
                    cp.append([2,1,18,0,11,2,'','','','','',''])
                else:
                    cp.append([2,1,4,0,11,2,'','','','','',''])
            if c.name=='DT' or c.name == 'DT_NRM':
                cp.append([0,1,5,0,11,2,'','','','','',''])
            if c.name=='NPHI'or c.name=='NPSS':
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
        props=[cp[0], cp[1], cp[2],cp[3],cp[4],cp[5],cp[6]]

        # Dpt_plt(wellname, curvs, fcrvs, props, trcks, pltype=0, Fms)
        fcrvs=[]
        depthPlot = DepthPlot()
        depthPlot.depthPlot(wellname, curvs, fcrvs, props, trcks, DepthPlot.DepthPlotType.DepthPlot,well.formations,zoneDepths)
        #DepthPlot.newDepthPlot(wellname, curvs, fcrvs, props, trcks, 0, fm_list)

    #Save calculated curves
    if mytry==False:
        las_data.set_data(self.las_df)    #update las_data
        if self.settings.Get('Lithology')=='SS':
            fn_curves=['VCL_MM', 'VSS_MM', 'VCARB_MM','VWAT_MM']
        else:
            fn_curves=['VCL_MM', 'LIM_MM', 'VDOL_MM','VWAT_MM','PHIT_MM']
        #update curve units and descriptions
        for fn in fn_curves:
            for crvs in las_data.curves:
                if fn==crvs.mnemonic:
                    crvs.unit='V/V'
                    crvs.descr=f'{fn} BY EUCALYPTUS CONSULTING INC'

        # save curve in las with curvename = Phie_Fn and/or Phi_Fn
        curDir = os.getcwd()
        os.chdir(global_vars.project.outDir)                #directory for calculated curves
        las_data.write(well.uwi + '.las', fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
        os.chdir(curDir)
    global_vars.ui.Root.window.deiconify()
