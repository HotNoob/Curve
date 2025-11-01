import os
from datetime import datetime
from tkinter import (BROWSE, NS, VERTICAL, Button, E, Label, LabelFrame,
                     Listbox, StringVar, W, filedialog, ttk)
import tkinter
from typing import TYPE_CHECKING

import lasio
from matplotlib import pyplot
import numpy as np
import pandas as pd

import Curve
from classes.Object import Object                
from classes.Plot.DepthPlot import DepthPlot
from classes.Project.WellList import WellList
import global_vars
from defs import alert, common, las, main, program, prompt, excel
from enumerables import Dir, ErrorMessage
from structs import ZoneDepths


if TYPE_CHECKING:
    from classes.Project.Well import Well
    from classes.Project.WellFile import WellFile



def copy_in_to(opt):
    '''
    copy files from INDIR (opt 1 and 3) or from OUTDIR (opt 2)
    to OUTDIR (opt 1) or CLIENTDIR (opt 2 and 3) COPY from OUTDIR to INDIR (opt 5)- Rename curve (opt 4)
    '''
    print(f"copy_in_to({opt})")

    curdir=os.getcwd()                  #keep track of working directory

    global_vars.ui.Root.window.iconify()

    #if opt 4 - select directory to change curve names)
    if opt==4:
        try:
            global_vars.myDir = filedialog.askdirectory(
                title="Please, select an input folder",
                initialdir=global_vars.project.inDir[:-7])
        except FileNotFoundError:
            alert.Error('Directory could not be found. Please, try again.')
            global_vars.ui.Root.window.deiconify()
            return
        except ValueError:
            alert.Error('File could not be opened. Please, try again.')
            global_vars.ui.Root.window.deiconify()
            return
        if global_vars.myDir != global_vars.project.inDir and global_vars.myDir != global_vars.project.outDir and global_vars.myDir != global_vars.project.clientDir:
            alert.Error(f"{global_vars.myDir} is an incorrect Input Directory")
            return

        #get alias if mydir is Indir
        if global_vars.myDir==global_vars.project.inDir:                        #If Indir selected get alias list for crv_list
            # create curve selection list
            to_list=global_vars.project.curveNameTranslator.GetNames()
            to_list.insert(0, 'None')
        else:                     #otherwise get calculated curves
            #Calculated curves already defined in main wells: crvnm
            to_list=[]
            to_list.append('None')
            for a in global_vars.CalcCurveNames:
                to_list.append(a)
            crv_list=to_list

    #Get alias list for Indir
    if opt==1 or opt==3:
        # create curve selection list
        crv_list=[]   #empty crv_list
        crv_list=program.com_crvs('DEPT',crv_list,1)
        del crv_list[0]
        #global_vars.project.curveNameTranslator.GetNames()
        #Calculated curves allready defined in main wells: crvnm
        to_list=[]
        for a in global_vars.CalcCurveNames:
            to_list.append(a)
    if opt==2:   #Set curve lists to crvnm
        to_list=[]
        #Calculated curves allready defined in main wells: crvnm
        to_list.append('None')
        for a in global_vars.CalcCurveNames:
            to_list.append(a)
        crv_list=to_list  # copy to_list into crv_list
    if opt==5:
        no_crvs=[]      #create empty no_crvlist
        to_list=[]      #create empty to_list
        crv_list=[] 
             #create empty crv_list)

        crv_list = program.com_crvs('DEPT',to_list,0)    #get list of common curves in outdirs of Well List
        to_list = program.com_crvs(no_crvs,crv_list,1)     #add list of common curves in indirs of Well_List
        del crv_list[0]

    #create toplevel window
    cpy_win = common.initCommonWindow(title='', width=270, height=310)

   # Define Well list frame
    cpy_frame=LabelFrame(cpy_win,text="From: ")
    cpy_frame.grid(column=0,row=0, sticky=NS)
   # Define To list frame
    cto_frame=LabelFrame(cpy_win, text='To: ')
    cto_frame.grid(column=1,row=0, sticky=NS)

    #window expansion
    cpy_win.rowconfigure(0,weight=1)
    cpy_win.columnconfigure(0,weight=1)

    #frame expansion
    cpy_frame.rowconfigure(0,weight=1)
    cpy_frame.columnconfigure(0,weight=1)
    #frame expansion
    cto_frame.rowconfigure(1,weight=1)
    cto_frame.columnconfigure(1,weight=1)

    # Create selectable well listbox gr_win
    crv_names=StringVar(value=crv_list)
    cto_names=StringVar(value=to_list)
    height=len(crv_list)
    if height>20:                   #box height beyond frame height
        height=20

    #install scrollbar to wellbox
    cpy_scroll=ttk.Scrollbar(cpy_frame,orient=VERTICAL)
    cpy_scroll.pack(side='right',  fill='y')
    cto_scroll=ttk.Scrollbar(cto_frame,orient=VERTICAL)
    cto_scroll.pack(side='right', fill='y')

    cpy_box=Listbox(cpy_frame,exportselection=0, listvariable=crv_names, height=height, selectmode=BROWSE)
    cpy_box.pack()
    cpy_box['yscrollcommand']=cpy_scroll.set
    cto_box=Listbox(cto_frame,exportselection=0,listvariable=cto_names, height=height, selectmode=BROWSE)
    cto_box.pack()
    cto_box['yscrollcommand']=cto_scroll.set
    # Colorize alternating lines of the listbox
    for i in range(0,len(crv_list)-2,2):
        cpy_box.itemconfigure(i,background='#f0f0ff')
        if i<len(global_vars.CalcCurveNames)-2:    
            cto_box.itemconfigure(i,background='#f0f0ff')

    cpy_scroll.config( command=cpy_box.yview) # select one or more wells
    cto_scroll.config( command=cto_box.yview) # select one or more wells

    # If curves selected
    cpy_box.selection_clear(0,'end')
    cto_box.selection_clear(0,'end')

    '''
    cpy_box.bind("<Double-1>", lambda e: cpy_quit(cpy_win))
    #cpy_box.bind("<Button-1>", command=lambda mx: mx=cpy_box.get()     # left mouse button
    cto_box.bind("<<ListboxSelect>>", lambda e: cpy_crv(cpy_win,cpy_box, cto_box, opt))
    #cpy_box.bind("<Button-3>", lambda 
    e:  Submit_cpy(cpy_win,outdir))     # left mouse button
    '''

    # done
    b_done=Button(cpy_win, bg='cyan', text="Copy", command=lambda:cpy_crv(cpy_win,cpy_box, cto_box, opt))
    b_cancel=Button(cpy_win, bg='pink', text='Done/Cancel', command= cpy_win.quit)

    #place widgets
    b_done.grid(row=2, column=0, padx=10, pady=10,sticky = W)
    b_cancel.grid(row=2, column=1,padx=10,pady=10,sticky= E)

    my_instruct='Select curve from input directory,\nselect new curve in output directory\nPress Copy when ready or Cancel to stop'
    alert.Message(my_instruct)

    cpy_box.focus_set()

    cpy_win.mainloop()   #loop until quit
    cpy_win.destroy()

    os.chdir(curdir)
    
    #close script and update project
    alert.Message("Scan")   
    global_vars.project.Scan ()
    alert.Message("Updating Project")
    global_vars.ui.Root.Update()  
    global_vars.ui.Root.window.deiconify()
