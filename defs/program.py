
import csv
import glob
import os

import numpy as np
from classes.Project.Well import Well
from enumerables import Dir

import global_vars
from defs import alert, prompt


# ----------------------------------------------------------------------------------------------------------
def get_crvlist(crv_no):
    '''
    Create an alias or curve list
    crv_no = curve number (1 to 3) or
    crv_no = '4 or Z-curve'
    crv_no = 5 - pickett plot
    '''
    if crv_no==5:
        myyesno=0
    else:
        myyesno=prompt.customYesNoPrompt(f'Use Input or Output directory for Curve {crv_no}', 'Input', 'Output')

    if myyesno==1:                   # INDIR
        global_vars.myDirC=global_vars.project.inDir
        crv_list=[]
        no_crvs=['DEPT']
        crv_list=com_crvs(no_crvs,crv_list,1)

        # add cas file curves that wells in WELL_LIST have in common
        crv_list=comm_core(crv_list)
    else:                   #OUTDIR
        global_vars.myDirC=global_vars.project.outDir
        #create list of common curves
        crv_list=[]
        if crv_no==5:
            no_crvs=['DEPT','BIT','TEMP','GR_NRM','DT_NRM','NPSS_NRM','NPHI_NRM','DPSS_NRM','RHOB_NRM','GR','DT','RHOB','NPSS','NPHI','PEF','DRHO','ILM','SFL','SP','CALI','CALY',
            'DTS','IGR','VCL_LIN','VCL_CLV','VCL_TRT','VCL_OLD','VCL_STB_I',
            'VCL_STB_II','VCL_STB_MP','VCL_ND','VCL_NEU', 'VCL_TS', 'PHIE_FN','K_FN']
        else:
            no_crvs=['DEPT']
        crv_list=com_crvs(no_crvs,crv_list,0)

    return crv_list
#-------------------------------------------------------------------------------------------------------
def com_crvs(no_crvs,crv_list,opt):
    '''
    no_crvs is list of curves to be excluded
    create a list of common curve in Lasfiles of
        option = 0 OUTDIR
        option = 1 INDIR
        option = 2 CLIENTDIR
        option = 3 OUTDIR added to existing curvelist
    '''

    global_vars.missingCurveList=[]     #initilize list of curvs in well list not in Alias_arr

    mopt=0
    if opt==3: #add current list to new well list
        crv_list.append('OUTDIR CURVES')
        old_list=crv_list.copy()
        crv_list=[]         #clear crv_list for Outdir
        mopt=3
        opt=0
    else: old_list=[]

    curDir = os.getcwd()
    lasDir = curDir
    if opt==0:                  #outdir
        lasDir = global_vars.project.outDir
        os.chdir(lasDir)
        las_list = glob.glob("*.las")
        if len(las_list)==0:            #empty outDir
            crv_list=old_list[:-1]
            os.chdir(curDir)
            return crv_list
    if opt==1:
        lasDir = global_vars.project.inDir                #indir
        os.chdir(lasDir)
        loadCL()
    if opt==2:
        lasDir = global_vars.project.clientDir
        os.chdir(lasDir)     #clientdir
    count=0
    my_list=[]
    for well in global_vars.project.currentWellList.GetWells():
        #load load las from Clientdir Outdir or indir
        if opt!=1:
            # check if well is in Outdir
            tst_lst=glob.glob('*.las')
            if well.uwi+'.las' not in tst_lst:
                return old_list[:-1]
            las_data = global_vars.LASCache.GetLASHeaders(lasDir + '/' + well.uwi+'.las') #nopt is not needed, lasDir instead.

            if len(las_data.curves)==0:            #not found
                if old_list[-1]=='OUTDIR CURVES':
                    old_list.pop(-1)
                crv_list=old_list[:]
                os.chdir(curDir)
                return crv_list
        if count==0:     #first well curve.mnemonic
            if opt==1:          #If Indir
                crv_list=pcrv_aka(well)       #Curvelist for Indir Las in current well
            else:
                for crv in las_data.curves:
                    if crv.mnemonic not in no_crvs:
                        crv_list.append(crv.mnemonic)
        else:
            if opt==1: #If Indir
                my_list=pcrv_aka(well)       #Curvelist for Indir Las in current well
            else:
                for mcrv in las_data.curves:
                    if mcrv.mnemonic not in no_crvs:
                        my_list.append(mcrv.mnemonic)   #Curvelist for Outdir or Client Dir Las in current well


            for i in reversed(range(len(crv_list))): #cycle through the crv_lst and if not in my_list delete, loop using a reversed range to avoid delete conflicts
                if crv_list[i] not in my_list:
                    del crv_list[i]

            if len(crv_list) == 0:
                alert.Error('These wells have no common curves')
                global_vars.ui.Root.window.deiconify()
                os.chdir(curDir)
                raise Exception()
        count +=1

    #restore list when mopt==3
    if mopt==3 and count>=1:
        #if well list wells not all with core then remove core curves
        os.chdir(global_vars.project.inDir)
        list1 = glob.glob("*.cas")
        found=1
        for uwi in global_vars.project.currentWellList:  #If some Well_List wells have 'cas' files
            if uwi+'.cas' not in list1:
                found=0
        os.chdir(global_vars.project.outDir)
        if found==1:
            if "CORE DATA" in old_list:
                ind = old_list.index("CORE DATA")
                old_list=old_list[:ind]  #remove "CORE DATA "
                old_list.append('OUTDIR CURVES')
        else: #If All wells have core
            old_list.append('OUTDIR CURVES')
        crv_list=old_list + crv_list

    if crv_list[0]!='None':
        crv_list.insert(0,'None')
    #when done return list
    save_MissCrvs()
    os.chdir(curDir)
    return crv_list
