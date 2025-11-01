
import os
import pandas as pd
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
    #MANNVILLE : float = None
    #U_MANNVILLE : float = None
    #WSEC : float = None
    #SPRK : float = None
    #GP : float = None
    #REX : float = None
    #LDMR : float = None
    #L_MANNVILLE : float = None
    #CMGS : float = None
    #OCDZ : float = None
    #description : str = ''
    
    @classmethod
    def GetZones(cls, exclude : list[str] = None):
        ''' exclude, is a list of zone names to exclude '''
  
        if exclude is None:
            exclude = []

        exclude += ['PARAMS', 'description']

        #add attribute fields
        if global_vars.project.formationZones:
            for mvalue in global_vars.project.formationZones:
                setattr(cls,mvalue,mvalue)

        mzones=[]
        mlen=len(global_vars.project.formationZones)

        cls.__getattribute__()
        for zon in range(mlen):
            if cls.__dataclass_fields__.items() not in exclude:
                mzones.append(zon.name)


        #global_vars.project.formationZones=cls
        
        return mzones

    def Get(self, attribute : str) -> float | str:
        ''' lazy way to get attribute without worrying about case'''
        return getattr(self, attribute.upper().replace(' ', '_'))
    
    def Set(self, attribute : str, value : str | float):
        ''' lazy way to set attribute without worrying about case, todo enforce typing based on typehint'''
        setattr(self, attribute.upper(), value)
