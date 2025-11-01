import os
from tkinter import Listbox
from typing import TYPE_CHECKING

import pandas as pd  # For Excel actions

import classes.LASCache
import classes.PerfTester as PerfTester

from classes.CurveNameTranslator import CurveNameTranslator
from classes.LanguageTranslator import LanguageTranslator


if TYPE_CHECKING:
    from classes.Project import Project
    from classes.Project.Well import Well
    from classes.Settings import Settings
    from classes.UI import UI
    from classes.Login import Login

print('Define Globals')

SoftwareVersion = '3.1.0'
fileEncoding="utf-8" #default file encoding

##this is file location sensitive; globals.py must be in project root or this has to be changed
rootDir = os.path.dirname(os.path.abspath(__file__))
running : bool = False
''' handles main loop; a way to quit'''

perfTest = PerfTester.PerfTester()
ui : 'UI' = None

login : 'Login' = None

inFile = ''
outFile = ''
myDir = ''

myStatusList = []             #Status line in root window

#Petrofacies Criteria list
PF = []                 #initialize PetroFacies list

#Current Well name
currentWell : 'Well' = None

#project.formationData=[] # Formation top database

myDirC=''         # temp directory

cr_shft=[]        #global list for core shift

#Global dataframes  to enable data editing, creation and saving in files
las_df =    pd.DataFrame(None)       #LAS with curve values dpt index and curve columns
core_df =   pd.DataFrame(None)      #Core data dataframe with core description TS analysis and core analysis to be depth shifted against the LAS data frame

curv_df =   pd.DataFrame(None)       #list curves created in scripts and other calculations
out_df =    pd.DataFrame(None)        #general purpose dataframe to transfer data between functions (such as copy)
in_df = pd.DataFrame(None)        #general purpose dataframe to transfer data between functions (such as copy)

# multipurpose global list
tmp=[]              # create empty list
mflag=1             # temp global flag

### other globals

w_names = None

my_anns = None

facies = None

missingCurveList = None

fc_fn = None

func_id = None

x_df = None

CalcCurveNames : tuple[str] = (
                                        'BIT','TEMP','GR_NRM','DT_NRM','NPSS_NRM','NPHI_NRM','DPSS_NRM','RHOB_NRM','GR','DT','RHOB','NPSS','NPHI','PEF','DRHO','RT','ILM','SFL','SP','CALI','CALY',
                                        'DTS','IGR','VCL_LIN','VCL_CLV','VCL_TRT','VCL_OLD','VCL_STB_I',
                                        'VCL_STB_II','VCL_STB_MP','VCL_ND','VCL_NEU', 'VCL_TS','VCL_FN','PHI_FN', 'PHIE_FN','SW_FN','K_FN'
                                    )
''' read only'''


cdescrvs : tuple[str] = (
                            'DEPT', 'COREDEPT','SAMPLE','FACIES',
                            'LITHOLOGY','ACCESSORIES','SEDSTRUCT',
                            'GRAIN_MM','GRAIN_PHI','BIODEGR',
                            'VISPOR','ORGPOR','TOC','SID','PYR','CARB',
                            'SHCLST','SH-RCK','SHDISP','SHTOT','VSLT',
                            'RNDG','SORT','SLT_SRT',
                            'POR','+CARB','+VCLAY','BRITL','CPHIT','CSW',
                            'MAVCL','MAPHIT','MA1','MA2','MA3',
                            # Core Analysis Curves
                            'CORNO','S_TP','S_TCK','KMAX','KVRT','K90',
                            'CPOR','GDEN','BDEN','RSO','RSW'
                        )        #defined core curve names
''' read only '''


c_units : tuple[str] = (
                            'M', 'M','no','code',
                            'code','code','code',
                            'mu','phi','code',
                            'PU','PU','PU','PU','PU','PU',
                            'PU','PCNT','PU','PU','PU',
                            'code','code','code',
                            'PU','PU','+PU','VAL','PU','PU',
                            'PU','PU','','','',
                            # Core Analysis Curves
                            'code','M','M','mD','mD','mD',
                            'V/V','g/cm3','g/cm3','V/V','V/V','code'
                        )
''' read only '''

c_descr : tuple[str] = (
                            'MEASURED CORE DEPTH','CORE# DISTANCE FROM TOP','SAMPLE OR THIN SECTION ID','FACIES TYPE',
                            'LITHOLOGY TYPE','ACCESSORIES','SEDIMENTARY STRUCTURES OBSERVED',
                            'GRAIN SIZE IN MICRONS','GRAIN SIZE ON PHI_SCALE','INTENSITY OF BIOTURBATION',
                            'VISUAL POROSITY UNDER CUTTINGS MICROSCOPE','ORGANIC VISUAL POROSIY','ESTIMATED ORGANIC CONTENT',
                            'SIDERITE CEMENT','PYRITE CEMENT','CARBONATE CEMENT CALCITE AND/OR DOLOMITE',
                            'SHALE CLAST IN SS FRAMEWORK','SHALE - ROCK RATIO','DISPERSED SHALE IN SS FRAMEWORK',
                            'TOTAL SHALE VOLUME','TOTAL SILY OR SAND CONTENT',
                            'ROUNDING OF SS GRAINS','SORTING  OF SS GRAINS','SORTING OF SILT SIZED GRAINS IN SS',
                            'TOTAL POROSITY','ADD CARBONATE CONTENT','ADD CLAY VOLUME (NOT SHALE)','BRITTLENESS CALCULAYED BASED ON MINERALOGY CONTENT',
                            'TOTAL POROSITY IN CORE','TOTAL WATER SATURATION ESTIMATED IN CORE',
                            'VCl 5 STEP MOVING AVERAGE','PHIT 5 STEP MOVING AVERAGE',
                            'UNDESIGNATED 5 STEP MOVING AVERAGE','UNDESIGNATED 5 STEP MOVING AVERAGE',
                            'UNDESIGNATED 5 STEP MOVING AVERAGE',
                            # Core Analysis Curves
                            'CORE NUMBER','SAMPLE TOP','SAMPLE THICKNESS','MAXIMUM HORIZONTAL PERMEABILITY TO AIR',
                            'VERTICAL PERMEABILITY TO AIR','PERMEABILITY TO AIR AT 90 DEGREES TO KMAX',
                            'CORE POROSITY','GRAIN DENSITY','BULK DENSITY','RESIDUAL OIL SATURATION',
                            'RESIDUAL WATER SATURATION','PLUG NUMBER'
                        )
''' read only '''

my_status = None
current_stat = None

#==========================================================================================================
# Set default directories
inFile = ''
outFile = ''
#project.settings.Get('inDir') = 'c:/'
#project.settings.Get('outDir') = ''
#project.settings.Get('rawDir')=''
#project.settings.Get('coreDir')=''
#project.settings.Get('clientDir')=''
myDir=''
myStatList = [" "," "," ","","",""]  # initialize status list

#las data cache
#las_data
#file name
#file time

languageTranslator : LanguageTranslator = LanguageTranslator(rootDir + '/language/english.json')

LASCache = classes.LASCache.LASCache()

project : 'Project' = None


#new
color_list = []
line_list = []
line_style = []
tick_list = []
mtick_list = []
scale_list = []
marker_list = []
marker_style = []
gticks = []

