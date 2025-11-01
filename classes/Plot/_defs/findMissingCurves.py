import glob
import os
import global_vars
from typing import TYPE_CHECKING

from tkinter import messagebox
import numpy as np
import pandas as pd
#import CurveNameTranslator as al

import defs.alert as alert
from enumerables import Dir


from defs import program 

if TYPE_CHECKING:
    from .. import Plot
    

def findMissingCurves(self : 'Plot'):
    '''
    validation function
    Create CurveNameInSettings dictionary
    Create CurveDirInSettings dictionary

    Update graphics well list

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

    #create curvename list
    for name in curveNameSettings:
        val = self.settings.Get(name)
        if val: 
            curveNamesInSettings[name] = val
        
    require_cas = False
    for well in self.wellList.GetWells():               #check Well_List
        dirInFile = well.GetWellFile(Dir.In)            #Get w
        dirOutFile = well.GetWellFile(Dir.Out)
        coreFile = well.GetWellFile(Dir.In, ".cas")
        found=0
        for key, value in curveNamesInSettings.items():
            if dirInFile is not None:
                #name = global_vars.project.curveNameTranslator.GetName(value)
                #get akas for value (alias)
                akas = global_vars.project.curveNameTranslator.GetAliases(value)
                for aka in akas:
                    if aka in dirInFile.curves:
                        found +=1
                        break
            if value in coreFile.curves: #if part of coredescription
                    require_cas = True
                    found+=1
                    #break
            if dirOutFile is not None and value in dirOutFile.curves:
                    found+=1
                    #break
        if found!=len(curveNamesInSettings):        #if not all curves found
            self.wellList.Delete(well)
            alert.Error(f'well {well.uwi}({well.alias}) does not contain {key}({value}) and has been removed from Well_List')
            continue

        #Check if in remaining Well_List coredescriptions are missing
        if require_cas:     #Check if wells have a coredescription
            for well in self.wellList.GetWells():
                #get cas_data and create core_df
                cas_data = well.GetLASHeaders(Dir.In, '.cas')
                try:
                    null=cas_data.well.NULL.value
                except Exception:
                    self.wellList.Delete(well)
                    alert.Error(f'well {well.uwi}({well.alias}) does not contain null value and has been removed from Well_List')
                    continue
                core_df=cas_data.df()
                #check is core_df['COREDEPT'] is empty
                c=core_df['COREDEPT'].copy()
                c.replace(null, np.NaN, inplace=True)
                if c.empty== True:              #remove well from list
                    self.wellList.Delete(well)
                    alert.Error(f'well {well.uwi}({well.alias}) does not contain coredept and has been removed from Well_List')

        global_vars.ui.Graphing.SetWellList(self.wellList)
        return
