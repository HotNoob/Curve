import math
import numpy as np
import pandas as pd
import global_vars
import os
import inspect as insp

from .Parameter import ZoneParameter


class FormationZoneParameters:
    def __init__(self, file : str = '') -> None:
        ''' file is the file name, self.file holds the last file that was opened / saved, object is locked to filename, 
            if file is empty, assumes default file'''
        
        if file == '':
            file = global_vars.project.inDir + '/databases/Params.xlsx'

        self.__file = os.path.abspath(file)
        self.parametersFile : str = ''
        self.parameters : dict[str, ZoneParameter] = {}
        self.calculatedParameters : dict[str, dict[str, float]] = {}
        ''' [zone, [param, value]]'''

        ''' parameters, most likeyl loaded from param.xlsx'''

    def Load(self):
        '''loads parameters from Params.xlsx by default'''

        self.parameters.clear()
        self.parametersFile = self.__file
        
        df = pd.read_excel(self.__file)
        df.columns = map(lambda s: str(s).strip().upper().replace(' ', '_'), df.columns) #upper case all column names
        if "NAME" in df.columns:
            df.rename(columns={"NAME" : "PARAMS"}, inplace=True)
      
        for index, row in df.iterrows():
            if pd.isna(row['PARAMS']): #if empty
                break; 
            
            name = str(row['PARAMS']).strip().upper()  #set key for paramDict

            #creat parameter dict from df rows
            paramDict = {}
            for col in df:
                #ensure all uppercase for consistency
                cleanCol = str(col).strip().upper()
                paramDict[cleanCol] = row[col]
            
            # Replace ZoneParameter attributes with StratCol attributes
            prvKey=''
            for zone in ZoneParameter.__dataclass_fields__:
                if zone not in 'PARAMS DESCRIPTION':
                    #get correspoding ParamDict name
                    for key, value in paramDict.items():
                            if key not in 'PARAMS, DESCRIPTION': 
                                if key not in prvKey:
                                    if hasattr(ZoneParameter,zone)==True:  
                                        delattr(ZoneParameter,zone)
                                        setattr(ZoneParameter,key,None)
                                    prvKey=prvKey+','+key   #update prvKey
                                    break
            
            self.parameters[name] = ZoneParameter(paramDict)
            #go to ZoneParameters and assign Zone Name??


    def CalculateZoneParameters(self, param, zone, old_Ps, Pa):
        ''' calculates "missing" zone parameters, based on zone type'''
        val=None    #Return value

        # Get zone type list
        #defaultIndex = self.Get('ZONE TYPE')

        #get zone params
        zonetype=getattr(self.parameters['ZONE TYPE'],zone)
        #self.calculatedParameters : dict[str, dict[str, float]] = {}  #Reset default parameter
        val = getattr(self.parameters[param],zone)     # [zone, [param, value : float]]
        if zonetype==0:      #if default zone
            old_Ps.append((param,val, zonetype))              #list of tuples
            return val,old_Ps
        if np.isnan(val)==True:          #If empty then keep old_P
            for index in range(-Pa,1):
                if old_Ps[index][0]==param:
                    val=old_Ps[index][1]
                    break
            return val,old_Ps
        if zonetype>0:     #if not default
            #update old_Ps
            old_Ps.append((param,val, zonetype))
            return val,old_Ps
        '''
            if zonetype!=old_Ps[-1][2]:  #if different zonetype
            # delete previous set of zonetypes
                for index in range(2,-Pa,1):
                    old_Ps.pop()
            elif old_Ps[1][2]!=0:

            pass
        '''
        
        mzones = ZoneParameter.GetZones()   #get zone list
        
        for index,zone in enumerate(mzones):
            #self.calculatedParameters[zone] = {}
            #[param, value : float]

            defaultParams = self.calculatedParameters[zone[index]]
            #global_vars.project.formationZoneParameters.parameters.get('GRSH').__getattribute__(zone)
            for v in self.parameters.values():
                val = v.Get(zone)
                if math.isnan(val):
                    if v.PARAMS in defaultParams:
                        self.calculatedParameters[zone][v.PARAMS] = defaultParams[v.PARAMS]
                    else: #if not set, when should be, revert to "DEFAULT" zone
                        self.calculatedParameters[zone][v.PARAMS] = v.DEFAULT
                else:
                    self.calculatedParameters[zone][v.PARAMS] = val

        return val, old_Ps
        
    def GetCalculatedZoneParameters(self, zone : str):
        ret_par=self.calculatedParameters[zone.strip().upper().replace(' ', '_')]
        return ret_par
    
    def GetZoneParameters(self, zone : str) -> dict[str, float]:
        params : dict[str, float] = []
        for v in self.parameters.values():
            params[v.PARAMS] = v.Get(zone)
            
        return params

    def Zone_list(self) :
        ''' list of zones from combined from param.xls AND strat_col '''
        zones=[]
        
        # get list of mzones Project.Parameter.ZoneParameter
        mzones = ZoneParameter.GetZones()   #get zone list  from strat-col.xls 
        exclude = []

        exclude += ['PARAMS', 'DESCRIPTION','toJson','Get','Set','clear']
        # get list of pzones Project.parameters (param.xls)
        pzones=[]    #Create empty list
        for field in insp.getmembers(self.parameters['ZONE TYPE']):
            # Ignores anything starting with underscore 
            # (that is, private and protected attributes)
            if not field[0].startswith('_'):
            # Ignores methods
                if not insp.ismethod(field[0]):
                    if field[0] not in exclude:
                        pzones.append(field[0])
        
        #compare zone lists
        nzones=[]
        for zone in mzones:
            if zone in pzones:
                nzones.append(zone)
        return nzones

    def Get(self, name : str) -> ZoneParameter:
        ''' a lazy way to get a parameter (param.xlsx) without uppercase letters and worry'''
        name = name.upper()

        if(name not in self.parameters):
            return None

        return self.parameters[name]

    def Set(self, name : str) -> None:
        ''' a lazy way to get a parameter (param.xlsx) without uppercase letters and worry'''

        self.parameters[name.upper()]

    def Save(self):
        if(self.__file == ''):
            raise Exception('file name can not be empty, object is locked to filename to avoid problems')
        
        data = []
        for key, value in self.parameters.items():
            data.append(value.__dict__)

        df = pd.DataFrame(data)
        df.to_excel(self.__file, index=False)

    def  SaveAs(self, file : str):
        ''' a new file created as well as a new object. as to keep one object to one file'''
        newSave = FormationZoneParameters(file)
        newSave.parameters = self.parameters.copy() #create a new copy, not just reference
        newSave.Save()
        return newSave