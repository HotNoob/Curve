
import threading
import global_vars

class LASConverter:
    #static, because only one conversion at a time
    workerLock : threading.Lock = threading.Lock()
    workerThread : threading.Thread = None

    def __init__(self) -> None:
        self.convertAll : bool = False
        self.convertDescriptions : bool = False
        self.convertNewCurves : bool = False
        self.convertCurveUnits : bool = False
        self.statusMessage : str = ''

    #region constructors
    @classmethod
    def New(cls) -> 'LASConverter':
        ''' creates new LASConverter object and opens a settings menu'''
        newObj = cls()
        newObj.newSettingsMenu()
        return newObj
    #endregion

    def UpdateStatusLabel(self, text : str):
        ''' this is required for accessing ui elements from another thread'''
        global_vars.ui.Root.c_mylabel.configure(text=text)

    from ._defs.las_convert import las_convert
    from ._defs.las_crvdesc import las_crvdesc
    from ._defs.las_newcrvs import Las_NewCrvs
    from ._defs.las_resample import las_resample
    from ._defs.las_resample_optimized import las_resample_optimize_test
    from ._defs.las_serv import convertService
    from ._defs.las_units import las_units
    from ._defs.newSettingsMenu import newSettingsMenu