import glob
import os
from typing import TYPE_CHECKING

from tkinter import messagebox
import numpy as np
import pandas as pd

import defs.alert as alert
from enumerables import Dir


from defs import program 

if TYPE_CHECKING:
    from .. import Plot
    from classes.CurveNameTranslator import CurveNameTranslator

def findMissingCurves(self : 'Plot'):
    '''
    validation function
    Create CurveNameInSettings dictionary
    Create CurveDirInSettings dictionary

    !!!! TODO -- rewrite and intergrate into PLOT class. required for self.loadOrCreateSettings function
    determine if plt_settings curves are missing
    '''
    
    if self.settings.empty:        # aborted plot settings
            alert.Error('Plot settings NOT defined')
            return

    #Curve names
    curveNameSettings = ['CURVE1', 'CURVE2', 'CURVE3', 'CURVE4', 'ZCURVE']
    curveNamesInSettings : dict[str, str] = {}
    #key is setting name, value is curve name

    #Directories
    DirSettings = ['CURVE1_DIR', 'CURVE2_DIR', 'CURVE3_DIR', 'CURVE4_DIR', 'ZCURVE_DIR']
    DirInSettings : dict[str, str] = {}
    #key is setting name, value is dir 

    #create curvename list
    for name in curveNameSettings:
        val = self.settings.Get(name)
        if val: 
            curveNamesInSettings[name] = val

    #create directory list
    for name in DirSettings:
        val = self.settings.Get(name)
        if val:
            DirInSettings[name] = val
        
    require_cas = False                                 #for non-core curves
    for well in self.wellList.GetWells():               #check Well_List
        dirInFile = well.GetWellFile(Dir.In)
        dirOutFile = well.GetWellFile(Dir.Out)
        coreFile = well.GetWellFile(Dir.In, ".cas")

        for key, value in DirInSettings.items():
            mDir=value
            if Dir.In.name.upper() in mDir :   #Indir    #check DirIN
                cfound=0
                idx=0
                for key, value in curveNamesInSettings.items():
                    aka=CurveNameTranslator.GetName(value)
                    #aliases = global_vars.project.CurveNameTranslator.GetAliases(name)

                    if dirInFile is not None and value in dirInFile.curves:
                        if cfound==idx:
                            cfound=+1  #new curve found
                            idx=0
                            break
                        else:
                            idx=+1 # next curve in DirInFile
                    '''
                    else:  
                        self.wellList.Delete(well)
                        alert.Error(f'well {well.uwi}({well.alias}) does not contain {key}({value}) and has been removed from Well_List')
                        break
                    '''
            if Dir.Out.name.upper() in mDir :    #Outdir
                for key, value in curveNamesInSettings.items():
                    if dirOutFile is not None and value in dirOutFile.curves:
                        break
                    else:  
                        self.wellList.Delete(well)
                        alert.Error(f'well {well.uwi}({well.alias}) does not contain {key}({value}) and has been removed from Well_List')
                        break

        #elif coreFile is not None and value in coreFile.curves and value in global_vars.cdescrvs[:35]: #if part of coredescription
        #require_cas = True
        #break


        #Check if in remaining Well_List coredescriptions are missing
        if require_cas:     #Check if wells have a coredescription
            for well in self.wellList.GetWells():
                #get cas_data and create core_df
                cas_data = well.GetLASHeaders(Dir.In, '.cas')
                
                null=cas_data.well.NULL.value
                core_df=cas_data.df()
                #check is core_df['COREDEPT'] is empty
                c=core_df['COREDEPT'].copy()
                c.replace(null, np.NaN, inplace=True)
                if c.empty== True:              #remove well from list
                    self.wellList.Delete(well)
                    alert.Error(f'well {well.uwi}({well.alias}) does not contain coredept and has been removed from Well_List')
        return

