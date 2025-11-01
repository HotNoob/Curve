import os
import traceback

from typing import TYPE_CHECKING


import global_vars
from enumerables import Dir

from . import alert, prompt

if TYPE_CHECKING:
    from classes.Project.Well import Well

def get_lasdata(well : 'Well', dir : Dir):
    '''
     opens a LAS file and returns the lasdata
     opt=0  from Indir
     opt=1  from Outdir
     opt=2  from Clientdir
    '''
    global_vars.perfTest.Start("get_lasdata_total")
    las_data=[]

    if isinstance(dir, int): #convert int to enum, if input was int instead of enum
        dir = Dir(dir)

    curDir = os.getcwd()
    if dir==Dir.In:
        os.chdir(global_vars.project.inDir)
    if dir==Dir.Out:
        os.chdir(global_vars.project.outDir)
    if dir==Dir.Client:
        os.chdir(global_vars.project.clientDir)

    try:
        las_data = well.GetLASData(dir)

        global_vars.perfTest.Stop("get_lasdata_total")
    except FileNotFoundError:
        print(traceback.format_exc())
        alert.Error('LAS file could not be found. Please, try again.')
        os.chdir(curDir)
        return las_data
    except ValueError:
        print(traceback.format_exc())
        alert.Error('LAS file could not be opened. Please, try again.')
        os.chdir(curDir)
        return las_data
    except Exception:
        print(traceback.format_exc())
        alert.Error('LAS file could not be read. Please, try again.')
        os.chdir(curDir)
        return las_data
    os.chdir(curDir)
    return las_data

#===============================================================================================================
def get_lasfile(filename,opt):
    '''
     opens a LAS file and returns the lasdata
     opt 0 = Indir, opt 1 = Outdir, opt 2 = Clientdir
    '''
    las_data=[]

    if len(filename)<21:  #if filename does not include directory
        curDir = os.getcwd()
        if opt==0:   #Indir
            os.chdir(global_vars.project.inDir)
        if opt==1:   #Outdir
            os.chdir(global_vars.project.outDir)
        if opt==2:   #Clientdir
            if global_vars.project.clientDir=="":               # if clientdir not yet set
                prompt.ClientDir()
            os.chdir(global_vars.project.clientDir)
    else:
        curDir = os.getcwd()
    try:
        well = r"{}".format(filename)
        if os.path.exists(well + ".zip"):
            las_data = global_vars.LASCache.GetLASData(well + ".zip")
        else:
            las_data = global_vars.LASCache.GetLASData(well)

    except FileNotFoundError:
        if opt!=1:       #don't show for nwcrnm window
            alert.Error('LAS file could not be found.')
        os.chdir(curDir)
        return las_data
    except ValueError:
        alert.Error('LAS file could not be opened. Please, try again.')
        os.chdir(curDir)
        return las_data
    except Exception:
        alert.Error('LAS file could not be read. Please, try again.')
        os.chdir(curDir)
        return las_data
    os.chdir(curDir)
    return las_data

def save_curves(filename, final_crv : str , fname : str):
    '''
    Save file curves to LAS file.  las_df is global store of all new curves.
    final curve is curve name to be stored as final
    fname = VCL_FN | PHI_FN | PHIE_FN | SW_FN | K_FN | Any curve name.
    .
    
    '''
    #open las file of filename in Outdir using temp_df
    tmp_dat=get_lasfile(filename,1)
    temp_df=global_vars.las_df

    #extract final crv from las_df and determine final curve type: PHIT_FN, VCL_FN etc.

    #update temp_df, curve descriptions and units
    temp_df[final_crv]=global_vars.las_df[final_crv].copy()

    tmp_dat.set_data(temp_df)    #update tmp_data

    for curve in tmp_dat.curves:
        if final_crv == curve.mnemonic:    #if curve already in Lasfile
            curve.descr=f'{fname} BY EUCALYPTUS CONSULTING INC'
            if final_crv=='K_FN':
                curve.unit = 'mD'
            else:
                curve.unit = 'V/V'

        if curve.mnemonic=='SWIRR':
            curve.descr=f'WITH HOLMES CONSTANTS BY EUCALYPTUS CONSULTING INC'
            curve.unit = 'V/V'
            
        
    #write to lasfile in temp_df
    tmp_dat.set_data(temp_df)    #update tmp_data
    save_cas(filename,tmp_dat, Dir.Out)

#-------------------------------------------------------------------------------------------
def save_cas(filename,new_las, dir : Dir = Dir.In):
    '''
    opt=0 save in Indir   opt=1 save in Outdir
    '''

    if dir == Dir.In:
        if (global_vars.project.inDir != global_vars.project.rawDir):
            # check if Indir selected
            if global_vars.project.inDir:
                curDir = os.getcwd()
                os.chdir(global_vars.project.inDir)
                # Now save
                new_las.write(filename, fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
                os.chdir(curDir)
            else:
                alert.Error('No Output Directory selected - select in File menu')
        elif not global_vars.inFile:
            alert.Error('Output must differ from Raw directory - Select in File menu')
    if dir == Dir.Out:
        if global_vars.project.outDir:
            curDir = os.getcwd()
            os.chdir(global_vars.project.outDir)     #directory for calculated curves
            # Now save
            new_las.write(filename, fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
            os.chdir(curDir)
        else:
            alert.Error('No Output Directory selected - select in File menu')