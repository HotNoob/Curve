from enum import Enum

class Dir(Enum):
    In = 0
    Out = 1
    Client = 2
    Core = 3
    Raw = 4
    Other = 7
    @staticmethod
    def FromString(value : str) -> 'Dir':
        '''converts str to DIR, mainly for combo selects and so forth'''
        if isinstance(value, Dir): #check if is already Dir
            return value

        value = value.upper()
        
        match value:
            case 'OTHER':
                return Dir.Other
            case 'IN' | 'INPUT':
                return Dir.In
            case 'OUT' | 'OUTPUT':
                return Dir.Out
            case 'CLIENT':
                return Dir.Client
            case 'CORE' | 'COREDATA':
                return Dir.Core
            case 'RAW':
                return Dir.Raw
            case _:
                raise ValueError('Unknown Dir Value "'+str(value)+'"') 

class Help(Enum):
    Curve = 0
    Graph = 1

class PlotType(Enum):
    Histogram = 'hg'
    CrossPlot = 'xp'
    ZPlot = 'zp'
    ThreeDPlot = '3d'
    PK = 'pk'
    @staticmethod
    def FromString(value : str) -> 'PlotType':
        if(isinstance(value, PlotType)): #check if is already PlotType
            return value
            
        if value == "hg":
            return PlotType.Histogram
        if value == "xp":
            return PlotType.CrossPlot
        if value == "zp":
            return PlotType.ZPlot
        if value == "3d":
            return PlotType.ThreeDPlot
        if value == "pk":
            return PlotType.PK

class MenuMessage(Enum):
    FILE = 'FILE'

class ErrorMessage(Enum):
    ''' 
    holds enumerator for standard error messages, actual error messages are defined in
    language/english.json, english being the active language. 

    comments for enumerator values is to provide parameter hinting

    '''

    FAILED_LOAD_LAS = 'FAILED_LOAD_LAS'

    MISSING_FORMATION = 'MISSING_FORMATION'
    '''[formation, well]'''

    MISSING_FORMATION_ZONE = 'MISSING_FORMATION_ZONE'
    '''[formation zone, well]'''

    MISSING_FORMATION_ZONE_SKIP = 'MISSING_FORMATION_ZONE'
    '''[formation zone, well]'''

    WRONG_FORMATION_TOP = 'WRONG_FORMATION_TOP'
    '''[formation, well]'''

    MISSING_POROSITY_CURVE_SKIP = 'MISSING_POROSITY_CURVE_SKIP'
    '''[curve, well]'''
    
    MISSING_CURVE_SKIP = 'MISSING_CURVE_SKIP'
    '''[curve, well]'''

    MISSING_CURVE_CREATE = 'MISSING_CURVE_CREATE FIRST'
    '''[curve, well]'''