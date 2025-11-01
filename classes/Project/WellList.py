'''this class is for managing user created well lists, this is not the project well list which holds all wells in a project'''

from tkinter import filedialog
from typing import TYPE_CHECKING, Type
from classes.Project.ProjectWellList import ProjectWellList

from defs import alert, common
from enumerables import Dir

import global_vars

from .Well import Well

class WellList:
    def __init__(self, file : str = 'init.wnz', wellList : list[str] | ProjectWellList = None):
        ''' file is the file name, self.file holds the last file that was opened / saved '''
        self.__file = file

        self.list : list[str] = []
        '''list that holds the well uwis '''

        if isinstance(wellList, dict | ProjectWellList):
            self.list : list[str] = []
            self.LoadFromWells(wellList)
        elif isinstance(wellList, list):
            self.list : list[str] = wellList

    #region list behaviours
    '''makes pwl behave like dict, instead of calling .list'''
    def __len__(self):
        return len(self.list)
    
    def __iter__(self):
        return iter(self.list)
    
    '''make subscriptable'''
    def __setitem__(self, index, item):
        self.list.__setitem__(index, item)

    def __getitem__(self, index):
        return self.list.__getitem__(index)
    #endregion list behaviours

    def copy(self, file : str = None):
        if file is None:
            file = self.__file

        new = WellList(file)
        new.list = self.list.copy()
        return new

    @classmethod
    def newLoadFromFilePrompt(cls : Type['WellList']) -> 'WellList | None':
        ''' creates a file prompt, asking to load a wnz list. returns None if cancelled'''
        loadFile = filedialog.askopenfilename(
            initialdir=global_vars.project.dataDir,
            defaultextension="*.wnz",
            filetypes=(("Curve well list", "*.wnz"),("UWI files", "*.uwi"),(" text files", "*.txt"))
            )
        if not loadFile:
            return None
        
        wellList = cls(loadFile)
        if wellList.Load():
            return wellList
        else:
            return None

    @classmethod 
    def newLoadFromFile(cls : Type['WellList'], file : str) -> 'WellList | None' :
        wellList = cls(file)
        if wellList.Load():
            return wellList
        else:
            return None

    def Get(self) -> list[str]:
        '''just a function of convenience, returns self.list'''
        return self.list
    
    def GetWell(self, index : int) -> Well:
        return global_vars.project.projectWellList.Get(self.list[index])

    def GetWells(self):
        '''function of convenience, gets Wells from project.projectWellList based on list contents '''
        return global_vars.project.projectWellList.GetWells(self.list)
    
    def GetCommonCurves(self, dir : Dir = None, ext : str = ".las") -> set:
        '''returns a list of all curve names within wells, if dir is none, returns all curves'''

        curvelists : list[list] = []
        if dir == None: #all dirs
            for well in self.GetWells():
                curvelists.append(well.curves)
        else:
            for well in self.GetWells():
                wellFile = well.GetWellFile(dir, ext)
                if wellFile is not None:
                    curvelists.append(wellFile.curves)

        return set().union(*curvelists)

    def GetWellsByCurveAlias(self, curveAlias : str, dir : Dir = Dir.In) -> 'WellList':
        ''' returns a list of wells that contain a curve with the same name, or an alias of that name '''
        newWellList : list[str] = []
        
        curveName = global_vars.project.curveNameTranslator.GetName(curveAlias)
        if(curveName == ''):
            alert.Error(f'{curveAlias} not found in alias list')
            return

        for well in self.GetWells():
            wellFile = well.GetWellFile(dir)
            if wellFile is not None:
                aliasCurves = global_vars.project.curveNameTranslator.GetCurveAliasesInListByName(curveName, wellFile.curves)
                aliases = len(aliasCurves)
                if aliases > 0:
                    newWellList.append(well.uwi)
                if  aliases > 1:
                    alert.Message(f'{well.uwi}({well.alias}) has several {curveName} curves - ' + ', '.join(aliasCurves))

        return WellList(wellList=newWellList)

    def GetWellsByCurveName(self, curveName : str, dir : Dir = Dir.In) -> 'WellList':
        ''' returns a list of wells that contain a curve with the same name '''
        newWellList : list[str] = []

        for well in self.GetWells():        #get wells in current list
            wellFile = well.GetWellFile(dir) #get wells in dir
            if wellFile is not None:
                if curveName in wellFile.curves: #If curveName in outDir WellFile
                    if dir == Dir.In:
                        aliasCurves = global_vars.project.curveNameTranslator.GetCurveAliasesInListByName(curveName, wellFile.curves)
                        aliases = len(aliasCurves)
                        if aliases > 0:
                            newWellList.append(well.uwi)
                        if  aliases > 1:
                            alert.Message(f'{well.uwi}({well.alias}) has several {curveName} curves - ' + ', '.join(aliasCurves))
                    else:
                        newWellList.append(well.uwi) 
        return newWellList

    def Add(self, well : str | Well) -> bool:
        if isinstance(well, Well):
            well = well.uwi

        uwi = common.cleanUWI(well)
        if not uwi: #if is empty
            return False

        if uwi in self.list:
            return False
        
        self.list.append(uwi)
        return True
    
    def Delete(self, uwi : str | Well) -> bool:
        ''' removes and returns True if in list, returns false if not in list'''

        if isinstance(uwi, Well):
            uwi = uwi.uwi

        uwi = common.cleanUWI(uwi)

        if uwi not in self.list:
            return False
        
        self.list.remove(uwi)
        return True

    def Load(self, delimiter : str = " ") -> bool:
        print('load WellList: ' + self.__file)
        self.list = [] #clear

        #load lines from file
        with open(self.__file, "r", encoding=global_vars.fileEncoding) as fileHandler:
            for line in fileHandler:
                lineParts =line.split(delimiter, 1)
                uwi = common.cleanUWI(lineParts[0])
                if uwi: #if not empty add
                    self.list.append(uwi) #ignore the old numbers, this is to be handled by projectwelllist and alias'
                
        if(delimiter == "," and len(self.list) == 0): #if failed to load with "," delimiter, try with " " for max compatability
            return self.Load(' ')

        self.list = list(set(self.list)) #ensure wells in list are unique
        self.list.sort()

        return True #allows for empty well list to load
    
    def LoadFromList(self, wells : list[str]):
        self.list = wells.copy()

    def LoadFromWells(self, wells : list[Well] | dict[str, Well] | ProjectWellList):
        '''
        load well list
        '''
        if isinstance(wells, ProjectWellList):
            wells = wells.list

        if isinstance(wells, dict):
            self.list = [wells[key].uwi for key in wells]
        else:
            self.list = [well.uwi for well in wells]

    def Save(self):
        '''current uses old file definition'''
        print(f'save settings: {self.__file}')

        if(self.__file == ''):
            raise Exception('file name can not be empty, object is locked to filename to avoid problems')

        with open(self.__file,'w', encoding=global_vars.fileEncoding) as f:
            for val in self.list:
                f.write(str(val) + '\n')

        return True

    def SaveAs(self, file : str) -> 'WellList':
        ''' a new file created as well as a new object. as to keep one object to one file'''
        newSave = WellList(file)
        newSave.list = self.list.copy() #create a new copy, not just reference
        newSave.Save()
        return newSave
    
    def SaveAsPrompt(self) -> 'WellList | None':
        ''' creates a file prompt, asking where to save as'''
        newFile = filedialog.asksaveasfilename(
            initialdir=global_vars.project.dataDir,
            defaultextension="*.wnz",
            confirmoverwrite=True,
            filetypes=(("Curve well list", "*.wnz"),("UWI files", "*.uwi"),(" text files", "*.txt"))
            )
        
        if not newFile or not str(newFile).strip():
            return None
        
        return self.SaveAs(newFile)
        