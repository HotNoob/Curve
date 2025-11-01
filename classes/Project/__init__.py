import copy
import os
from tkinter import filedialog

import pandas as pd

import defs.alert as alert
import global_vars
from classes.CurveNameTranslator import CurveNameTranslator
from classes.Settings import Settings
from defs import common
from enumerables import Dir
from structs import FormationZone

from .CurveParameter import CurveParameter
from .ProjectWellList import ProjectWellList
from .WellList import WellList
from .FormationZoneParameters import FormationZoneParameters


class Project:

    def __init__(self, file : str, preloadCache : bool = True):
        ''' file is the project file '''



        self.file = os.path.abspath(file) #determine absolute path right away
        self.name = ''
        self.wells = [] # globals.P_wells=[]
        self.curves = [] #globals.P_crvs=[]
        self.formationData = [] #globals.c_fm=[] Formation tops for each well
        self.formationZones : dict[str, FormationZone] = {}  #stratigraphic zones to be analyzed

        self.formationZoneParameters : FormationZoneParameters = None  #Script parameters for
        ''' formation zone specific parameters'''

        self.curveParameters : dict[str, CurveParameter] = {}
        ''' curve specific parameters, [curve name : str, CurveParameter]'''
        
        self.settings : Settings = Settings(self.file)
        ''' project settings '''

        self.requiredSettings = ['InputDir', 'OutputDir', 'rawDir', 'coreDir', 'clientDir']
        self.preloadCache = preloadCache
        self.projectWellList : ProjectWellList = None
        self.currentWellList : WellList = None # new current well list
        self.prevWellList : WellList= None #new pervious well list
        self.curveNameTranslator : CurveNameTranslator = CurveNameTranslator()

        

    #region class methods
    @classmethod
    def newLoadProject(cls, file : str):
        ''' loads a new project, new project is set to global_vars.project '''

        newProject = cls(file=file)
        newProject.Load()
        global_vars.project = newProject

        if global_vars.ui != None:
            global_vars.ui.Root.status.set(global_vars.project.inDir +" "*3 + global_vars.project.outDir+" "*3 + global_vars.project.rawDir+ " "*3 + global_vars.project.coreDir + " "+global_vars.project.clientDir)
            global_vars.ui.Root.Update()

    @classmethod
    def newLoadProjectPrompt(cls) -> None:
        ''' prompts user to open a project file, new project is set to global_vars.project '''
        if global_vars.project.inDir:            # Ensure InputDir has been set
            mpath=global_vars.project.inDir+'/databases/'
        else:
            mpath=global_vars.rootDir

        project_file : str = ''
        try:
            project_file = filedialog.askopenfilename(
                initialdir = mpath,
                title="Please, select a project",
                filetypes=(("Projects", "*.crv"),)
                )
        except ValueError:
            alert.Error('Project could not be opened. Please, try again')
            return
    
        cls.newLoadProject(project_file)
        return
        
    #endregion class methods

    def GetDir(self, dir : Dir) -> str:
        ''' returns project directory based on enum input'''
        match dir:
            case Dir.In:
                return self.inDir
            case Dir.Out:
                return self.outDir
            case Dir.Client:
                return  self.clientDir
            case Dir.Out:
                return self.outDir
            case Dir.Core:
                return self.coreDir
            
    def IdentifyDir(self, path : str) -> Dir:
        ''' attempts to identify the specified path and returns the appropriate enumerable, if not found, will return Dir.Other'''
        path = common.cleanPath(path)

        for dir in Dir.__members__.values():
            if self.GetDir(dir) == path:
                return dir
            
        return Dir.Other

    #region Get/Set Defs
    @property
    def unsavedSettings(self) -> bool:
        ''' determines if settings need to be saved; for in the future a list to determine which settings needs to be saved '''

        return self.settings.unsavedSettings

    #Get dataDir
    @property
    def dataDir(self) -> str:
        '''Get DatabaseDir, this is always in inDir, so readonly'''
        return self.settings.Get('InputDir') + '/databases/'
    

    #Get inDir
    @property
    def inDir(self) -> str:
        return self.settings.Get('InputDir') 

    #Set InDir
    @inDir.setter
    def inDir(self, val : str) -> None:
        self.settings.Set('InputDir', common.cleanPath(val))

    #Get outDir
    @property
    def outDir(self) -> str:
        return self.settings.Get('OutputDir')

    #Set InDir
    @outDir.setter
    def outDir(self, val : str) -> None:
        self.settings.Set('OutputDir', common.cleanPath(val))

    #Get rawDir
    @property
    def rawDir(self) -> str:
        return self.settings.Get('rawDir')

    #Set rawDir
    @rawDir.setter
    def rawDir(self, val : str) -> None:
        self.settings.Set('rawDir', common.cleanPath(val))

    #Get coreDir
    @property
    def coreDir(self) -> str:
        return self.settings.Get('coreDir')

    #Set rawDir
    @coreDir.setter
    def coreDir(self, val : str) -> None:
        self.settings.Set('coreDir', common.cleanPath(val))

    #Get clientDir
    @property
    def clientDir(self) -> str:
        return self.settings.Get('clientDir')

    #Set clientDir
    @clientDir.setter
    def clientDir(self, val : str) -> None:
        self.settings.Set('clientDir', common.cleanPath(val))

    #endregion 

    def Copy(self) -> 'Project':
        return copy.deepcopy(self)

    #region Formation Zone Parameters

    def LoadFormationZoneParameters(self, file : str  = ''):
        ''' if file is empty, loads file based on settings'''

        if file == '':
            file = self.settings.Get('zoneParamFile')
        #self.fmZones=fmZones
        self.formationZoneParameters = FormationZoneParameters(file)
        self.formationZoneParameters.Load()

    #endregion Formation Zone Parameters
    #region CurveNameTranslator

    def PromptLoadCurveNameTranslatorFile(self):
        ''' asks for curve alias file, loads it, and changes project settings to reflect '''
        file = filedialog.askopenfilename(
            initialdir=global_vars.rootDir,
            title="Please, select the Alias file",
            filetype=(("Excel files", "*.xlsx"), ("all files", "*.*")))
        
        if file:
            self.LoadCurveNameTranslator(file)
            self.settings.Set('curveAliasFile', file) #add changes to settings
            
    def LoadCurveNameTranslator(self, file : str = ''):
        ''' if file is empty, loads file based on settings'''
        if file == '':
            file = self.settings.Get('curveAliasFile')

        if not file:
            self.curveNameTranslator.LoadDefaultFile()
        else:
            self.curveNameTranslator.Load(file)

    #endregion CurveNameTranslator
    #region Curve Parameters
    def PromptLoadCurveParameters(self):
        ''' asks for curve parameter file, loads it, and changes project settings to reflect '''
        file = filedialog.askopenfilename(
            initialdir=global_vars.rootDir,
            title="Please, select the Mnemonics file (Curve Parameters File)",
            filetype=(("Excel files", "*.xlsx"), ("all files", "*.*")))
        
        if file:
            self.LoadCurveParameters(file)
            self.settings.Set('curveParameterFile', file) #add changes to settings

    def LoadCurveParameters(self, file : str = ''):
        ''' Load_Mnem / load curve parameters '''
        # open Mnemonic file
        if file == '':
            file = self.settings.Get('curveParameterFile')
            self.curveParameters.clear()
            try:
                df : pd.DataFrame = pd.read_excel(file)
                df.columns = [str(x).strip().lower() for x in df.columns]

                for index, row in df.iterrows():
                    self.curveParameters[row['curve name']] = CurveParameter(
                                                                            curveName   = row['curve name'], 
                                                                            unit        = row['units'],
                                                                            description = row['description'],
                                                                            scale       = row['scale'])

            except FileNotFoundError:
                alert.Error('Mnemonics file could not be found. Please, try again.')
            except ValueError:
                alert.Error('Mnemomics file could not be opened. Please, try again.')
            # except Exception:
                alert.Error('Mnemomics file could not be read. Please, try again.')
        return
    #endregion Curve Parameters

    #region FormationZones
    
    def LoadFormationZones(self, file : str = '') -> bool:
        '''loads formation zone data from strat_col.xlsx by default'''
        
        if file == '':
            file = self.inDir + '/databases/strat_col.xlsx'

        self.formationZones.clear()

        df=pd.read_excel(os.path.abspath(file))
        zoneColumnIndex = df.columns.get_loc('ZONE')
        self.formationZones['DEFAULT'] = None
        for row, zone in df.iloc[:,zoneColumnIndex].items():
                if pd.isna(zone): #check if empty
                    break
                self.formationZones[zone] = FormationZone(Name=zone, 
                                                          TopFormation=str(df['Z_TOP'][row]).upper().strip(),
                                                          BaseFormation=str(df['Z_BASE'][row]).upper().strip(),
                                                          TopOffset=float(df['OFFS_TOP'][row]),
                                                          BaseOffset=float(df['OFFS_BASE'][row]),
                                                          Type=int(df.iloc[row,zoneColumnIndex+5]))
        return True     
    
    def GetFormationZone(self, name : str = '') -> FormationZone:
        ''' a lazy way to get FormationZone without uppercase letters and worry'''
        name = name.strip().upper().replace('_','')

        if(name not in self.formationZones):
            return None

        return self.formationZones[name]
    
    def Get_Zonelist(self,name : str = '') -> FormationZone:     #Get zones list
        zones=[] #empty list
        for name in self.formationZones.items():
            zones.append(name)
        return zones
 

    #endregion FormationZones
    #region WellList
    def resetWellList(self):
        '''resets the currentWellList, puts all project wells in a list, init.wnz'''
        if self.currentWellList is not None: #autosave prev.wnz if list not empty
            self.SaveAs('prev.wnz')

        self.currentWellList = WellList('init.wnz')
        self.currentWellList.LoadFromWells(self.projectWellList.list)

    def loadWellListPrompt(self) -> bool:
        if self.currentWellList is not None: #autosave prev.wnz if list not empty
            self.currentWellList.SaveAs('prev.wnz')

        wellList = WellList.newLoadFromFilePrompt()
        if wellList is not None:
            self.currentWellList = wellList
            return True
        return False

    def loadInitWellList(self) -> bool:
        wellList = WellList.newLoadFromFile('init.wnz')
        if wellList is not None:
            self.currentWellList = wellList
            return True
        return False

    def loadPreviousWellList(self) -> bool:

        wellList = WellList.newLoadFromFile('prev.wnz')
        if self.prevWellList:
            self.prevWellList=wellList #set to current wellList
        if wellList is not None:
            self.currentWellList = wellList
            global_vars.ui.Root.Update()
            return True
        return False
    

    #endregion WellList

    
    def Load(self) -> bool:
        ''' loads project and subcomponents '''
        try:
            self.settings.Load(',') # project files are using , as the delimiter
        except FileNotFoundError:
            alert.Error('{self.file} could not be found. Please, try again.')
            return False
            #c_project()
        except ValueError:
            alert.Error('{self.file} with project settings could not be opened. Please, try again')
            return False    

        #if inDir setting is empty, set default value
        if(self.inDir == ''):
            self.inDir = 'C:/'

        #start preloading cache 
        if self.preloadCache:
            global_vars.LASCache.startPreLoading()

        #check for required settings. we do the check here so no problems later down the road
        for name in self.requiredSettings:
            if self.settings.Get(name) == '':
                alert.Error(f'Project {self.file} is missing {name}')
                return False
        
        if not self.settings.Get('curveParameterFile'): #if not set, use default mnemoics / curve parameter file
            self.settings.Set('curveParameterFile', global_vars.rootDir + '/config/Mnemonics for logs.xlsx') 
            
        #set name. if not in settings will be blank
        self.name = self.settings.Get('name')
            
        self.LoadFormationZones()
        self.LoadFormationZoneParameters()
        self.LoadCurveNameTranslator()
        self.LoadCurveParameters()

        if self.inDir != '':
            #load the project wells
            self.projectWellList = ProjectWellList(self.inDir+'/databases/'+self.name+'.crv.pwl')
            self.projectWellList.Load()
        
        self.currentWellList = WellList('init.wnz')
        self.currentWellList.Load()

        return True
    
    def Close(self):
        ''' close '''
        global_vars.LASCache.Close()

    def Save(self) -> bool:
        '''saves project'''
        self.settings.Save(',')

        if self.projectWellList is not None:
            self.projectWellList.Save()

        self.currentWellList.SaveAs('init.wnz')

        global_vars.LASCache.SaveCacheList()

    def SaveAs(self, file : str) -> 'Project':
        ''' a new file created as well as a new object. as to keep one object to one file'''
        newProject = self.Copy()
        newProject.file = os.path.abspath(file)
        newProject.settings = newProject.settings.SaveAs(newProject.file, ',')
        return newProject

    def SaveInit(self) -> bool:
        '''saves the init / default project file -- also saves project well list and lasdata cache list'''
        print(global_vars.rootDir)
        self.settings.SaveAs(global_vars.rootDir + '/config/init.crv', ',')
        
        if self.projectWellList is not None:
            self.projectWellList.Save()

        global_vars.LASCache.SaveCacheList()

    def Scan(self):
        '''scans the folders / files, reloading and regenerating data where needed '''
        if self.projectWellList is not None:
            self.projectWellList.Scan()