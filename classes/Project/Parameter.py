
import os
import pandas as pd
import inspect as insp
import global_vars

from global_vars import project

from dataclasses import dataclass

from classes.JsonObject import JsonObject


@dataclass
class ZoneParameter(JsonObject):
    def __init__ (self, zones : [str,float]):
        for key, value in zones.items():
            self.__setattr__(key, value)


    ''' formation zone specific parameters '''
    PARAMS : str = ''
    ''' parameter name, is called PARAMS for compatabiliy. can rename later'''

    #the order of these parameters MUST match the order in the spreadsheet for index sensitive zone function
    DEFAULT : float = None
    DESCRIPTION : str = ''
    ZONE01 : float = None
    ZONE02 : float = None
    ZONE03 : float = None
    ZONE04 : float = None
    ZONE05 : float = None
    ZONE06 : float = None
    ZONE07 : float = None
    ZONE08 : float = None
    ZONE09 : float = None
    ZONE10 : float = None
    ZONE11 : float = None
    ZONE12 : float = None

    
    @classmethod
    def GetZones(cls, exclude : list[str] = None):
        ''' exclude, is a list of zone names to exclude using formationZones (param.xls) '''       
        if exclude is None:
            exclude = []

        exclude += ['PARAMS', 'DESCRIPTION','toJson','Get','Set']
        '''
        #add attribute fields
        if global_vars.project.formationZones:
                for mvalue in global_vars.project.formationZones:
                        setattr(m_cls,mvalue,None)
        '''
        zones=[]    #Create empty list get zones in correct order 
        for zone in global_vars.project.formationZones.items():
            zones.append(zone[0])

        '''
        # get list of zones Project.Parameter.ZoneParameter in cls
        zones=[]    #Create empty list
        #clen=cls.__dataclass_fields__.__sizeof__
        for field in insp.getmembers(cls):
            # Ignores anything starting with underscore 
            # (that is, private and protected attributes)
            if not field[0].startswith('_'):
            # Ignores methods
                if not insp.ismethod(field[1]):
                    if field[0] not in exclude:
                        zones.append(field[0])
        '''
        return zones

    def Get(self, attribute : str) -> float | str:
        ''' lazy way to get attribute without worrying about case'''
        return getattr(self, attribute.upper().replace(' ', '_'))
    
    def Set(self, attribute : str, value : str | float):
        ''' lazy way to set attribute without worrying about case, todo enforce typing based on typehint'''
        setattr(self, attribute.upper(), value)

