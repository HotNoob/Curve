#main.py contains main program functions without a dedicate module or class. this will be a transitory location for many functions.
import os
import traceback
from tkinter import filedialog, messagebox

import pandas as pd

import global_vars
from enumerables import Help
from structs import ZoneDepths

from . import alert, excel, prompt


# ==========================================================================================================
#Status line
def stat_update(mdir, myindex):
    '''
        option 6 - update entire status line
        option 7 - well progress counter

    '''
    if global_vars.ui.Root.status is None:
        return

    if mdir==global_vars.project.inDir and myindex==0:
        mydir='IN Dir'
        maxlen=int(20)
    if mdir==global_vars.project.outDir and myindex==1:
        mydir='OUT Dir'
        maxlen=int(20)
    if mdir==global_vars.inFile and myindex==2:
        mydir='IN File'
        maxlen=int(40)
    if mdir==global_vars.project.rawDir and myindex==3:
        mydir='Raw'
        maxlen=int(20)
    if mdir==global_vars.project.coreDir and myindex==4:
        mydir='  Core'
        maxlen=int(20)
    if mdir==global_vars.project.clientDir and myindex==5:
        mydir='  Core'
        maxlen=int(20)
    if myindex==6:      #update entire line
        mylen=str(len(global_vars.project.currentWellList))
        mylen2=str(len(global_vars.project.projectWellList))
        mydir= f"{global_vars.project.settings.Get('name')+ '  ' + mylen + ' of '+ mylen2 +' Wells IN Dir: ' + global_vars.project.inDir[20:] + '  OUT Dir: ' + global_vars.project.outDir[20:] + '  Raw: ' + global_vars.project.rawDir[20:] + '  Core: ' + global_vars.project.coreDir[20:] + '  Client: ' + global_vars.project.clientDir[20:]}"
        global_vars.ui.Root.status.set(mydir)
        return
    if myindex==7:      #update well progress r
        mylen=str(len(global_vars.project.currentWellList))
        mydir= f"{global_vars.project.settings.Get('name')+ '     ' + mdir + ' of '+ mylen +' Wells'}"
        global_vars.ui.Root.status.set(mydir)
        return
    if myindex!=7 and myindex!=6:
        mydir=''
        maxlen=int(20)

    if global_vars.ui.Root.status.get() == 'Waiting for directories':
        if len(mdir) > maxlen:
            mydir = mydir + ': ...' + mdir[-maxlen:]
        else:
            mydir = mydir + ': ' + mdir
    else:
        if len(mdir) > maxlen:
            mydir = mydir + ': ...' + mdir[-maxlen:]
        else:
            mydir = mydir +': ' + mdir

    global_vars.myStatList[myindex]=mydir
    global_vars.ui.Root.status.set(global_vars.myStatList[0]+" "*3 + global_vars.myStatList[1]+" "*3 + global_vars.myStatList[2]+ " "*3 + global_vars.myStatList[3] + " "+global_vars.myStatList[4]+ " "+global_vars.myStatList[5])
#------------------------------------------------------------------------------------------------------
def PetroFacies(crv1, crv2, mzone):
    '''
    Load, update and save PetroFacies
    '''
    f1yesno=False      #default
    f2yesno=False      #default

    #crvs=['GR','RHOB','NPHI','DT','PE']

    if global_vars.PF!=[]:   #IF Petrofacies selected
        yesno=prompt.yesno("Update Petrofacies data Y or N?")
        if yesno==False:
            return
        if yesno==True:
            try:
                mpath='databases/PETROFAC.xlsx'
                df=excel.get_exceldata(mpath)
            except Exception:
                print(traceback.format_exc)
                alert.Error('{mpath} not found in project - Create empty template')

            f_idx=0
            #check columns for crvs
            if df.empty==True:
                return
            col_list=list(df.columns.values)
            if crv1 in col_list:
                f1yesno=prompt.yesno(f"{crv1} already in Facies dataframe. Overwrite (Y/N)?")
                newc1=df[crv1]
            if crv2 in col_list:
                f2yesno=prompt.yesno(f"{crv2} already in Facies dataframe. Overwrite (Y/N)?")
                newc2=df[crv2]

            for item in df.index:            #loop through df rows
                if df.iloc[item]['PetroFacies']==global_vars.PF[f_idx][0]:  #found Petrofacies row - now fill it in
                    mymin=round(global_vars.PF[f_idx][3][0],4)
                    mymax=round(global_vars.PF[f_idx][3][1],4)
                    ltgt=str(mymin)+','+str(mymax)
                    if f1yesno==True:
                        newc1.iloc[item]=ltgt              #store in curve or create new curve column
                    mymin=round(global_vars.PF[f_idx][3][2],4)
                    mymax=round(global_vars.PF[f_idx][3][3],4)
                    ltgt=str(mymin)+','+str(mymax)
                    if f2yesno==True:
                        newc2.iloc[item]=ltgt              #store in curve or create new name column
                    f_idx +=1   #Next PF list

            #Enter zone
            df.iloc[1]['OTHER']=mzone

            #update excel file
            curDir=os.getcwd()
            os.chdir(global_vars.project.inDir)
            try:
                filename= r"{}".format(mpath)
                df.to_excel(filename,index=False)

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