#-----------------------------------------------------------------------------------------------------
def cpy_crv(cpy_win, sel_frm, sel_to, opt):
    '''
    Select curve to be copied and copy to be created
    INDIR (opt 1 and 3) or from OUTDIR (opt 2)
    to InDIR (opt 5) or CLIENTDIR (opt 2 and 3) if opt =4 switch to mydir and rename curves
    '''
    #general purpose dataframes
        #to return transfer data between functions (such as copy)

    cpy_win.iconify()

    if sel_to.curselection()==() or sel_frm.curselection()==():  #if not both lists selected
        alert.Message("select curve to copy AND new curve name")
        cpy_win.deiconify()
        return

    else:                                                       #if both in and from selected continue
        out_ix=sel_to.curselection()
        in_ix=sel_frm.curselection()
        input_curve=sel_frm.get(in_ix[0])
        output_curve=sel_to.get(out_ix[0])

        # get directories
        if opt==1:
            my_output=global_vars.project.outDir
        if opt==2:
            if global_vars.project.clientDir=="":               # if clientdir not yet set
                prompt.ClientDir()
            my_output=global_vars.project.clientDir
        if opt==3:
            if global_vars.project.clientDir=="":               # if clientdir not yet set
                prompt.ClientDir()
            my_output=global_vars.project.clientDir
        if opt==5:
            if global_vars.project.outDir=="":               # if clientdir not yet set
                prompt.OutputDir()
            my_output=global_vars.project.inDir
            if output_curve=='None':     #if no curve name selected set to input_curve
                output_curve=input_curve

        #current well list
        All_cur_Wells= global_vars.project.currentWellList.GetWells()
        for well in All_cur_Wells:
            alert.Message(f"{well.uwi} ({well.alias}) is being processed")

            #load global dfs
            if opt==1 or opt==3:     # if copied from Indir
                las_data = well.GetLASData(Dir.In)
                if not las_data:                     #canceled or no file in client dir
                    cpy_win.deiconify()
                    return

                global_vars.in_df=las_data.df()
                #find input curve aka in Las
                found = False
                aliasList = global_vars.project.curveNameTranslator.GetAliases(input_curve)
                for curve in las_data.curves:
                    if curve.mnemonic in aliasList:
                        input_curve=curve.mnemonic
                        crv_desc=curve.descr
                        crv_unit=curve.unit
                        found = True
                        break

                if not found:      # curve not found
                    input_curve=sel_frm.get(in_ix[0])
                    continue       # go to next well
                if opt==1:
                    las_data = well.GetLASData(Dir.Out)
                    las_df = las_data.df()
                if opt==3:
                    las_df=las_data.df()                #Save input dir las_data dataframe in las_df
                    las_data = well.GetLASData(Dir.Client)
                    if not las_data:
                        myDpt=las_df.index
                        path_name=global_vars.project.inDir+'/'+well.uwi + ".las"   # get file to be recreated
                        las_data=create_cas(path_name)
                        las_data.insert_curve(ix=0, mnemonic='DEPT', data=np.array(myDpt),
                        unit= 'M', descr='DEPTH',
                        value='')

                if not las_data:
                    #canceled
                    message=f"{well.uwi}.las not in {my_output} - create new las file?"
                    myes=prompt.yesno(message)
                    if myes==True:
                        #create new lasfile in Outdir
                        myDpt=global_vars.in_df.index  #get depth index from indir las
                        path_name=global_vars.project.inDir+'/'+well.uwi + ".las"   # get file to be recreated
                        las_data=create_cas(path_name)
                        las_data.insert_curve(ix=0, mnemonic='DEPT', data=np.array(myDpt),
                        unit= 'M', descr='DEPTH',
                        value='')
                    else:
                        cpy_win.deiconify()
                        return

                global_vars.out_df=las_data.df()    #set data frame for output

                if output_curve in global_vars.out_df:
                    message=f'{output_curve} already exists in {well.uwi}.las . Overwrite? Y/N'
                    myes=prompt.yesno(message)
                    if myes==True:
                        #overwrite
                        global_vars.out_df[output_curve]=global_vars.in_df[input_curve]
                        las_df=global_vars.out_df #trying to keep track of dataframes
                        #update curve description and units

                else:
                    global_vars.out_df[output_curve]=global_vars.in_df[input_curve]

            if opt==2:          #input_dir = Outdir   output_dir= ClientDir
                las_data = well.GetLASData(Dir.Out)
                global_vars.in_df=las_data.df()                #Save input dir (OutDir) in In_df
                #get output las
                las_data = well.GetLASData(Dir.Client)
                if not las_data:
                    myDpt=las_df.index
                    path_name=global_vars.project.inDir+'/'+well.uwi+".las"   # get file to be recreated
                    las_data=create_cas(path_name)
                    las_data.insert_curve(ix=0, mnemonic='DEPT', data=np.array(myDpt),
                    unit= 'M', descr='DEPTH',
                    value='')
                global_vars.out_df=las_data.df()            #Save output dir (ClientDir) in Out_df

                if output_curve in global_vars.out_df:
                    message=f'{output_curve} already exists in {well.uwi}.las. Overwrite? Y/N'
                    myes=prompt.yesno(message)
                    if myes==True:
                        #overwrite
                        global_vars.out_df[output_curve]=global_vars.in_df[input_curve]
                        #update curve description and units
                else:
                    global_vars.out_df[output_curve]=global_vars.in_df[input_curve]

            if opt==4:      #rename
                # las data for current well
                if global_vars.myDir==global_vars.project.inDir:
                    las_data = well.GetLASData(Dir.In)
                elif global_vars.myDir==global_vars.project.outDir:
                    las_data = well.GetLASData(Dir.Out)
                elif global_vars.myDir==global_vars.project.clientDir:
                    las_data = well.GetLASData(Dir.Client)
                else:
                    alert.Error(f"{global_vars.myDir} is an incorrect Input Directory")
                    cpy_win.deiconify()
                    return

                if las_data is None:                     #canceled or no file in client dir
                    cpy_win.deiconify()
                    return
                
                for c in las_data.curves:
                    if c.mnemonic==output_curve:
                        alert.Error(f"{c.mnemonic} already in {well.uwi}.las - skip well" )
                        continue

                #find aka name for input curve
                if global_vars.myDir==global_vars.project.inDir:
                    #find input curve aka in Las
                    aliasList = global_vars.project.curveNameTranslator.GetAliases(input_curve)
                    for curve in las_data.curves:       #find in las data curve
                        if curve.mnemonic in aliasList:
                            curve.mnemonic=output_curve
                            #save in lasfile
                            curdir=os.getcwd()
                            os.chdir(global_vars.myDir)
                            las_data.write(well.uwi+".las", fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
                            os.chdir(curdir)
                            break
                else:
                    fnd_fl=0
                    for curve in las_data.curves:       #find in las data curve
                        if input_curve == curve.mnemonic:    #found input curve
                            curve.mnemonic=output_curve
                            #save in lasfile
                            curdir=os.getcwd()
                            os.chdir(global_vars.myDir)
                            las_data.write(well.uwi+".las", fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
                            os.chdir(curdir)
                            fnd_fl=1
                        if fnd_fl==1:
                            break       #break las curve loop
                input_curve=sel_frm.get(in_ix[0])
                continue       # go to next well
            if opt==5:
                las_data = well.GetLASData(Dir.Out)
                if not las_data:
                    alert.Error(f"{well.uwi}.las does not exist in {global_vars.project.outDir}")
                    continue    # next well
                for curve in las_data.curves:
                    if curve.mnemonic==input_curve:
                        crv_desc=curve.descr
                        crv_unit=curve.unit
                global_vars.in_df=las_data.df()                 #input df

                las_data=well.GetLASData(Dir.In)          # get las from Indir
                if not las_data:
                    alert.Error(f"{well.uwi}.las does not exist in {global_vars.project.inDir}")
                    continue    # next well

                global_vars.out_df=las_data.df()    #set data frame for output
                if output_curve in global_vars.out_df:
                    message=f'{output_curve} already exists in {well.uwi}.las . Overwrite? Y/N'
                    myes=prompt.yesno(message)
                    if myes==True:
                        #overwrite/Copy
                        global_vars.out_df[output_curve]=global_vars.in_df[input_curve]
                        #update curve description and units
                    else:
                        alert.Message(f"Skip {well.uwi}.las")
                        continue
                else:

                    #Copy to out_df
                    global_vars.out_df[output_curve]=global_vars.in_df[input_curve]

            #Update well file in outdir
            las_df=global_vars.out_df
            #find curve in updated las
            las_data.set_data(las_df)    #update las_data
            for curve in las_data.curves:
                if curve.mnemonic==output_curve:
                    curve.descr=crv_desc
                    curve.unit=crv_unit
            
            #las_data.set_data(las_df)    #update las_data and save in my_output dir
            filename= my_output + '/'  + well.uwi + ".las"
            las_data.write(filename, fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
            curdir=os.getcwd()
            os.chdir(my_output)

            sel_frm.selection_clear(0,'end')
            sel_to.selection_clear(0,'end')
    
    if opt==5 or opt==1 or opt==3:   #update P_crvs when new curves in Indir
        alert.Message("Update project curve list for Indir")
        global_vars.project.Scan()
    cpy_win.deiconify()
#-----------------------------------------------------------------------------------------------------
def cpy_quit(win):
    '''
    Done copying
    '''
    win.destroy()
#-----------------------------------------------------------------------------------------------------
def advance_crv(opt):
    '''
    copy, rename of delete a curve from any selected LAS file of Well_List
    opt = 1  Copy
    opt = 2  Rename
    opt = 3  Delete
    '''

    global_vars.ui.Root.window.iconify()

    try:
        global_vars.myDir = filedialog.askdirectory(
            title="Please, select an input folder",
            initialdir=global_vars.project.inDir[:-7])
    except FileNotFoundError:
        alert.Error('Directory could not be found. Please, try again.')
        global_vars.ui.Root.window.deiconify()
        return
    except ValueError:
        alert.Error('File could not be opened. Please, try again.')
        global_vars.ui.Root.window.deiconify()
        return

    if global_vars.myDir != global_vars.project.inDir and global_vars.myDir != global_vars.project.outDir and global_vars.myDir != global_vars.project.clientDir:
        alert.Error(f"{global_vars.myDir} is an incorrect Input Directory")
        global_vars.ui.Root.window.deiconify()
        return

    dir : Dir = None
    if global_vars.myDir==global_vars.project.inDir:
        nopt=1
        mopt=0   #For get_lasdata
        dir = Dir.In
    elif global_vars.myDir==global_vars.project.outDir:
        nopt=0
        mopt=1   #For get_lasdata
        dir = Dir.Out
    elif global_vars.myDir==global_vars.project.clientDir:
        nopt=2
        mopt=2   #For get_lasdata
        dir = Dir.Client
    else:
        alert.Error("Incorrect data directory - only select: Las_CLIENT, LAS_IN or LAS_OUT,")
        return

    #create list of curves common in Well_List
    crv_list=[]
    no_crvs=['DEPT']
    crv_list = program.com_crvs(no_crvs,crv_list,nopt)
    del(crv_list[0])  # Remove None option

    #Open top level window
    adv_win = common.initCommonWindow('', 280, 310, y = 100)

   # Define Well list frame
    adv_frame=LabelFrame(adv_win,text="Select Curve: ")
    adv_frame.grid(column=0,row=0, sticky=NS)
   # Define To list frame

    #window expansion
    adv_win.rowconfigure(0,weight=1)
    adv_win.columnconfigure(0,weight=1)

    #frame expansion
    adv_frame.rowconfigure(0,weight=1)
    adv_frame.columnconfigure(0,weight=1)

    # Create selectable well listbox gr_win
    crv_names=StringVar(value=crv_list)
    height=len(crv_list)
    if height>12:                   #box height beyond frame height
        height=12

    #install scrollbar to wellbox
    adv_scroll=ttk.Scrollbar(adv_frame,orient=VERTICAL)
    adv_scroll.pack(side='right', fill='y')

    adv_box=Listbox(adv_frame,exportselection=0, listvariable=crv_names, height=height, selectmode=BROWSE)
    adv_box.pack()
    adv_box['yscrollcommand']=adv_scroll.set

    # Colorize alternating lines of the listbox
    for i in range(0,len(crv_list)-2,2):
        adv_box.itemconfigure(i,background='#f0f0ff')

    adv_scroll.config( command=adv_box.yview) # select one or more wells

    if opt==1 or opt==2:
        Newlabel=Label(adv_win,text='Enter New Curve Name')
        varNew=StringVar()
        varNew.set("NewCurve")
        Newentry=ttk.Entry(adv_win,textvariable=varNew, width=12)
        Newlabel.grid(row=height, column=0, sticky=W)
        Newentry.grid(row=height+1, column=1,pady=10, sticky=E)

    # If curves selected
    adv_box.selection_clear(0,'end')

    adv_box.bind("<Double-1>", lambda e: adv_quit(adv_win))
    #adv_box.bind("<Button-1>", command=lambda mx: mx=adv_box.get()     # left mouse button
    #adv_box.bind("<Button-3>", lambda e:  Submit_cpy(adv_win,outdir))     # left mouse button

    if opt==1:
        my_instruct='Select curve to be COPIED\nDouble click on list when done\nClose window (X) to ABORT'
    elif opt==2:
        my_instruct='Select curve to be RENAMED\nDouble click on list when done\nClose window (X) to ABORT'
    else:
        my_instruct='Select curve to be DELETED\nDouble click on list when done\nClose window (X) to ABORT'
    alert.Message(my_instruct)

    adv_box.focus_set()
    adv_win.mainloop()

    if adv_box.curselection()==() :  #if no curve selected
        return
    else:                                                       #if both in and from selected continue
        in_ix=adv_box.curselection()
        input_curve=adv_box.get(in_ix[0])
        if opt<3:
            new_curve=varNew.get()

    adv_win.destroy()

    for well in global_vars.project.currentWellList.GetWells():
        #open Las_file
        las_data = well.GetLASData(dir)
        global_vars.las_df = las_data.df()

        if opt==1:               #Copy curve
            #new curve
            global_vars.las_df[new_curve]=global_vars.las_df[input_curve].copy()
            las_data.set_data(global_vars.las_df)    #update las_data
        if opt==2:   #rename curve
            #rename curve
            for crv in las_data.curves:
                if input_curve == crv.mnemonic:  #Found old curve name
                    crv.mnemonic = new_curve
                    #las_data.set_data(las_df)    #update las_data
                    break
        if opt==3:               #delete curve
            las_data.delete_curve(mnemonic=input_curve, ix=None)

        #save las file
        CurDir=os.getcwd()
        os.chdir(global_vars.myDir)
        las_data.write(well.uwi+".las", fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
        os.chdir(CurDir)
    
    global_vars.ui.Root.window.deiconify()
#-----------------------------------------------------------------------------------------------------
def adv_quit(win,adv_box,opt):
    '''
    Quit adv_win
    '''

    win.quit()

    if opt==1:              #Delete button
        global_vars.mflag=1
    if opt==0:              #Done/Cancel
        global_vars.mflag=0

#-----------------------------------------------------------------------------------------------------
def del_any_crv():
    '''
    Delete any curve in an las file
    '''
    global_vars.mflag = 1       #Refresh adv_win
 
    #global_vars.ui.Root.window.iconify()
    #Get Directory
    curDir=os.getcwd()
    #use current well list or select a random las file
    yn=prompt.yesno("Use current well list (Y) or a selected las file (N) ")
    if yn==False:   #if No
        try:
            list_f = filedialog.askopenfilename(
                initialdir = global_vars.project.inDir[:-7],
                title="Please, select a LAS file",
                filetypes=(("Projects", "*.las"),)
                )
        except FileNotFoundError:
            alert.Error('{list_f} could not be found. Please, try again.')
            program.c_project()
        except ValueError:
            alert.Error('{list_f} with project settings could not be opened. Please, try again')
            return
            
        #get LAS file
        ixdir=list_f.rfind('/')   #Reverse find of substring
        Mydir=list_f[:ixdir]

        dir : Dir = None
        if Mydir==global_vars.project.inDir:
            dir = Dir.In
        elif Mydir==global_vars.project.outDir:
            dir = Dir.Out
        elif Mydir==global_vars.project.clientDir:
            dir = Dir.Client
        else:
            alert.Error(f'{Mydir} is not a valid directory')
            return
                
        idx=list_f.rfind('/')   #Reverse find of substring
        myname=list_f[idx+1:-4]

        well : 'Well' = global_vars.project.projectWellList.Get(myname)

        del_curves(well, dir)
        
    if yn==True:   #if yes get current well list
        well_list= global_vars.project.currentWellList.GetWells()
        mydir=prompt.customButtonPrompt(question='Select directory',buttons=['Indir','Outdir'])
    
        mydir=mydir[:-3]   

        dir : Dir = None
        if mydir=='In':
            dir = Dir.In
        elif mydir=='Out':
            dir = Dir.Out
        else:
            alert.Error(f'{mydir} is not a valid directory')
            return

        for well in well_list:
            del_curves(well,dir)
        

def del_curves (well : 'Well', mydir : 'Dir'):
    ''' Del curves from las file'''    
        #select curves
    global_vars.mflag=1 

    #open Las_file
    las_file : 'WellFile' = well.GetWellFile(mydir)
    las_data = las_file.GetLASData()
    global_vars.las_df = las_data.df()

    while global_vars.mflag==1:
        #create list of curves common in Well_List
        #crv_list = list(las_data.curvesdict.items())
        crv_list=[]
        crv_list = list(las_data.curvesdict.keys())
        del(crv_list[0])  # Remove None option or Dept curve.

        #Open top level window
        adv_win = common.initCommonWindow('', 280, 310, y = 100)

        # Create selectable well listbox gr_win
        crv_names=StringVar(value=crv_list)
        height=len(crv_list)
        if height>12:                   #box height beyond frame height
            height=12
        adv_label=Label(adv_win, text='Select curve to select for deletion\n To execute press <Delete/Done> button \n Press Close window (X) to ABORT')
        adv_label.grid(column=0,row=0)
        # Define Well list frame
        adv_frame=LabelFrame(adv_win,text="Select Curve: ",height=height)
        adv_frame.grid(column=0,row=2)
        # Define To list frame

        #window expansion
        adv_win.rowconfigure(0,weight=1)
        adv_win.columnconfigure(0,weight=1)

        #frame expansion
        adv_frame.rowconfigure(0,weight=1)
        adv_frame.columnconfigure(0,weight=1)

        #install scrollbar to wellbox
        adv_scroll=ttk.Scrollbar(adv_frame,orient=VERTICAL)
        adv_scroll.grid(row=0, column=1, sticky=NS)

        adv_box=Listbox(adv_frame,exportselection=0, listvariable=crv_names, height=height, selectmode='browsw')  #BROWSE(single selection) or MULTIPLE 
        adv_box.grid(row=0,column=0, columnspan=1)
        adv_box['yscrollcommand']=adv_scroll.set

        # Colorize alternating lines of the listbox
        for i in range(0,len(crv_list)-2,2):
            adv_box.itemconfigure(i,background='#f0f0ff')

        adv_scroll.config( command=adv_box.yview) # select one or more wells

        # If curves selected0
        adv_box.selection_clear(0,'end')

        SelectedCurve = Object()        
        SelectedCurve.value = None
        
        #my_instruct='Select curve to be DELETED\button click on list when done\nClose window (X) to ABORT'
        #alert.Message(my_instruct)

        # done
        b_done=Button(adv_win, bg='cyan', text="Delete Curves", command=lambda:adv_quit(adv_win,adv_box,1))
        b_cancel=Button(adv_win, bg='pink', text='Done', command=lambda: adv_quit(adv_win,adv_box,0))

        #place widgets
        b_done.grid(row=4, column=0, padx=10, pady=10,sticky = W)
        b_cancel.grid(row=4, column=1,padx=10,pady=10,sticky= E)

        adv_box.focus_set()
        adv_win.mainloop()
        
        if adv_box.curselection()==() :  #if no curve selected
            adv_win.destroy()
        else:                                                     #if both in and from selected continue
            in_ix=adv_box.curselection()

            input_curve=adv_box.get(in_ix)
            #delete using lasio lib
            las_data.delete_curve(mnemonic=input_curve)   #, ix=None
            adv_win.destroy()

        #save lasfile
        if global_vars.mflag==0:
            dir : Dir = None
            
            if mydir==Dir.In:
                dir = global_vars.project.inDir
            elif mydir==Dir.Out:
                dir = global_vars.project.outDir
            filename=dir+'/'+las_file.filename
            las_data.write(filename, fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)

    global_vars.ui.Root.window.deiconify()

    alert.Message("Scan")   
    global_vars.project.Scan ()
    alert.Message("Updating Project")
    global_vars.ui.Root.Update()  

  
# ----------------------------------------------------------------------------------------------------------
def findWellsWithTopFormationZones( opt):

    global_vars.ui.Root.window.iconify()

    excel.get_zone()
    lst_names= list(global_vars.project.formationZones.keys())
    #get zones and depth interval

    #create toplevel window
    top_win = common.initCommonWindow('', 270, 100)

    #window expansion
    top_win.rowconfigure(0,weight=1)
    top_win.columnconfigure(0,weight=1)

    #define widgets
    if opt==0:
        top_win.title('Find wells with Zone')
        lbl_txt="Select a zone:"

    qlabel=Label(top_win,text=lbl_txt)

    zone_box=ttk.Combobox(top_win,value=lst_names)

    buttonResponses : Object = Object()
    buttonResponses.cancel = False

    # done
    b_done=Button(top_win, bg='cyan', text="Submit", command=lambda: top_win.quit())
    b_cancel=Button(top_win, bg='pink', text='Cancel', command= lambda: (setattr(buttonResponses, 'cancel', True), top_win.quit()) )
    
    #place widgets
    qlabel.grid(row=0, column=0, columnspan=2, sticky=W)
    zone_box.grid(row=1,column=1,sticky = W)

    b_done.grid(row=2, column=0, padx=10, pady=10,sticky = W)
    b_cancel.grid(row=2, column=2,pady=10,sticky= W)

    #----------------- blocking ----------------#
    top_win.mainloop() 

    if buttonResponses.cancel==True:
        top_win.destroy()
        global_vars.ui.Root.window.deiconify()
        return
    
    #find zone in wells and update Well_List
    zone=zone_box.get()
    if zone=='':                #Zone not selected
        top_win.iconify()
        alert.Error("Select first a zone")
        top_win.deiconify()
        global_vars.ui.Root.window.deiconify()
        return
    
    top_win.destroy()
    # Ready to update list
    new_list = WellList()
    for well in global_vars.project.currentWellList.GetWells():
        if well.GetZoneDepths(zone, True) is not None:
            new_list.Add(well)

    if len(new_list)>0:                  #If wells found with zone tops
        global_vars.project.currentWellList=new_list

    global_vars.ui.Root.Update()
    global_vars.ui.Root.window.deiconify()
#-------------------------------------------------------------------------------------------------------------------------------------
def selectWellFromCurrentList():
    '''
    Add to list a well selected from current well list
    '''
    input = prompt.customValuePrompt("Enter a Alias or UWI:")
    well : 'Well' = None
    if input: #if is not empty
        well = global_vars.project.projectWellList.Get(input) #get by uwi
        if well is None:
            well = global_vars.project.projectWellList.GetByAlias(input) #get by alias
            if well is None:
                return alert.Error(f'well uwi/alias "{input}" not found')
            
    listBoxItems = list(global_vars.ui.Root.well_listBox.get(0, "end"))
    listBoxWellIndex = -1
    for index,value in enumerate(listBoxItems):
        if well.uwi in value:
            listBoxWellIndex = index
            break
    
    if listBoxWellIndex == -1:
        global_vars.ui.Root.well_listBox.selection_clear(0,'end')
        return alert.Error(f"Well UWI {well.uwi}({well.alias}) not in list")
    

    global_vars.ui.Root.well_listBox.select_clear(0, "end")
    global_vars.ui.Root.well_listBox.selection_set(index)
    global_vars.ui.Root.well_listBox.see(index)
    global_vars.ui.Root.well_listBox.activate(index)
    global_vars.ui.Root.well_listBox.selection_anchor(index)

def deleteWellFromCurrentList() -> bool:
    alias = prompt.customValuePrompt("Enter Well Alias or UWI to Delete?")
    if alias and str(alias).strip(): #if is not empty
        well = global_vars.project.projectWellList.Get(alias) #get by uwi
        if well is None:
            well = global_vars.project.projectWellList.GetByAlias(alias) #get by alias
            if well is None:
                return alert.Error(f'well alias "{alias}" not found')
        
        # save before changing
        global_vars.project.currentWellList.SaveAs('prev.wnz')
        deleted = global_vars.project.currentWellList.Delete(well.uwi)
        if deleted:
            global_vars.ui.Root.Update() #update view...

        return deleted
    
    return False #not found, not deleted

def createWellListFromCurveAliases():
    curveName = prompt.customListPrompt("Search Wells for Alias of Curve : ", global_vars.project.curveNameTranslator.GetNames())
    if not curveName or not curveName.strip():
        return #no curve selected or cancelled
    
    aliasList = global_vars.project.curveNameTranslator.GetAliases(curveName)
    wells = global_vars.project.projectWellList.GetWellsByCurveNames(aliasList)

    if wells == []:      # if no wells found
        alert.Error(f"No wells with {curveName} in project")
    else:
        #load and save new well list
        global_vars.project.currentWellList.LoadFromWells(wells)
        global_vars.project.currentWellList.SaveAsPrompt()
        #Curve.save_wellist(0)

    global_vars.ui.Root.Update()  #refresh main window
#-----------------------------------------------------------------------------------------------------
def q_Township():
    '''
        Find wells within one or more townpships and save as list
    '''
    if global_vars.project.inDir=='c:/':
        alert.Error("Please, select an input directory in the File menu")
        return

    global_vars.ui.Root.window.iconify()

    global_vars.tmp=[]
    global_vars.tmp.append(0)               #create cancel flag

    #create window
    Q_Twp = common.initCommonWindow(title="Enter NE and SW corners:", width=400, height=300)

    #Create Widgets
    NWtxt="Northwest corner"
    NWlabel=Label(Q_Twp,text=NWtxt)
    Ttxt="Township"
    Rtxt="Range"
    Mtxt="Meridian"
    Wtxt="    W"
    TNlabel=Label(Q_Twp,text=Ttxt)
    varTN=StringVar()
    varTN.set("000")
    TNentry=ttk.Entry(Q_Twp,textvariable=varTN, width=15)

    RNlabel=Label(Q_Twp,text=Rtxt)
    varRN=StringVar()
    varRN.set("000")
    RNentry=ttk.Entry(Q_Twp,textvariable=varRN,width=15)

    NMWlabel=Label(Q_Twp,text=Wtxt)
    MNlabel=Label(Q_Twp,text=Mtxt)
    varMN=StringVar()
    varMN.set("00")
    MNentry=ttk.Entry(Q_Twp,textvariable=varMN,width=5)

    SEtxt="Southeast corner"
    SElabel=Label(Q_Twp,text=SEtxt)
    TSlabel=Label(Q_Twp,text=Ttxt)
    varTS=StringVar()
    varTS.set("000")
    TSentry=ttk.Entry(Q_Twp,textvariable=varTS, width=15)

    RSlabel=Label(Q_Twp,text=Rtxt)
    varRS=StringVar()
    varRS.set("000")
    RSentry=ttk.Entry(Q_Twp,textvariable=varRS, width=15)

    SMWlabel=Label(Q_Twp,text=Wtxt)
    MSlabel=Label(Q_Twp,text=Mtxt)
    varMS=StringVar()
    varMS.set("00")
    MSentry=ttk.Entry(Q_Twp,textvariable=varMS, width=5)

    # done
    b_done=Button(Q_Twp, bg='cyan', text="Submit", command=lambda:T_submit(Q_Twp, varTN.get(), varRN.get(), varMN.get(), varTS.get(), varRS.get(), varMS.get(),1))
    b_cancel=Button(Q_Twp, bg='pink', text='Cancel', command= lambda:T_submit(Q_Twp,0,0,0,0,0,0,0))

    #place widgets
    NWlabel.grid(row=0, column=1, pady=10, sticky=W)
    TNlabel.grid(row=1, column=1, sticky=W)
    TNentry.grid(row=2, column=1, padx=5, pady=10)
    RNlabel.grid(row=1, column=2, padx=5, sticky=W)
    RNentry.grid(row=2, column=2, padx=5, pady=10)
    NMWlabel.grid(row=2, column=3, sticky=E)
    MNlabel.grid(row=1, column=4, sticky=W)
    MNentry.grid(row=2, column=4,pady=10)

    SElabel.grid(row=3, column=1, pady=10, sticky=W)
    TSlabel.grid(row=4, column=1, sticky=W)
    TSentry.grid(row=5, column=1, padx=5, pady=10)
    RSlabel.grid(row=4, column=2, padx=5, sticky=W)
    RSentry.grid(row=5, column=2, padx=5, pady=10)
    SMWlabel.grid(row=5, column=3, sticky=E)
    MSlabel.grid(row=4, column=4, sticky=W)
    MSentry.grid(row=5, column=4,pady=10)

    b_done.grid(row=6, column=2, pady=5,sticky = E)
    b_cancel.grid(row=6, column=4,pady=5,sticky= E)
#-----------------------------------------------------------------------------------------------------
def T_submit(win, TN, RN, MN, TS, RS, MS, opt):
    '''
    Submit the sesults of myQuest including cancel
    opt=0 is cancel  opt=1 Submit
    '''

    #Submit
    if opt==0 or TN=='000'or MN=='00'or TS=='000'or MS=='00':       #clear mwell_box
        opt=0
    else:
        if int(float(TN))!=float(TN) or int(float(RN))!=float(RN) or int(float(MN))!=float(MN) or int(float(TS))!=float(TS) or int(float(RS))!=float(RS) or int(float(MS))!=float(MS):   #if not integers
            alert.Error("Invalid data entered")
            return

        TN=int(TN)
        RN=int(RN)
        MN=int(MN)
        TS=int(TS)
        RS=int(RS)
        MS=int(MS)
        if MN<MS:           #If North Meridian less than South Meridian
            alert.Error("Meridian Mix up")
            return
        if TN<TS or TN<0 or TS<0:           #If North Township less than South Township or negative
            alert.Error("Townships Not valid")
            return
        if RN<RS:           #If North Range greater than South Range
            if MN==MS:      #if within same range then ranges are mixed up
                alert.Error("Range Mix up")
                return
            if RN>30 or RS>30:
                alert.Error("Range Not Valid")
                return

    win.destroy()

    if opt==1:   # Township search
        # save previous well list
        #Curve.save_wellist(2)
        global_vars.project.currentWellList.SaveAs('prev.wnz')

        newWellList : list[str] = []        # create an empty well list
        for well in global_vars.project.currentWellList.list:
            if (
                    MN != MS                 and
                    MN<=int(well[13:14])<=MS and    # if UWI in Meridian range
                    TS<=int(well[7:10])<=TN  and    #If in correct range
                    (
                        RS>int(well[10:12]) or RS<=int(well[10:12])<=RN # if in correct range
                    )
                ):
                    newWellList.append(well)
        
        if newWellList == []:
            return alert.Error('no wells found')
            
        global_vars.project.currentWellList.LoadFromList(newWellList) #update current well list
        global_vars.project.currentWellList.SaveAsPrompt()
        #Curve.save_wellist(0)
        
    global_vars.ui.Root.Update()
    global_vars.ui.Root.window.deiconify()
    return
#------------------------------------------------------------------------------------------------------
def cln_las(filename):
    ''' Clean up an existing las data from a las file in Indir'''
    #load las-data
    filename = global_vars.project.inDir + '/'+ filename
    #las_data
    try:
        las_data = global_vars.LASCache.GetLASDataCopy(filename)

    except FileNotFoundError:
        alert.Error('LAS file could not be found. Please, try again.')
        return None
    except ValueError:
        alert.Error('LAS file could not be opened. Please, try again.')
        return None
    except Exception:
        alert.Error('LAS file could not be read. Please, try again.')
        return None

    mend=len(las_data.curves)-1   #leave depth curve
    idx=1 #skip depth curve
    while idx<mend:    #cycle through curves and del from curves
        #delete curves
        if idx>0:
            crv2=None
            if las_data.curves[idx].mnemonic!='TEMP':
                crv2=program.get_aka(las_data.curves[idx].mnemonic, las_data)
            if (las_data.curves[idx].mnemonic=='BIT' or las_data.curves[idx].mnemonic=='TEMP'):
                if las_data.curves[idx].mnemonic=='BIT':
                    desc=las_data.curves['DEPT'].descr[2:]  #remove numbering
                    las_data.curves['DEPT'].descr=desc
                    desc=las_data.curves['BIT'].descr[3:]
                    las_data.curves['BIT'].descr=desc
                    if crv2!='TEMP' and crv2!='BIT':
                        desc=las_data.curves['TEMP'].descr[3:]
                        las_data.curves['TEMP'].descr=desc
                idx +=1 #Skip curve
            if crv2=='TEMP':
                las_data.curves[idx].mnemonic='TEMP'
                idx +=1 #Skip curve
            else:
                las_data.delete_curve( ix=idx)
                mend -=1
        else:
            idx=1
    return las_data
#----------------------------------------------------------------------------------------------------
def create_cas(path_name):
    '''
    Create a new las or cas data
    '''
    # get las_data from UWI
    try:
        las_data = global_vars.LASCache.GetLASData(path_name)

    except FileNotFoundError:
        alert.Error('LAS file could not be found. Please, try again.')
        return None
    except ValueError:
        alert.Error('LAS file could not be opened. Please, try again.')
        return None
    except Exception:
        alert.Error('LAS file could not be read. Please, try again.')
        return None

    
    lasFile = lasio.LASFile()
        # Get las SERV
    lasFile.version.SERV = 'EUKY'
    #las.version.SERV.descr = 'Eucalyptus Consulting Inc.'
    lasFile.version.SERV = lasio.HeaderItem('SERV', value='EUKY',descr = 'Eucalyptus Consulting Inc.')
    lasFile.well.FLD=las_data.well.FLD
    lasFile.well.LOC=las_data.well.LOC
    lasFile.well.PROV=las_data.well.PROV
    lasFile.well.CNTY=las_data.well.CNTY
    lasFile.well.CTRY=las_data.well.CTRY
    lasFile.well.UWI=las_data.well.UWI
    lasFile.well.NULL.value=-999.25
    lasFile.well.DATE = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    '''
    curDir = os.getcwd()
    os.chdir(Indir)
    filename=path_name[-20:-4] +'.cas'
    las.write(filename, fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
    os.chdir(curDir)
    '''
    return lasFile


#===========================================================================================================
# Tool Module
# ==========================================================================================================
def dshift():
    '''
    graphical shifting of core depth and log depth
    '''

    global_vars.tmp.append(0)

    global_vars.ui.Root.window.iconify()

    crv_list=[]
    fcrvs=[]                            #curves in dpt plot fills

    nocurves=['Dept','Temp','Bit']
    crv_list=program.com_crvs(nocurves,crv_list,1)

    # Cycle through Well_List and cq if a casfile exists
    for well in global_vars.project.currentWellList.GetWells():

        #get core data
        cas_data = well.GetLASData(Dir.In, '.cas')
        if cas_data is None: #no .cas file
            continue

        las_data = well.GetLASData(Dir.In)
        if las_data is None:
            continue

        global_vars.core_df = cas_data.df()
        global_vars.las_df = las_data.df()

        #get depth shift for all cores
        dptshift=str(cas_data.params.CSH.value)
        # if dptshift != '':
        #    dptshift.split(',')                #If multiple cores then split shifts bu successive core
        # Check for graphical shift or numerical

        ls_start=cas_data.well.STRT.value-15      #start 15m above core interval
        #check whether valid in lasfile
        if ls_start<las_data.well.STRT.value:
            ls_start=las_data.well.STRT.value
        ls_stop=cas_data.well.STOP.value+15       #start 15m below core interval
        #check whether valid in lasfile
        if ls_stop>las_data.well.STOP.value:
            ls_start=las_data.well.STOP.value

        zoneDepths= ZoneDepths(top=ls_start, base=ls_stop, name='WELL')

        #Make log curve list to be displayed
        log_list=['GR','DPSS','DPHI','RHOB','DT','DRHO']

        #Make core cure list to be displayed
        core_list=['FACIES','MAVCL','MAPHIT','CPOR']

        #find akas in las file  not needed in crvdesc list
        #load Alias settings with previous selected path or default path
        fnd_fl=[0,0,0,0,0,0] #found list

        crv1=log_list[0]
        crv2=log_list[1]
        crv3=log_list[2]
        crv4=log_list[3]
        crv5=log_list[4]
        crv6=log_list[5]

        # Find alias curve names
        c1,found_key= main.find_aka(crv1, crv_list, 1, las_data, 0, zoneDepths)
        if found_key==1:
            fnd_fl[0]=1
            c1.name=crv1
        c2,found_key= main.find_aka(crv2,crv_list, 2, las_data, 0, zoneDepths)
        if found_key==2:
            fnd_fl[1]=2
            c2.name=crv2
        c3,found_key= main.find_aka(crv3,crv_list, 3, las_data, 0, zoneDepths)
        if found_key==3:
            fnd_fl[2]=3
            c3.name=crv3
        c4,found_key= main.find_aka(crv4,crv_list, 4, las_data, 0, zoneDepths)
        if found_key==4:
            fnd_fl[3]=4
            c4.name=crv4
        c5,found_key= main.find_aka(crv5,crv_list, 5, las_data, 0, zoneDepths)
        if found_key==5:
            fnd_fl[4]=5
            c5.name=crv5
        c6,found_key= main.find_aka(crv6,crv_list, 6, las_data, 0, zoneDepths)
        if found_key==6:
            fnd_fl[5]=6
            c6.name=crv6

        if 1 not in fnd_fl:                   # GR was NOT found
            alert.Error(f"{crv1} was not in {well}")
            return                                  # go back to graphs and start over
        if 2 not in fnd_fl:                       # PHISS nor PHILS were found
            #c_Error(f"{crv2} and/or {crv3} were not in {well}, will try to create {crv2} using {crv4}")
            if 4 not in fnd_fl:                   # RHOB was NOT found
                alert.Error(f"{crv4} was not in {well}, will try {crv5}")
                if 5 not in fnd_fl:               # DT was NOT found
                    alert.Error(f"{crv5} was not in {well}, can not create a log porosity curve - Next well")    # DT was NOT found
                    main.show_las(well)
                    continue
                else:
                    if 3 not in fnd_fl:
                        #first estimate VCL
                        if c1.empty==False:
                            GRsh=c1.quantile(float(0.80))
                            GRcl=c1.quantile(float(0.10))
                            GRind=(c1-GRcl)/(GRsh-GRcl)

                        #calculate PHIS (sonic)
                        #PHIS=(DT-DTMA)/(DTFL-DTMA)
                        c2=(c5-182)/438-GRind
                        c2.name='PHIS'
                        fnd_fl[4]=5
                    else:
                        c2=c3.copy()
            else:
                #calculate PHISS
                #Set all nulls to NaN
                #las_df.replace(mynull,np.nan)   #does this affect c1 - c5???
                #create c2 with dataframe

                #DPSS = (RHOMA - RHOB)(RHOMA-RHOFL)
                c2= (2.65-c4)/1.65
                c2.name='DPSS'
                fnd_fl[1]=2
        if 6 not in fnd_fl:      #No DRHO
            alert.Error(f"{crv6} was not in {well}")
        #cdescrvs is list of all core data curves
        #Add core curves: MAVCL, CPOR, MAPHIT
        c7=global_vars.core_df[core_list[1]]        #MAVCL
        c8=global_vars.core_df[core_list[2]]        #MAPHIT
        c9=global_vars.core_df[core_list[3]]       #CPOR

        c1.replace(-999.25,np.nan,inplace=True)
        c2.replace(-999.25,np.nan,inplace=True)
        c3.replace(-999.25,np.nan,inplace=True)
        c4.replace(-999.25,np.nan,inplace=True)
        c5.replace(-999.25,np.nan,inplace=True)
        c6.replace(-999.25,np.nan,inplace=True)
        c7.replace(-999.25,np.nan,inplace=True)
        c8.replace(-999.25,np.nan,inplace=True)
        c9.replace(-999.25,np.nan,inplace=True)

        #GR = c1, DPSS = c2, DPHI = c3, RHOB = c4, DT = c5, DRHO = c6
        #MAVCl = c7, MAPHIT= c8 c6
        curvs=[c1, c7, c2, c8, c9, c6]
        '''
        Defined in depth plot
        color_list=['green', 'palegreen','red','lightcoral','olive','blue','cyan' ,'magenta','purple','gold','lightgrey', 'black', 'darkblue', 'lightblue', 'gray','yellow','orange']
        line_list=['dotted','solid','dashed','dashdot',(0,(3,1,1,1)),(0,(4, 2, 1, 2)),(0,(3,1,1,1,1,1))]
        tick_list=[[0, 50, 100, 150, 200],[0.45, 0.3, 0.15, 0, -0.15],[0.60, 0.45, 0.30, 0.15, 0],[0.0, 0.25, 0.5, 0.75, 1.0],[1.95, 2.2, 2.45, 2.7, 2.95],[500,400,300,200,100],[-0.15,0.15,0.45,0.75,1.05],[1000,750,500,250,0.0],[0.1,1,10,100,1000],[0.2,2,20,200,2000],[0, 0.15, 0.30, 0.45, 0.60],
        [-0.75,-0.50,-0.25,0.0,0.25],[0,5,10,15,20],[300,200,100,0,-100],[150,200,250,350,400],[0,0.5,1,1.5,2],[1000,100,10,1,0.1],[2000,200,20,2,0.2],[1.65, 1.90, 2.15, 2.4, 2.65],[-2,0,2,4,6]]
        scale (0=default or 'lin', 1='log')
        marker_list=['o','O','s','d','D','x','X','h','+','*','^','']

        props[color, linestyle, ticks, scale , marker, track]
        '''
        #
        props=[[0,1,0,0,11,1,1,"","","","","",""],[7,2,3,0,11,1,1,"","","","","",""],[2,1,1,0,11,2,1,"","","","","",""],[5,2,1,0,11,2,1,"","","","","",""],[11,0,1,0,0,2,1,"","","","","",""],[4,3,6,0,11,2,1,"","","","","",""]]

        # create depth plots 2 tracks GR_Facies Track Porosity track Plot type = 1
        global_vars.cr_shft=[]
        global_vars.tmp[0]=0
        
        depthPlot = DepthPlot()
        depthPlot.depthPlot(f"{well.uwi}({well.alias})", curvs, fcrvs, props, 2, DepthPlot.DepthPlotType.DepthShift, well.formations, zoneDepths)

        '''
        yn=prompt.yesno("Continue with other wells(Yes) or return to Main(No)")
        if yn==False:   #if No return to main
            os.chdir(curDir)
            plt.close()
            return
        '''
        pyplot.close()

        while len(global_vars.cr_shft)>1:
            global_vars.cr_shft.pop(0)
        global_vars.cr_shft.append(0)

        #update casfile for depthshift
        '''
        shift_str=''
        for x in cr_shft:
            shift_str=shift_str+str(round(x,4))+','

        yn=prompt.yesno("Save coreshift (Yes) or skip well (No)")
        if yn==False:   #if No return to main
            continue
        '''

        dptshift = str(round(global_vars.cr_shft[0],2))
        #When multiple core shifts recorded
        #for cr in range(1,len(cr_shft))
        #   dptshift = dptshift +','+str(round(cr_shft[cr],2))
        cas_data.params.CSH.value= float(dptshift)
        # Now save casfile
        las.save_cas(well.uwi + ".cas", cas_data, Dir.In)

    #Done with files
    global_vars.ui.Root.window.deiconify()
#------------------------------------------------------------------------------------------------------
def nshift():
    '''
    Add value of core shift to casfile - no graphics
    '''
    count : int = 0
    for well in global_vars.project.currentWellList.GetWells():

        #get core data
        cas_data = well.GetLASData(Dir.In, '.cas')
        if cas_data is None: #no .cas file
            continue

        count += 1

        myquestion= f"For {well.uwi}({well.alias}) enter the depth shift (m) (Down = + and Up = -)"
        dptshift=prompt.simpleQuestion(myquestion)
        if dptshift=='':       #if empty return
            alert.Error("No amount of shift entered - next well")
            continue

        cas_data.params.CSH.value= float(dptshift)

        # Now save casfile
        las.save_cas(well.uwi+".cas", cas_data, Dir.In)
    
    #if no '.cas' files return
    if count == 0:
        alert.Error(f"No .cas / core data found in {global_vars.project.inDir}")
        return
#------------------------------------------------------------------------------------------------------
def crvshift():
    '''
    Shift selected curve down las_df (i.e. shift up or down the dpt index) - One well at a time
    get selection from global mwell_box
    '''
    selection=global_vars.ui.Root.well_listBox.curselection()            #select ONE curve from Mainmodule well list
    if len(selection)!=1:
        alert.Error("select ONE well for which curve(s) has to be shifted")
        return
    
    uwi = ''
    item = str(global_vars.ui.Root.well_listBox.get(selection))
    parts = item.split(':', 2)
    if len(parts) > 1:
        uwi = parts[1]
    else:
        uwi = parts[0]

    well = global_vars.project.projectWellList.Get(uwi)

    las_data = well.GetLASData(Dir.In)
    if las_data is None:
        return alert.Error(ErrorMessage.FAILED_LOAD_LAS, [Dir.In, well])
    
    las_df=las_data.df()                #Indir las_df data frame

    #create list of las_data curves
    crv_list=[crv.mnemonic for crv in las_data.curves]
    del crv_list[0]     #delete depth curve from list

    #select curve from toplevel window
    # Define window height
    mheight=len(crv_list)
    if mheight>7:                   #box height beyond frame height
        mheight=7

    #Open top level window
    slcrv_win = common.initCommonWindow(title='', width=255, height=int(300*(mheight+1)/12))

    slcrv_frame=LabelFrame(slcrv_win, pady=5, text="Left Double Click when done Select Curve: ")
    slcrv_frame.grid(column=0,row=0,padx=5,sticky=NS)

    #window expansion
   # slcrv_win.rowconfigure(0,weight=1)
   # slcrv_win.columnconfigure(0,weight=1)

    #frame expansion
    #slcrv_frame.rowconfigure(0,weight=1)
    #slcrv_frame.columnconfigure(0,weight=1)

    # Create selectable well listbox gr_win
    crv_names=StringVar(value=crv_list)

    #install scrollbar to wellbox
    slcrv_scroll=ttk.Scrollbar(slcrv_frame,orient=tkinter.VERTICAL)
    slcrv_scroll.pack(side='right', fill='y')

    slcrv_box=Listbox(slcrv_frame,exportselection=0, listvariable=crv_names, height=mheight, selectmode="multiple")
    slcrv_box.pack()
    slcrv_box['yscrollcommand']=slcrv_scroll.set
    slcrv_scroll.config( command=slcrv_box.yview) # select one or more wells

    # If curves selected
    slcrv_box.selection_clear(0,'end')

    slcrv_box.bind("<Double-1>", lambda e: slcrv_win.quit())

    slcrv_box.focus_set()
    slcrv_win.mainloop()

    if slcrv_box.curselection()==() :  #if no curve selected
        return
    else:                                                       #if both in and from selected continue
        in_ix=slcrv_box.curselection()
        sft_crv=[]                                              #list of curves selected to be shifted
        for idx in in_ix:
            sft_crv.append(slcrv_box.get(idx))

    slcrv_win.destroy()

    #get amount of shift
    amnt=prompt.simpleQuestion("Enter Amount of depth shift in 0.1m increments. (Down = + and Up = -)")
    if amnt=='':        #If no amount then return to main
        return
    sft=int(float(amnt)*10)
    if sft>0:       #shift down
        msft=sft-1
    if sft<0:       #shift up
        msft=sft+1
    #get curves
    mydat = well.GetLASData(Dir.Out)

    # if no las file in Outdir yet
    filename = well.uwi + ".las"
    if mydat==[]:
        #create new las
        yn=prompt.yesno('Create New file in ' + global_vars.project.outDir)
        if yn==False:
            return
        mydat=cln_las(filename)
       #mydat=create_cas(path_name)  #create las headers with empty crv_df

    # cycle through curves in curves to be shifted
    crv_df=pd.DataFrame(None) #placeholder
    #create empty las_df column
    las_df['EMPTY']=np.nan  #create in Indir las_df empty new curve
    for mcrv in sft_crv:
        ncr=mcrv+'_SFT'   # create new curve name with '-sft'
        crv_df[ncr]=las_df['EMPTY'].copy(deep=True)
        mval=las_df[mcrv].tolist()
        nwval=crv_df[ncr].to_list()
        if sft<0:           #Shift up
            nwval[:msft]=mval[-msft:]  #.copy()
        elif sft>0:           #Shift down
            nwval[msft:]=mval[:-msft]
        #else no shift
        crv_df[ncr]=nwval
        mydat.curves['DEPT'].descr[2:]

    # update las_dat prior to saving
    #save output dir
    mynull=round(las_data.well.NULL.value,2)
    crv_df.fillna(mynull,inplace=True)
    mydat.set_data(crv_df)    #update las_data
    mydat.curves['DEPT'].descr='DEPTH'
    mydat.curves['DEPT'].value = '00 001 00 00'
    for mcrv in sft_crv:  #update curve description
        ncr=mcrv+'_SFT'   # create new curve name with '-sft'
        n_desc= ncr + ' Shifted ' + amnt + 'm.'
        mydat.curves[ncr].descr=n_desc

    # Now save
    mydat.write(global_vars.project.outDir+'/'+filename, fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