# ----------------------------------------------------------------------------------------------------------
def comm_core( crv_list):
    '''
    Find core cores (in cas file) for Well_List
    '''
    Cur_dir=os.getcwd()
    os.chdir(global_vars.project.inDir)

    mycore=glob.glob('*.cas')       #Get list of wells with cas-files
    all_flag=1
    for uwi in global_vars.project.currentWellList:
        if (uwi+'.cas') not in mycore:          #if Not all wells in Well_list have a cas file
            all_flag=0
            break       #get out

    if all_flag==1:             #all wells in well list have cas files
        for well in global_vars.project.currentWellList.GetWells():
            #if NOT all curves in Well_List have a core description get out
            #get cas_data and create core_df
            cas_data = well.GetLASHeaders(Dir.In, ".cas")
            null=cas_data.well.NULL.value
            core_df=cas_data.df()
            #check if core_df['COREDEPT'] is empty
            c=core_df['COREDEPT'].copy()
            c.replace(null, np.NaN, inplace=True)
            if c.empty== True:              #if NOT ALL wells have a core description curves
                all_flag=2
                break

    if all_flag>0:      #update curve list for cas curves
        crv_list.append("CORE DATA")
        unwanted=['DEPT','CORNO' ,'S_TP','S_TCK', 'COREDEPT','SAMPLE','ACCESSORIES','SEDSTRUCT']
        idx=0
        for crv in global_vars.cdescrvs:              # now add core curves
            if crv not in unwanted:
                if all_flag==1:
                    crv_list.append(crv)
                elif all_flag==2:
                    if idx>=35:
                        crv_list.append(crv)
            idx +=1
    os.chdir(Cur_dir)
    return crv_list
# ----------------------------------------------------------------------------------------------------------
def loadCL():
    '''
    Load all curve names in Indir
    '''
    print('LoadCL()')

    global_vars.project.curves=[]    #Reset

    mpath= global_vars.project.inDir + '/databases/ALLcurves.TXT'
    try:
        with open(mpath,newline='', encoding= global_vars.fileEncoding) as f:
            reader = csv.reader(f)
            global_vars.project.curves = list(reader)

    except FileNotFoundError:
        alert.Error('File with Indir Curves could could not be found. Please, run Update Project.')
    except ValueError:
        alert.Error('File with Indir Curves could could not be opened. Please, try again')

    return

#---------------------------------------------------------------------------------------------------------
def pcrv_aka(well : 'Well'):
    '''
    find akas in las file
    opt 0 is Indir
    '''
    aka_lst=[]          #Initiate list
    for curve in well.GetWellFile(Dir.In).curves: # for each curve in Indir wells
        name = global_vars.project.curveNameTranslator.GetName(curve)
        if(name != ''):
            aka_lst.append(name)
        else:
            global_vars.missingCurveList.append([well.uwi,curve])

    return aka_lst
#------------------------------------------------------------------------------------
def save_MissCrvs():
    '''
        Save curves of well list with curves not in Alias file
    '''

    curDir=os.getcwd()
    os.chdir(global_vars.project.inDir)
    mpath='databases/Misscurves.TXT'
    with open(mpath,'w', encoding=global_vars.fileEncoding) as f:
        for mline in global_vars.missingCurveList:
            record=''
            for it in mline: #Create a string
                record=record + it+ ','
            # write Frm data
            record=record[:-1]+'\n'
            f.write(record)
        f.close()

    os.chdir(curDir)
#------------------------------------------------------------------------------------
def get_aka(alias, lasdata):
    '''
    #get aka name for an alias
    '''
    # alias name index number in alias array
    name = global_vars.project.curveNameTranslator.GetName(alias)
    aliasList = global_vars.project.curveNameTranslator.GetAliases(name)

    for alias in aliasList:
        if alias in lasdata.curves:
            return alias