def find_aka(crv1,crv_list,fnd_key, las_data, opt, zoneDepths : ZoneDepths ):
    '''
        find aka name in alias array
        opt 0 = for finding an alias_array curve
        opt 1 = for normalizing to include UWIs curves or else for xplots
        opt 2 = for finding a calulated curve (Outdir)
    '''
    # get las data frame
    df = las_data.df()

    ls_strt=las_data.well.strt.value
    cstep=las_data.well.STEP.value
    if opt==1:
        df['UWI'] = str(las_data.well.UWI.value)   #add a curve filled with the UWI
        df['DEPT'] = df.index          # DEPT as index

    c1=pd.DataFrame(None)
    #set depth interval
    idx_top=int((zoneDepths.top - ls_strt)/cstep)
    idx_bot=int((zoneDepths.base - ls_strt)/cstep)+1  #get very last of array

    # Find alias curve names
    # Index for alias array of aka-s for alias name
    if(crv1 in crv_list):  #check list of alias curves
        if opt==2:
            if crv1 not in df.columns:
                alert.Error(crv1 + ' not in ' + las_data.well.WELL.value + f' - {las_data.well.UWI.value} in outDir')
                raise Exception
            c1=df.iloc[idx_top:idx_bot][crv1]
            return c1, fnd_key
        else:
            myList = global_vars.project.curveNameTranslator.GetAliases(crv1)
            for aka in myList:     # check aka-s against LAS file curves or calculated curves
                if aka in df.columns:
                    #for depth interval in df index
                    if opt==1:
                        c1=df.iloc[idx_top:idx_bot]
                        c1=c1[[aka,'UWI']]
                        if aka!=crv1:
                            c1.rename(columns = {aka:crv1}, inplace = True)
                        return c1, fnd_key
                    else:
                        c1=df.iloc[idx_top:idx_bot][aka]
                        return c1, fnd_key

    return c1, 0

def show_las(well : str | int):

    curDir = os.getcwd()
    os.chdir(global_vars.project.inDir)

    if global_vars.project.inDir == 'c:/':   # No Indir selected return
        myTXT="No Input directory selected first do so in File>Directories"
        alert.Error(myTXT)
        return

    if well==0:
        #load data LAS using a file dialog box
        try:
            well = filedialog.askopenfilename(
            #initialdir = inDir,
            title="Please, select an input file",
            filetype=(("LAS files", "*.las"), ("all files", "*.*"))
            )
        except FileNotFoundError:
            alert.Error('Directory could not be found. Please, try again.')
        except ValueError:
            alert.Error('File could not be opened. Please, try again')
    else:
        myTXT = f"{'Do you want to see ' + well + ' in ' +global_vars.project.inDir + '?'}"
        MsgBox = messagebox.askquestion (message=myTXT,icon = 'warning')
        if MsgBox == 'no':
            os.chdir(curDir)
            return

    osCommandString = "start notepad.exe " + well
    os.system(osCommandString)

    os.chdir(curDir)

#-----------------------------------------------------------------------------------------------------------------------
def get_scale(curv1, curv2, curv3, zcurv):
    ''' this function should be phased out '''
    # Define scales
    c1_scale=''
    c2_scale=''
    c3_scale=''
    z_scale=''

    if curv1 and curv1 in global_vars.project.curveParameters:
        c1_scale= global_vars.project.curveParameters[curv1].scale.strip('()')

    if curv2 and curv2 in global_vars.project.curveParameters:
        c2_scale= global_vars.project.curveParameters[curv2].scale.strip('()')

    if curv3 and curv3 in global_vars.project.curveParameters:
        c3_scale= global_vars.project.curveParameters[curv3].scale.strip('()')

    if zcurv and zcurv in global_vars.project.curveParameters:
        z_scale= global_vars.project.curveParameters[zcurv].scale.strip('()')

    if curv2=='':                                # if histogram
        return c1_scale,0,0,0
    elif zcurv=='' and curv3=='':                 # if Xplot
        return c1_scale, c2_scale,0, 0
    elif curv3=='':                               # if Zplot
        return c1_scale, c2_scale, 0, z_scale
    elif zcurv!='' and curv1!='' and curv2!='' and curv2!='':                 # if 3D
        return c1_scale, c2_scale, c3_scale, z_scale
    else:
        alert.Error("A curve is missing in get_scale function")
        return

#=====================================================================================================
def c_help(opt : Help = 0):
    '''
    display the help file
    '''

    if(isinstance(opt, int)):
        opt = Help(opt)

    curDir=os.getcwd()

    if opt==Help.Curve:
        mpath = 'c:/curvehelpfiles/CURVE_HELP.docx'
    if opt==Help.Graph:
        mpath = 'c:/curvehelpfiles/GRAPH_HELP.docx'

    spath= r"{}".format(mpath)
    os.startfile(spath)

    os.chdir(curDir)
