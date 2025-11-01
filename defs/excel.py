import os
import traceback

import pandas as pd  # For Excel actions

import global_vars

from . import alert


#-------------------------------------------------------------------------------------------------------------------------------------------
def get_zone():

    mpath='databases/strat_col.xlsx'
    if not os.path.exists(mpath):
        mpath='config/Strat_col.xlsx'  #try default location
        
    try:
        get_exceldata(mpath)
    except Exception:
        print(traceback.format_exc())
        return    # error already reported - I hope

def loadExcelDataFrame(filename :  str) -> pd.DataFrame:
    '''loads excel file and returns dataframe. alerts errors. returns pandas.DataFrame(None) if fails'''
    df = pd.DataFrame(None)   #create or clear df
    try:
        df=pd.read_excel(os.path.abspath(filename))
    except FileNotFoundError:
        alert.Error(f'{filename} not found. Please, try again.')
    except ValueError:
        alert.Error('File could not be opened. Please, try again')
    except PermissionError:
        alert.Error('File already opened by another program. Please, try again')

    return df

def saveExcelDataFrame(filename : str, dataFrame : pd.DataFrame, index : bool = False) -> bool:
    try:
        dataFrame.to_excel(filename,index=index)
    except ValueError:
        return alert.Error('File could not be opened. Please, try again')
    except PermissionError:
        return alert.Error('File already opened by another program. Please, try again')
    return True    

#===============================================================================================================
def get_exceldata(mpath : str) -> pd.DataFrame:
    '''
     opens and reads excel files and loads into global variable, zone_df, core_df, para_df (param), and para_df ( petrofac )
    '''
    #allow zone_df to beloaded
    #allow core_df to beloaded
    #allow para_df to beloaded

    curDir = os.getcwd()
    os.chdir(global_vars.project.inDir)

    df = pd.DataFrame(None)   #create or clear df
    try:
        filename= r"{}".format(mpath)
        if mpath[:len(global_vars.project.coreDir)]==global_vars.project.coreDir:   #If core data load
            global_vars.core_df=pd.read_excel(os.path.abspath(filename))
        elif mpath=='databases/PETROFAC.xlsx':
            df=pd.read_excel(os.path.abspath(filename))
        else:
            df=pd.read_excel(os.path.abspath(filename))

    except FileNotFoundError:
        print(traceback.format_exc())
        alert.Error(f'{filename} not found. Please, try again.')
        return
    except ValueError:
        print(traceback.format_exc())
        alert.Error('File could not be opened. Please, try again')
        return
    except PermissionError:
        print(traceback.format_exc())
        alert.Error('File already opened by another program. Please, try again')
        return

    os.chdir(curDir)
    return df

#===============================================================================================================
def save_exceldata(mpath):
    '''
     opens and reads excel files
    '''
    #globals.zone_df          #allow zone_df to beloaded

    curDir = os.getcwd()
    os.chdir(global_vars.project.inDir)

    try:
        filename= r"{}".format(mpath)
        if mpath=='databases/MLT_values.xlsx':
            global_vars.x_df.to_excel(filename,index=False)

    except FileNotFoundError:
        alert.Error('File could not be found. Please, try again.')
        return
    except ValueError:
        alert.Error('File could not be opened. Please, try again')
        return
    except PermissionError:
        alert.Error('File already opened by another program. Please, try again')
        return

    os.chdir(curDir)