from ctypes import Union
import json
import os
import typing

import lasio
import numpy as np

import global_vars
from defs import alert
from enumerables import Dir, ErrorMessage
from structs import ZoneDepths

from .FormationInfo import FormationInfo
from .WellFile import WellFile

from classes.JsonObject import JsonObject

class Well(JsonObject):
    files : dict[str, WellFile]
    alias : str
    note : str
    uwi : str
    curves : set
    formations : dict[str, FormationInfo]

    def __init__(self, file = ''):
        self.files : dict[str, WellFile] = {}
        self.alias : str = ''

        self.note : str = ''

        self.uwi : str = ''
        '''unique well identifier'''

        self.curves : set = set() #set of curve names
        '''list (set - unique list) of curve names that the well has in all well files'''

        self.formations : dict[str, FormationInfo] = {}
        '''dictionary of formations contained in the well'''

        self.T_grad : np.float64 = 0 #is this temperature gradiant?

        #load first file and get wellnumber from the first file. since file names dont always reflect uwi
        if file != '': #this should only be the case when loading from json
            self.AddWellFile(file)
        
        super().__init__()

    #region operations
    # == operator
    def __eq__(self, other):
        ''' checks if other object is referencing to the same object; this should work because all wells are defined in the project well list'''
        return self is other

    #endregion operations

    #region WellFile
    def GetCoreFile(self):
        ''' gets core file, return self.GetWellFile(Dir.In, '.cas') '''
        return self.GetWellFile(Dir.In, '.cas')

    def GetWellFile(self, dir : Dir, ext : str = '.las') -> WellFile | None:
        ''' if ext is empty will grab all files'''

        if ext and ext[0] == '.':
            ext = ext[1:] #remove first . from ext

        folder = global_vars.project.GetDir(dir)

        folder = os.path.abspath(folder)
        for wellFile in self.files.values():
            if wellFile.path == folder and ( ext == '' or wellFile.fileExtension == ext):
                return wellFile
        
        return None

    def AddWellFile(self, file : str):
        newFile = WellFile(file)
        if self.uwi == '': #if wellnumber is empty. set it
            self.uwi = newFile.uwi

        self.files[file] = newFile
        self.curves = self.curves | newFile.curves #update well curve list | is the combine operation for sets

    def ScanWellFiles(self):
        ''' checks well files for changes, and updates cache / object'''
        updated = False
        missing : list[str] = []
        for key,file in self.files.items():
            try:
                if file.Scan():
                    updated = True
            except FileNotFoundError:
                updated = True
                missing.append(key)

        for key in missing:
            del self.files[key]
            
        if updated:
            if self.files:
                self.curves = set.union(*[item.curves for item in self.files.values()])
            else: #files are empty, so set curves to empty
                self.curves = set() 
        
    #endregion WellFile
    #region LAS
    def GetLASData(self, dir : Dir, ext : str = '.las' ) -> lasio.LASFile | None:
        file = self.GetWellFile(dir, ext)
        if file is None:
            return None

        return file.GetLASData()
    
    def GetLASHeaders(self, dir : Dir, ext : str = '.las') -> lasio.LASFile | None:
        file = self.GetWellFile(dir, ext)
        if file is None:
            return None
        
        return file.GetLASHeaders()
    #endregion LAS


    def AddFormation(self, formation : str, euc : str, depth : float):
        self.formations[formation] = FormationInfo(self.uwi, formation, euc, depth)

    def GetFormation(self, name : str) -> FormationInfo:
        ''' a lazy way to get formation from dict'''
        name = name.upper()

        if(name not in self.formations):
            return None

        return self.formations[name]
    
    def GetZoneDepths(self, name : str, silent = False) -> ZoneDepths | None:
        '''silent = False, by default will show error message if top or base formation is missing'''
        formationZone = global_vars.project.GetFormationZone(name)

        if formationZone is None:
            alert.Error(f'formation zone "{name}" is not in valid')
            return None

        topFormation = self.GetFormation(formationZone.TopFormation)
        baseFormation = self.GetFormation(formationZone.BaseFormation)

        if topFormation is None: #tops not found in well
            if not silent:
                alert.Error(ErrorMessage.MISSING_FORMATION, [formationZone.TopFormation, self])
                #alert.Error(f'{formationZone.TopFormation} not in {self.uwi}({self.alias}) - remove from well list')
            return None

        if baseFormation is None: #tops not found in well
            if not silent:
                alert.Error(ErrorMessage.MISSING_FORMATION, [formationZone.BaseFormation, self])
                #alert.Error(f'{formationZone.BaseFormation} not in {self.uwi} - remove from well list')
            return None
        
        #apply offsets and return        
        return ZoneDepths(top=topFormation.depth + formationZone.TopOffset, base=baseFormation.depth + formationZone.BaseOffset, name=name)
    
    @classmethod
    def LoadFromString(cls, data : str) -> typing.Optional[typing.Type['Well']]:
        ''' returns none if fails to load'''


        if data[0] == '{':
            newObj = cls.LoadFromDictionary(json.loads(data))
        else:
            newObj = cls()
            lineParts = data.split(" ", 1)
            if(len(lineParts) == 2):
                newObj.uwi = lineParts[0].upper()
                newObj.alias = lineParts[1].strip() #strip is trim
            else:
                return None
        
        newObj.alias = str(newObj.alias) #has a tendancy to be loaded in as a number instead of str. >.<
        return newObj

    
