
import os
from classes.JsonObject import JsonObject
import global_vars
from lasio import LASFile

class WellFile(JsonObject):
    filename : str
    fileTime : float
    path : str
    fileExtension : str
    uwi : str
    curves : set

    def __init__(self, file = ''):
        self.file : str = ''
        ''' absolute path / filename '''
        
        self.filename : str = ''
        self.fileTime : float = 0
        self.path : str = ''
        self.fileExtension : str = ''
        self.uwi : str = ''
        self.curves : set = set() #list of curve names within file
        self.temperatureGradiant : float = 0 #we have to use float isntead of np.float64, because json
        if file == '': #for loading from json
            return
        
        #normal loading with file specified
        file = os.path.abspath(file)
        self.file = file
        self.path = os.path.dirname(file)
        self.filename = os.path.basename(file)
        p = os.path.splitext(self.filename)
        self.fileExtension = p[1][1:]
        self.Update()

    def Scan(self) -> bool | None:
        ''' returns True if an update is done, best to catch FileNotFoundError'''
        ''' checks file time if an update is required and then updates '''
        if not os.path.exists(self.file):
            raise FileNotFoundError
        
        if self.fileTime != os.path.getmtime(self.file):
            self.Update()
            return True
        
        return False

    def Update(self):
        ''' updates info from las file, specifically the curves, uwi, and temperatureGradiant '''
        return
        lasHeaders = global_vars.LASCache.GetLASHeaders(self.file)
        self.curves = set(lasHeaders.curvesdict.keys())
        self.uwi = lasHeaders.well.UWI.value #get well number from file

        if 'TMAX' in lasHeaders.params and 'TDD' in lasHeaders.params:    #no TMAX and TDD in kas file skip
            if lasHeaders.params.TMAX.value>0 and lasHeaders.params.TDD.value>0:
                self.temperatureGradiant = (lasHeaders.params.TMAX.value - 6) / lasHeaders.well.STOP.value

        self.fileTime : float = os.path.getmtime(self.file)


    def GetLASData(self) -> 'LASFile':
        return global_vars.LASCache.GetLASData(self.file)
    
    def GetLASHeaders(self) -> 'LASFile':
        return global_vars.LASCache.GetLASHeaders(self.file)