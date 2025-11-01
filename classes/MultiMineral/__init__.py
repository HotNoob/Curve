# pylint: disable = import-outside-toplevel
import global_vars
import pandas as pd
import defs.excel as excel

from classes.Settings import Settings
from classes.ExcelFile import ExcelFile


class MultiMineral(object):
    def __init__(self):
        self.settings : Settings = None
        self.parameters : pd.DataFrame = pd.DataFrame(None) # multimineral values
        self.defaltParameters : pd.DataFrame = pd.DataFrame(None)
        self.las_df : pd.DataFrame = pd.DataFrame(None)

    from ._defs.analyze import analyze
    from ._defs.getParameter import getParameter
    from ._defs.newParametersMenu import newParametersMenu
    from ._defs.newSettingsMenu import newSettingsMenu

    from ._defs.min_4 import min_4
    from ._defs.min_5 import min_5

    #constructors
    from ._defs._constructors import newAnalysis

    def LoadParameters(self : 'MultiMineral', file : str) -> bool:
        
        self.defaltParameters= excel.loadExcelDataFrame(file)
        if self.defaltParameters.empty:
            return False
        
        return True

    def LoadDefaultParameters(self : 'MultiMineral') -> bool:
        '''mlt_load'''
        return self.LoadParameters(global_vars.project.inDir + '/databases/MLT_values.xlsx')

    def SaveParameters(self : 'MultiMineral', file : str) -> bool:
        return excel.saveExcelDataFrame(file, self.parameters)
        
    def SaveDefaultParameters(self : 'MultiMineral'):
        self.SaveParameters(global_vars.project.inDir + '/databases/MLT_values.xlsx')
        

    def LoadDefaultSettings(self : 'MultiMineral'):
        self.LoadSettings(global_vars.project.inDir+'/databases/default.mlt')

    def LoadSettings(self : 'MultiMineral', file : str):
        self.settings = Settings(file)
        self.settings.Load()
        #todo, validate settings. see def find_missing_curves(plt_settings):

    def SaveDefaultSettings(self : 'MultiMineral'):
        self.settings.SaveAs(global_vars.project.inDir+'/databases/default.mlt')