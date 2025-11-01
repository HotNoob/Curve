import copy
import csv
import glob
import json
import os
from datetime import date
from io import StringIO
from typing import TYPE_CHECKING
from zipfile import ZIP_DEFLATED, ZipFile

import global_vars
from defs import alert, main, prompt, common
from enumerables import Dir

from .Well import Well

if TYPE_CHECKING:
    from .. import Settings
    from .FormationInfo import FormationInfo

class ProjectWellList:
    def __init__(self, file : str = ''):
        self.list : dict[str, Well] = {}
        self.__file : str = os.path.abspath(file)
        self.__dir : str = ''        
        self.__wellsAdded = 0 #total number of wells added, mainly for keeping track of temp alias' 

    #region dict behaviours
    '''makes pwl behave like dict, instead of calling .list'''
    def __len__(self):
        return len(self.list)
    
    def __iter__(self):
        return iter(self.list)
    
    '''make subscriptable'''
    #def __setitem__(self, index, item): #dont allow setting this way. readonly
        #self.list.__setitem__(index, item)

    def __getitem__(self, index):
        return self.list.__getitem__(index)
    
    def items(self):
        return self.list.items()
    
    def values(self):
        return self.list.values()
    
    def keys(self):
        return self.list.keys()
    #endregion dict iteration

    #region utils
    def CalculateTemperatureGradiantAverage(self, dir : Dir = Dir.In):
        ''' calculates gradiant average'''
        count = 0
        sum = 0
        for well in self.list.values():
            wellFile = well.GetWellFile(dir)
            if wellFile is not None and wellFile.temperatureGradiant != 0:
                sum += wellFile.temperatureGradiant
                count += 1

        return sum / count
            
    #endregion

    def CheckFiles(self, dir : str = ''):
        ''' checks to see if the files in list exist and so forth'''
        if(dir != ''):
            self.__dir = dir

        return

    def FilterByDir(self, dir : str = '', extension : str = '.LAS') -> list[str]:
        wellNumbers : list[str] = []

        for well in self.list.values():
            if(os.path.exists(well.uwi + extension)):
                wellNumbers.append(well.uwi)

        return wellNumbers

    def LoadFolder(self, dir : str | Dir = Dir.In):
        '''creates a list from the files in a directory, also grabs formation data'''

        if not isinstance(dir, Dir):
            path = dir
            dir = global_vars.project.IdentifyDir(dir)
        else:
            if dir == Dir.Other:
                raise ValueError('dir can not be Dir.Other, please specifiy a string with the path if you want to use Dir.Other')
            
            path = global_vars.project.GetDir(dir)
        

        TemperatureAliases = global_vars.project.curveNameTranslator.GetAliases('TEMP')
        files = glob.glob(path+"/*.las")
        for file in files:
            las_data = global_vars.LASCache.GetLASHeaders(file)

            newWell = Well(file)
            muwi = newWell.uwi

            existingWell = self.Get(muwi)
            if existingWell is not None:
                newWell = existingWell
                newWell.AddWellFile(file)

            mTD = las_data.well.STOP.value
            newWell.AddFormation('START', 'EUC', las_data.well.STRT.value)
            newWell.AddFormation('TD', 'EUC', mTD)

            index=0
            temperatureFound = False
            for crv in las_data.curves:
                if index>0: #is this to exlude DEPT from the list?
                    newWell.curves.add(crv.mnemonic)
                    if not temperatureFound:
                        temperatureFound = (crv.mnemonic in TemperatureAliases)

                index +=1
            #check for BIT.MM and TEMP.C  or aka
            newWell.curves.add('BIT')
            if temperatureFound:
                 newWell.curves.add('TEMP') 

            self.Set(newWell)

        casFiles = glob.glob(path+"/*.cas")
        for file in casFiles:
            las_data = global_vars.LASCache.GetLASHeaders(file)
            uwi = las_data.well.UWI.value
            well = self.Get(uwi)
            if well is not None:
                well.AddWellFile(file)
            else:
                print('WARNING! Cas file found, but no well / .las : ' + file )
        return

    def Scan(self):
        '''scans the folders / files, reloading and updating the data '''
        print('ProjectWellList.Scan()')
        self.LoadFolder(global_vars.project.inDir)
        self.LoadFolder(global_vars.project.outDir)
        self.loadFM()
        return

    def Load(self) :
        print("WellList.Load " + self.__file)
        if not os.path.exists(self.__file): #if does not exist, scan folders / make a new file
            self.Scan()

        else: #load project
            with open(self.__file, "r") as fileHandler:
                for line in fileHandler:
                    line = line.strip()
                    if(line != ''):
                        well = Well.LoadFromString(line)
                        if well is not None:
                            well.ScanWellFiles() #check files for changes
                            self.Set(well)
        return
    
    def loadFM(self) -> None:
        '''
        loads legacy formation data
        '''
        #mpath='C:/Users/ggwas/OneDrive/Visual Studio Workspaces/Visual All-inOne Python code/Curve 3 Tops.TXT'
        mpath= global_vars.project.inDir + '/databases/Curve 3 Tops.TXT'
        try:
            with open(mpath,newline='', encoding=global_vars.fileEncoding) as f:
                reader = csv.reader(f)
                global_vars.project.formationData = list(reader)
            main.stat_update('   Formations Loaded', 4)
        except FileNotFoundError:
            alert.Error('File with FM TOPS could could not be found.')
            yn=prompt.yesno("Create a new Curve 3 Tops.TXT in databases? Y/N")
            if yn==True:    #yes create file
                #Create empty file
                # #change back from RAWdir to Indir to save results
                mpath=global_vars.project.inDir + '/databases/Curve 3 Tops.TXT'
                with open(mpath,'w', encoding=global_vars.fileEncoding) as f:
                    f.write('')
                f.close()

        except ValueError:
            alert.Error('File with FM TOPS could could not be opened. Please, try again')

        for val in global_vars.project.formationData: #load legacy formation data into new data
            well = self.Get(val[0])
            if well is not None:
                well.AddFormation(val[1], val[2], float(val[3]))

        return
        
    def Save(self):
        print("WellList.Save " + self.__file)
        with open(self.__file,'w') as f:
            for well in self.list:
                f.write(self.list[well].toJson()+ '\n')

        self.SaveBackUp()

    def SaveBackUp(self):
        path = os.path.dirname(self.__file)
        path += '/backup/'
        filename = os.path.basename(self.__file) #must not be dir
        if not os.path.exists(path):
            os.mkdir(path)

        memoryStream : StringIO = StringIO()
        for well in self.list:
            memoryStream.write(self.list[well].toJson()+ '\n')

        backupFile = path + filename +'.'+ str(date.today())+ '.backup.zip'
        print("WellList.SaveBackUp " + backupFile)

        with ZipFile(backupFile, 'w',  compression=ZIP_DEFLATED) as myzip:
            myzip.writestr(filename, memoryStream.getvalue())

    def Get(self, uwi : str) -> 'Well | None':
        ''' a lazy way to get wells without uppercase letters and worry'''
        uwi = common.cleanUWI(uwi)

        if(uwi not in self.list):
            return None

        return self.list[uwi]
    
    def GetWells(self, uwis : list[str]) -> 'list[Well]':
        ''' a lazy way to get wells without uppercase letters and worry'''

        wells : 'list[Well]' = []
        for uwi in uwis:
            well = self.Get(uwi)
            if well is not None:
                wells.append(well)

        return wells
    
    def GetByAlias(self, alias : str ) -> Well | None:
        ''' a lazy way to get wells without uppercase letters and worry'''
        alias = common.cleanWellAlias(alias)

        for well in self.list.values():
            if str(well.alias) == alias :
                return well 

        return None
    
    def GetWellsByCurveName(self, curveName : str, dir : Dir = None ) -> 'list[Well]':
        '''returns a list of wells that have a curve with matching name'''
        wells : list[Well] = []
        if dir is None:
            for well in self.list.values():
                if curveName in well.curves:
                    wells.append(well)
        else: 
            for well in self.list.values():
                wellFile = well.GetWellFile(dir)
                if wellFile and curveName in wellFile.curves:
                    wells.append(well)
                    
        return wells
    
    def GetWellsByCurveNames(self, curveNames : list[str], dir : Dir = None ) -> 'list[Well]':
        '''returns a list of wells that have a curve with matching name'''
        wells : list[Well] = []
        if dir is None:
            for well in self.list.values():
                if any(x in curveNames for x in well.curves):
                    wells.append(well)
        else: 
            for well in self.list.values():
                wellFile = well.GetWellFile(dir)
                if wellFile and any(x in curveNames for x in wellFile.curves):
                    wells.append(well)

        return wells

    def Add(self, well : 'Well') -> bool:
        ''' a lazy way to add a well, returns False if the well already exists'''
        name = well.uwi.upper()
        if(name in self.list):
            return False

        self.Set(well)
        return True

    def Set(self, well : 'Well') -> None:
        ''' a lazy way to set a well without uppercase letters'''

        uwi = well.uwi.upper()
        if(uwi not in self.list): ##adding a new well
            if not well.alias or not str(well.alias).strip(): #if alias is empty
                newAlias = len(self.list)+1 #would be more ideal to have a historic count 
                while self.GetByAlias(str(newAlias)): #make sure not already exists. 
                    newAlias += 1

                well.alias = common.cleanWellAlias(str(newAlias))

        self.list[uwi] = well

    def Delete(self, name : str) -> bool:
        ''' a lazy way to delete a well without uppercase letters, returns true if was in list and deleted, false if not found'''
        if(name not in self.list):
            return False

        del self.list[name.upper()]
        return True