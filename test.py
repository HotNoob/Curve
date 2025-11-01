


import json
from dataclasses import dataclass
import sys
from tkinter import *
from typing import NamedTuple

import matplotlib
import numpy as np
import pandas as pd
import re

import os
from dataclasses import dataclass


def is_vscode_debugging():
    """Check if the script is running from VSCode with debugger attached."""
    vscode_env_vars = ["VSCODE_PID", "VSCODE_IPC_HOOK_CLI", "VSCODE_DEBUGGER"]
    debugging = any(var in os.environ for var in vscode_env_vars)
    if not debugging:
        return sys.gettrace() is not None
    
print(is_vscode_debugging())


quit()

from classes.Project.Parameter import ZoneParameter

zp = ZoneParameter({'MANVILE' : 0, "MANVILE2" : None})

print(zp.MANVILE)
print(zp.MANVILE2)

quit()

if not all((1,2,3,4, '')):
    print('not')
else:
    print('yes')
quit()

rlist : tuple = (1,2,3,4)
print(rlist)
print(rlist)


quit()


languageTranslator : LanguageTranslator = LanguageTranslator('language/english.json')
'''
"FAILED_LOAD_LAS" : "Failed to Load LAS Data File for {uwi}({alias})"
'''

#prints "Failed to Load LAS Data File for testuwi(testalias)" in 3 different ways
obj  = Object()
obj.uwi = 'testuwi'
obj.alias = 'testalias'
obj.dir = Dir.In

print(languageTranslator.GetMessage(ErrorMessage.FAILED_LOAD_LAS, {'dir' : Dir.In, 'well' : obj}))
print(languageTranslator.GetMessage(ErrorMessage.FAILED_LOAD_LAS, obj))

#print(languageTranslator.GetMessage(ErrorMessage.MISSING_FORMATION, ['formationname', obj]))
#print(languageTranslator.GetMessage(ErrorMessage.MISSING_FORMATION, ['formationname', {'uwi' : 'testuwi', 'alias' : 'testalias'}]))
#print(languageTranslator.GetMessage(ErrorMessage.FAILED_LOAD_LAS, obj))
#print(languageTranslator.GetMessage(ErrorMessage.FAILED_LOAD_LAS, {'uwi' : 'testuwi', 'alias' : 'testalias'}))
#print(languageTranslator.GetMessage(ErrorMessage.FAILED_LOAD_LAS, ['testuwi', 'testalias']))

quit()
#global_vars.project.projectWellList.Scan()
#global_vars.project.projectWellList.Save()

#
#wellList.Load()

if False:
    global_vars.project.projectWellList.LoadFolder(global_vars.project.inDir)
    global_vars.project.projectWellList.LoadFolder(global_vars.project.outDir)
    global_vars.project.projectWellList.loadFM()

    #wellList.Save()
    #wellList.Load()
    well = global_vars.project.projectWellList.Get('1B0093604013W400')
    well.alias = 'THE WELL'
    global_vars.project.projectWellList.Save()
    
currentWellList = ['1A0101703801W400', '1B0093604013W400', '1A0072603705W400', '102091605126W400']
mylist = global_vars.project.projectWellList.GetWells(currentWellList)
for well in mylist:
    if well.alias != '':
        print(f"{well.uwi} is {well.alias}")

    zoneDepths = well.GetZoneDepths('WELL')
    if zoneDepths is not None:
        print(f"{well.uwi} -> top depth: {zoneDepths.top}, base depth: {zoneDepths.base}")

    #print(well.curves)

    InDirFile = well.GetWellFile(Dir.In)
    if InDirFile is not None:
        print("InDir Curves")
        #print(InDirFile.curves)

quit()


for file in well.files.values():
    print(file.path + '/' + file.filename)

print("formations")
print(well.formations['START'].name)
print(well.formations['START'].depth)
print(list(well.formations.keys()))
print(global_vars.project.projectWellList.Get('1B0093604013W400').curves)

uwi = '1B0093604013W400'

well = global_vars.project.projectWellList.Get(uwi)

formationZone = global_vars.project.GetFormationZone('MANNVILLE')
topFormation = well.GetFormation(formationZone.TopFormation)
baseFormation = well.GetFormation(formationZone.BaseFormation)

if topFormation is None: #tops not found in well
    alert.Error(f'{formationZone.TopFormation} not in {uwi} - remove from well list')

if baseFormation is None: #tops not found in well
    alert.Error(f'{formationZone.BaseFormation} not in {uwi} - remove from well list')

well = global_vars.project.projectWellList.Get('1B0093604013W400')
zoneDepths = well.GetZoneDepths('MANNVILLE')
if zoneDepths is not None:
    print(f"top depth: {zoneDepths.top}, base depth: {zoneDepths.base}")

print(f"top depth: {topFormation.depth}, base depth: {baseFormation.depth}")

quit()
