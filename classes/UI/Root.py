
import os
import tkinter
from re import X
from tkinter import (BOTH, CENTER, DISABLED, E, END, EW, MULTIPLE, NO, NORMAL, NS,
                     NSEW, NW, VERTICAL, YES, Button, Event, Frame, Label,
                     Listbox, Menu, PhotoImage, Scrollbar, StringVar, Tk, W,
                     ttk, Variable)
from tkinter import messagebox
import numpy as np
from typing import TYPE_CHECKING
from classes.LASConverter import LASConverter

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import classes.Normalizer
import Curve
import global_vars
from classes.Project import Project
from classes.Command import Command
from classes.MultiMineral import MultiMineral
from classes.Project.WellList import WellList
from classes.Script import Script
from defs import alert, common, excel, main, prompt, tools
from enumerables import Dir

if TYPE_CHECKING:
    from classes.Project.Well import Well


class Root:
    def __init__(self) -> None:
        self.window : Tk = Tk()
        '''root window'''

        self.window.option_add('*tearOff', False)

        self.window.wm_protocol("WM_DEICONIFY", self.Check_Disabled)
        self.window.bind("<FocusIn>", self.Check_Disabled)


       
        self.status : StringVar = StringVar()  
        '''Status bar - kind of -- linked to statusLabel; use to set status'''

        self.statusLabel : Label = None

             
        self.status.set('Waiting for directories')

        self.menuBar = Menu(self.window)
        '''top menu bar'''

        #main menus
        self.menu_file = Menu(self.menuBar)
        self.menu_las = Menu(self.menuBar)
        self.menu_lith = Menu(self.menuBar)
        self.menu_tool = Menu(self.menuBar)
        self.menu_graph = Menu(self.menuBar)
        self.menu_script = Menu(self.menuBar)
        self.menu_help = Menu(self.menuBar)

        ws = self.window.winfo_screenwidth()
        hs = self.window.winfo_screenheight()
        app_wdt = 800 # loop through Fm data rows
        app_hgt = 600
        x=ws/2 - app_wdt/2
        y=hs/2 - app_hgt/2
        self.window.geometry(f"{app_wdt}x{app_hgt}+{int(x)}+{int(y)}")

        #Window title and icon
        #version = Remake.MajorRevision.MinorRevision
        self.window.title('Curve ' + global_vars.SoftwareVersion)

        #.ico does not work on linux; tkinter is broken
        #globals.rootWindow.iconbitmap(globals.rootDir+'/Euc.ico')  # File in path (run directory)
        self.window.iconphoto(False, PhotoImage(file=global_vars.rootDir+'/Euc.png'))
        # expandable screen
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        self.window.attributes('-topmost',3)

        # Create menus for Root
        self.window['menu'] = self.menuBar
        #root.attributes('-topmost', 1)

        #region menu
        # Menubar
        self.menuBar.add_cascade(menu=self.menu_file, label='File')
        self.menuBar.add_cascade(menu=self.menu_las, label='LAS converter')
        self.menuBar.add_cascade(menu=self.menu_lith, label='Lithology')
        self.menuBar.add_cascade(menu=self.menu_tool, label='Tools')
        self.menuBar.add_command(label='Graphing', command=lambda: global_vars.ui.Graphing.Show())
        self.menuBar.add_cascade(menu=self.menu_script, label='Scripts')
        self.menuBar.add_command(label='Help', command=main.c_help)

        #Project subcommands
        menu_proj = Menu(self.menu_file)
        self.menu_file.add_cascade(menu=menu_proj, label='Project')
        menu_proj.add_command(label="Create Project", command=lambda: Curve.c_project())
        menu_proj.add_command(label="Save Project", command=lambda: global_vars.project.SaveInit())
        menu_proj.add_command(label="Load Project", command=lambda: Project.newLoadProjectPrompt())
        menu_proj.add_command(label="Update Project", command = lambda:global_vars.project.Scan())

        # Directory subcommands
        menu_dir = Menu(self.menu_file)
        self.menu_file.add_cascade(menu=menu_dir, label='Directories')
        menu_dir.add_command(label="Input Directory", command=prompt.InputDir)
        menu_dir.add_command(label="Output Directory", command=prompt.OutputDir)
        menu_dir.add_command(label="Raw Directory", command=prompt.RawDir)
        menu_dir.add_command(label="Core (raw) data Directory", command=prompt.CoreDir)
        menu_dir.add_command(label="Client Directory", command=prompt.ClientDir)
        menu_dir.add_command(label="List All Default Directories", command=Curve.c_ListDir)
        menu_dir.add_separator()
        menu_dir.add_command(label="Input File", command=prompt.InputFile)
        #menu_dir.add_command(label="Output File", command=c_OutputF)

        # File menu - commands
        self.menu_file.add_separator()
        self.menu_file.add_command( label='All wells',command= lambda: self.AllWells(),state=DISABLED)
        self.menu_file.add_command( label='Save Well list',command= lambda: global_vars.project.currentWellList.SaveAsPrompt()) #


        self.menu_file.add_command( label='Load Well list',command=lambda: (global_vars.project.loadWellListPrompt(), self.Update()))
        self.menu_file.add_separator()
        self.menu_file.add_command(label='Exit', command=Curve.c_Exit)

        menu_load=Menu(self.menu_lith)
        self.menu_lith.add_cascade(menu=menu_load, label='Load core data')
        self.menu_lith.add_command(label="Define Zones and AKAs", command=Curve.c_zones)

        # LAS menu - commands
        self.menu_las.add_command(
            label="Choose Mnemonic File instead of Default",        command=lambda: global_vars.project.PromptLoadCurveParameters())
        self.menu_las.add_command(
            label="Choose Alias File instead of Default",           command=lambda: global_vars.project.PromptLoadCurveNameTranslatorFile())
        self.menu_las.add_command(label="Open and examine a LAS file",   command=lambda: main.show_las(0))
        self.menu_las.add_separator()
        # Las Conversion Menu
        self.menu_las.add_command(label='Standard Las Conversion IHS source-like files',        command=lambda: LASConverter.New())
        self.menu_las.add_command(label='Standard Las Conversion Petro Ninja-like files')#,        command=lambda: LASConverter.New())
        self.menu_las.add_command(label='Add curves to selected InDir Las Files')#     Insert digitizer services curves to well las

        # tool sub menus
        self.menu_tool.add_command(label="Find Well using UWI or Alias", command=lambda: tools.selectWellFromCurrentList())
        self.menu_tool.add_command(label="Find Wells with tops", command=lambda: tools.findWellsWithTopFormationZones(0))

        self.menu_tool.add_command(label="Previous Well list", command=lambda: global_vars.project.loadPreviousWellList())
        self.menu_tool.add_command(label="Add selected well to list", command=self.add_tolist)
        self.menu_tool.add_command(label="Delete well from selected list", command=tools.deleteWellFromCurrentList)
        self.menu_tool.add_command(label="Delete any curve from a LAS file", command=lambda: tools.del_any_crv())
        self.menu_tool.add_separator()
        menu_adfile= Menu(self.menu_tool)
        self.menu_tool.add_cascade(menu=menu_adfile,label="Advanced Curve Operations for project")
        self.menu_tool.add_separator()
        self.menu_tool.add_command(label="Rename selected well alias", command=self.renameWellAliasPrompt)
        self.menu_tool.add_separator()
        self.menu_tool.add_command(label="Create well list by Township", command=tools.q_Township)
        self.menu_tool.add_command(label="Create well list with Alias curve", command=tools.createWellListFromCurveAliases)
        self.menu_tool.add_separator()
        self.menu_tool.add_command(label="Rename curves using aliases", command=lambda: tools.copy_in_to(4))
        self.menu_tool.add_command(label="Copy curves from IN directory to OUT directory", command=lambda: tools.copy_in_to(1))
        self.menu_tool.add_command(label="Copy curves from OUT directory to IN directory", command=lambda: tools.copy_in_to(5))
        self.menu_tool.add_command(label="Copy curves from OUT directory to CLIENT directory", command=lambda: tools.copy_in_to(2))
        self.menu_tool.add_command(label="Copy curves from IN directory to CLIENT directory", command=lambda: tools.copy_in_to(3))

        self.menu_tool.add_separator()
        self.menu_tool.add_command(label="Normalize", command=lambda: classes.Normalizer.Normalizer.newNormalize())  #classes.Normalizer.Normalizer.newNormalize()
        menu_sft=Menu(self.menu_tool)
        self.menu_tool.add_cascade(menu=menu_sft, label='Depth Shifting')
        menu_sft.add_command(label="Graphic Core Shift", command=tools.dshift)
        menu_sft.add_command(label="Numeric Core Shift", command=tools.nshift)
        menu_sft.add_command(label="Curve Shift", command=tools.crvshift)

        #submenu for advanced file operations menu_adfile
        menu_adfile.add_command(label="Create New Curve", command=lambda: tools.advance_crv(1))
        menu_adfile.add_command(label="rename Curve", command=lambda: tools.advance_crv(2))
        menu_adfile.add_command(label="Delete Curve", command=lambda: tools.advance_crv(3))

        # Menu Lithology loading Coredescription, Thin Section and Core analysis   CREATE dfcore and save it
        menu_load.add_command(label="Core Description", command=Curve.ld_c_des)
        #menu_load.add_command(label="Load Thin Section Summary", command=ld_c_ts, state=DISABLED)
        menu_load.add_command(label="Core Analysis", command=Curve.ld_c_an)

        # script menu - commands
        menu_dscripts= Menu(self.menu_script)
        self.menu_script.add_cascade(menu=menu_dscripts, label='Choose and run a Curve Script')
        self.menu_script.add_command(label="Create or run a Script", command= Command.newCommand)
        self.menu_script.add_separator()
        self.menu_script.add_command(label="Set Multimineral Settings", command=MultiMineral.newAnalysis)
        self.menu_script.add_separator()
        self.menu_script.add_command(label="Show or edit Formation names and AKAs", command=Curve.c_zones)
        self.menu_script.add_command(label="Show or edit parameter list", command=lambda: Curve.c_zones(1))

        #script submenus
        menu_dscripts.add_command(label="Vclay - Gamma Ray", command=lambda: Script.newVClayGammaRayScript())
        menu_dscripts.add_command(label="Vclay - Neutron-Density", command=lambda: Script.newVClayNeutronDensityScript())
        menu_dscripts.add_separator()
        menu_dscripts.add_command(label="Porosity", command=lambda: Script.newPorosityScript())
        menu_dscripts.add_command(label="Water Saturation", command=lambda:Script.newWaterSaturationScript())
        menu_dscripts.add_command(label="Re-iterate Simandoux and Dual Water Saturation", command=lambda:Script.newRITWaterSaturationScript())

        menu_dscripts.add_command(label="Permeability", command=lambda: Script.newPermeabilityScript())
        menu_dscripts.add_separator()
        menu_dscripts.add_command(label="Facies", command=lambda: Script.newFaciesScript())

        #endregion menu

        self.statusLabel = Label(self.window, textvariable=self.status, bd=2, relief='sunken', width=self.window.winfo_width(), anchor=W)
        self.statusLabel.grid(row=3, column=0, columnspan=3)
        self.statusLabel.columnconfigure(0,weight=1)

        # ============================================================================================
        # Data Tabs for root
        # ----------------------------------------------------------------------------------------------------
        self.c_mylabel = Label(self.window, text='')
        self.c_mylabel.grid(column=1, row=1, sticky=EW)
        
        def updateLabel(event : Event):
            self.c_mylabel.config(text=event.state)

        self.window.bind("<<updateLabel>>", updateLabel)
        # ====================================================================================================

        
        #region well list box        
        self.well_frame=Frame(self.window)
        '''well listbox frame'''

        self.well_frame.grid(column=0,row=0, sticky=NW)
 
        self.well_scrollBar : Scrollbar = Scrollbar(self.well_frame,orient=VERTICAL)
        self.well_scrollBar.pack(side='right',fill='y')
        self.well_stringVar : StringVar = StringVar()

        self.well_listBox : Listbox = Listbox(self.well_frame,listvariable=self.well_stringVar, yscrollcommand=self.well_scrollBar.set)
        self.well_listBox.columnconfigure([0,1],weight=1)
        self.well_listBox.config(selectmode=MULTIPLE)   # select one or more wells

         # If wells selected
        self.window.protocol("WM_DELETE_WINDOW", lambda:  Curve.c_Exit())
        self.well_listBox.bind('<Button-3>', lambda event: self.view_well(event))   # Show selected well tabs
        self.well_listBox.bind('<Double-1>', lambda e: self.final_wells())  #click double right mouse button
        #endregion well list box

        #region tabs
        self.tabs : ttk.Notebook = None
        self.formationTab : Frame = None
        self.logTab : Frame = None
        self.calcLogTab : Frame = None
        self.coreTab : Frame = None
        #endregion tabs


    def Check_Disabled(self, event):
        ''' force minimize if not logged in '''

        if not global_vars.login.loggedIn:
            self.window.iconify()


    def Show(self):
        '''is blocking'''
        self.Update()
        global_vars.running = True
        while global_vars.running:
            self.window.update_idletasks()
            self.window.update()
            if not global_vars.login.loggedIn:
                global_vars.login.login_window()

    def Update(self):
        #update well_well_listbox and title, check if unsaved changes. 

        #get rid off old tabs
        if self.tabs!=None:
            self.tabs.destroy()

        projectName : str = ''
        if global_vars.project != None:
            unsavedMarker : str = ''
            projectName = global_vars.project.name
            if global_vars.project.unsavedSettings:
                unsavedMarker = u"\u02DF" #unicode superscript */x
            
            projectName = f"{projectName}{unsavedMarker} - "
            
        self.window.title(f"{projectName}Curve {global_vars.SoftwareVersion}")

        self.window.rowconfigure(0, weight=1)

        # Create selectable well listbox gr_win
        #clear listbox
        self.well_listBox.delete(0, END)  #clear listbox

        maxWellNameLen = 0
        for well in global_vars.project.currentWellList.GetWells():
                item = well.alias + ': ' + well.uwi
                self.well_listBox.insert(END,item)
                if len(item) > maxWellNameLen:
                    maxWellNameLen = len(item)

        self.well_listBox.config(height=self.well_listBox.size(), width=maxWellNameLen+1) #update height
        self.well_listBox.pack(fill="y",expand=True)
        #mwell_box.select_set(wn)
        self.well_scrollBar.config(command=self.well_listBox.yview)

        # Colorize alternating lines of the listbox
        tlen=self.well_listBox.size()
        for i in range(0,tlen,2):
                self.well_listBox.itemconfigure(i,background='#f0f0ff')

        self.menu_file.entryconfigure('All wells', state=NORMAL)
        main.stat_update('dummy',6)


    def AllWells(self):
        '''saves currentWellList in prev and resets the currentWellList to show all project wells '''
        global_vars.project.currentWellList.SaveAs('prev.wnz')
        global_vars.project.resetWellList()
        self.Update()
        global_vars.project.Scan()

    def view_well(self, event : tkinter.Event):
        '''
        open selected well in tabs
        '''
        #global_vars.currentWell = None
        #global_vars.current_well=0          #Reset Cur_Well
        self.well_listBox.selection_clear(0,END)
        self.well_listBox.selection_set(self.well_listBox.nearest(event.y))
        self.well_listBox.activate(self.well_listBox.nearest(event.y))

        selection = self.well_listBox.curselection()
        if selection:
            item = self.well_listBox.get(selection)
            parts = item.split(':', 2)
            if len(parts) > 1:
                uwi = parts[1]
                well = global_vars.project.projectWellList.Get(uwi)
                if well is not None:
                    if global_vars.currentWell!=None and global_vars.currentWell!=well:
                        #New well selected close c_tabs
                        self.tabs.destroy()
                    global_vars.currentWell = well
                    self.well_listBox.selection_set(selection[0])
                    
        else:
            return

        self.CreateTabs()

    # Updates well list for selection
    def final_wells(self):
        ''' sets the well list to be only the selected wells'''

        self.tabs.destroy()

        select_list = self.well_listBox.curselection()
        if len(select_list)==0:  # if no selection
            return
        
        global_vars.project.currentWellList.SaveAs('prev.wnz')
        
        global_vars.project.currentWellList = WellList()
        for i in self.well_listBox.curselection():
            parts = str(self.well_listBox.get(i)).split(':',2)
            uwi = parts[1]
            global_vars.project.currentWellList.Add(uwi) 

        global_vars.currentWell = global_vars.project.currentWellList.GetWell(0) #set to first well in list

        # Refresh list box variable list
        self.Update()
        global_vars.project.Scan()
    #------------------------------------------------------------------------------------------------------------------------------------------------------
    def changeCurveName(self, my_treelc, event, well : 'Well'):
        '''
        Change Name of curve in tab
        '''

        row=my_treelc.focus()
        #Get aka of curve from values on selected line
        values=my_treelc.item(row,'values')
        if values=='':
            return
        curveName=values[0]
        #small toplevel to get changed name
        ch_win = common.initCommonWindow(title='Change Curve Name', width=350, height=100, topMost = 2 )

        # get project name
        P_label0=Label(ch_win,text="Enter New Curve Name:")
        var1=StringVar()
        var1.set(curveName)
        P_entry=ttk.Entry(ch_win,textvariable=var1)

        #place widgets
        P_entry.grid(row=1,column=0, pady=5)
        P_label0.grid(row=0, column=0,columnspan=2, pady=5,sticky=W)

        # done
        b_done=Button(ch_win, bg='cyan', text="Submit", command=lambda: ch_win.quit())
        b_cancel=Button(ch_win, bg='pink', text='Cancel', command= lambda: (var1.set(''), ch_win.quit()))

        b_done.grid(row=8,column=0, padx=10,pady=10,sticky=W)
        b_cancel.grid(row=8,column=0,padx=10,pady=10,sticky=E)

        ch_win.mainloop()
        #Update treeline
        myvalues=list(values)
        newCurveName = var1.get().strip().upper()
        if curveName == newCurveName or not newCurveName: #empty or unchanged
            ch_win.destroy()
            return
        
        las_data = well.GetLASData(Dir.In)
        #Update las_data
        changed = False
        for crv in las_data.curves:
            if curveName==crv.mnemonic:   #When old las file line found
                crv.mnemonic=newCurveName
                changed = True
                break

        if changed: #only write if changes are made
            las_data.write(global_vars.project.inDir + '/' + global_vars.currentWell.uwi+".las", fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
            global_vars.currentWell.ScanWellFiles() #update curves in project object

            #update tree row
            myvalues[0] = newCurveName
            my_treelc.item(row,text="",values=myvalues)

        #done
        ch_win.destroy()
        self.Update()
        global_vars.project.Scan()
    #=====================================================================================================
    def add_tolist(self):
        '''
        Add wellbox selection to a list
        '''
        self.window.iconify()

        #get list of selected wells
        mselect=self.well_listBox.curselection()
        if len(mselect)==0:
            return alert.Error("Please select a well to add first")
        
        if not global_vars.project.loadWellListPrompt():
            return False
        
        for i in mselect:
            item = str(self.well_listBox.get(i))
            parts = item.split(':', 2)
            if len(parts) > 1:
                uwi = parts[1]
                well = global_vars.project.projectWellList.Get(uwi)
                if well is not None:
                    global_vars.project.currentWellList.Add(well)

        self.window.deiconify()
        self.Update()
        global_vars.project.Scan()
    #------------------------------------------------------------------------------------------------------------------
    def renameWellAliasPrompt(self):
        #global_vars.rootWindow.iconify()

        #get list of selected wells
        mselect=self.well_listBox.curselection()
        if len(mselect)==0:
            return alert.Error("Please select a well to add first")
        
        if len(mselect) != 1:
            return alert.Error("Please only seelect one well to rename")
        
        i = mselect[0]
        item = str(self.well_listBox.get(i))
        parts = item.split(':', 2)
        if len(parts) > 1:
            uwi = parts[1]
            well = global_vars.project.projectWellList.Get(uwi)
            newAlias = prompt.customValuePrompt(f'new well alias for {well.uwi}({well.alias})', well.alias)
            if newAlias and newAlias.strip(): #if not empty
                newAlias = common.cleanWellAlias(newAlias)
                if well.alias == newAlias: #no change
                    return

                if newAlias:
                    aliasCheck = global_vars.project.projectWellList.GetByAlias(newAlias)
                    if aliasCheck is None: #check if alias is already in use
                        well.alias = newAlias
                    else:
                        alert.Error(f"Well alias '{newAlias}' is already being used by {aliasCheck.uwi}")
                #global_vars.project.projectWellList.Save() #save alias changes to pwl file

        #global_vars.rootWindow.deiconify()
        self.Update()
        global_vars.project.Scan()


    #region tabs
    def CreateTabs(self):
        '''
        Fill in the Formation, Log Curve and Core data tabs
        '''
        global_vars.perfTest.Start("c_tabs")
        #global_vars.project.Scan()

        ws = self.window.winfo_width()
        hs = self.window.winfo_height()

  
        self.tabs = ttk.Notebook(self.window)
        self.tabs.grid(column=2,row=0,sticky=NSEW)
        self.tabs.columnconfigure(2,weight=1)
        #c_tab.rowconfigure(0,weight=1)

        # Formation tab
        self.formationTab = Frame(self.tabs, bg='#d7ffff')
        self.formationTab.grid(column=0, row=0)
        #fm_frame.columnconfigure(0,weight=1)
        #fm_frame.rowconfigure(0,weight=1)

        # Log tab
        self.logTab=Frame(self.tabs,width=ws*0.8, height=0.7*hs, bg='#e8e8e8')
        self.logTab.grid(column=0, row=0)
        #lc_frame.columnconfigure(0,weight=1)
        #lc_frame.rowconfigure(0,weight=1)

        # New Log tab
        self.calcLogTab=Frame(self.tabs,width=ws*0.8, height=0.7*hs, bg='#e8e8e8')
        self.calcLogTab.grid(column=0, row=0)
        #lc_frame.columnconfigure(0,weight=1)
        #lc_frame.rowconfigure(0,weight=1)

        # Core tab
        self.coreTab=Frame(self.tabs,width=ws*0.8, height=0.6*hs, bg='#fff4df')
        self.coreTab.grid(column=0, row=0)
        #cr_frame.columnconfigure(0,weight=1)
        #cr_frame.rowconfigure(0,weight=1)
        # add to each C-tab a frame
        self.tabs.add(self.formationTab, text= f'{global_vars.currentWell.uwi}({global_vars.currentWell.alias}) Formations')
        self.tabs.add(self.logTab, text= 'Log Curves')
        self.tabs.add(self.calcLogTab, text= 'Calculated Curves')
        self.tabs.add(self.coreTab, text= 'Core data')

        self.UpdateTabs()

        global_vars.perfTest.Stop("c_tabs")

    def UpdateTabs(self):
        if global_vars.ui.Root.tabs != None:
            self.updateFormationTab()         # fill in Formation Tab content
            self.updateLogCurveTab()          # fill in Log Tab content
            self.updateCalcLogTab()         # fill in Calculated Log Tab content
            self.updateCoreTab()              # fill in core tab
    #------------------------------------------------------------------------------------------------------------------------------------------------------
    # Define FM tab content
    def updateFormationTab(self):
        '''
        Define FM tab content
        '''
        myscrollbar = Scrollbar(self.formationTab, orient=VERTICAL)
        myscrollbar.grid(column=1, row=0, sticky=(NS))

        # Create a Tree in the fm_framebal
        my_tree = ttk.Treeview(self.formationTab, height = 20,yscrollcommand=myscrollbar.set,selectmode='none')

        #my_tree.delete(*my_tree.get_children()) #clear tree

        # Add to fm_frame
        my_tree.grid(column=0, row=0, sticky=(NSEW))
        myscrollbar.config(command=my_tree.yview)
        
        # Set up New my_tree view in Fm_frame
        #define colums
        my_tree['column'] = ['Fm','Src', 'MD']

        #format columns
        my_tree.column("#0",width=0, stretch=NO)
        my_tree.column("Fm",anchor=W, width=120, minwidth=25)
        my_tree.column('Src',anchor=CENTER, width=60)
        my_tree.column("MD",anchor=W, width=100, minwidth=25)

        #Create Headings
        my_tree.heading("#0", text="", anchor=W)
        my_tree.heading('Fm', text="Formation", anchor=W)
        my_tree.heading('Src',text="Source", anchor=CENTER)
        my_tree.heading('MD', text="Measured Depth", anchor=W)

        # loop through column list for headers
        #for column in my_tree['column']:
        #   my_tree.heading(column, text=column)
        #my_tree['show'] = 'headings'

        # loop through Fm data rows
        count=0
        fm_old=0   #prevous formation depth
        for formation in global_vars.currentWell.formations.values():
            my_tree.insert(parent="", index= "end", iid=count, text="", values=(formation.name, formation.source, formation.depth))

            if formation.name != 'TD' and round(formation.depth,4) < fm_old:   #Error in formation top
                alert.Error(alert.ErrorMessage.WRONG_FORMATION_TOP, [formation.name, global_vars.currentWell])
            
            if formation.name != 'TD' and round(formation.depth,4) > fm_old:
                
                fm_old = round(formation.depth,4)  #old fm depth

            count +=1
           
    #------------------------------------------------------------------------------------------------------------------------------------------------------
    def updateLogCurveTab(self):
        '''
        Define Log Curve tab content
        '''
        # Set Treeview and attributes
        #Create Scrollbar
        myscrollbarlc = Scrollbar(self.logTab, orient=VERTICAL)
        myscrollbarlc.grid(column=1, row=0, sticky=(NS))

        # Create a Tree in the fm_frame
        my_treelc = ttk.Treeview(self.logTab, height = 20,yscrollcommand=myscrollbarlc.set,selectmode='browse')     # create a selectable tree view - single line
        # Add to lc_frame
        my_treelc.grid(column=0, row=0, sticky=(NSEW))

        myscrollbarlc.config(command=my_treelc.yview)

        # Working with data trees
        # clear old tree views
        my_treelc.delete(*my_treelc.get_children())

        # Set up New my_tree view in Fm_frame
        #define colums
        my_treelc['column'] = ['Na','Un', 'Ds', 'Fv', 'Lv']

        #format columns
        my_treelc.column("#0",width=0, stretch=NO)
        my_treelc.column('Na',anchor=W, width=100, minwidth=25)
        my_treelc.column('Un',anchor=CENTER, width=60)
        my_treelc.column("Ds",anchor=W, width=230, minwidth=25)
        my_treelc.column("Fv",anchor=W, width=80, minwidth=25)
        my_treelc.column("Lv",anchor=W, width=80, minwidth=25)

        #Create Headings
        my_treelc.heading("#0", text="", anchor=W)
        my_treelc.heading('Na', text="Curve Name", anchor=W)
        my_treelc.heading('Un',text="Units", anchor=W)
        my_treelc.heading('Ds', text="Description", anchor=W)
        my_treelc.heading('Fv', text="First Reading", anchor=W)
        my_treelc.heading('Lv', text="Last Reading", anchor=W)

        #Get las_data for current well
        las_data = global_vars.currentWell.GetLASData(Dir.In)
        if not las_data:   #las opening failed
            return
        df = las_data.df()

        # loop through Curve data rows
        start_V=0
        end_V=100
        count=0
        for item in las_data.curves:
            if count>0:      #Not dept index
                # get curve name
                c_name=item.mnemonic
                c = df[c_name]

                start_V=c.first_valid_index()
                end_V=c.last_valid_index()

                my_treelc.insert(parent="", index= "end", iid=count, text="", values=(item.mnemonic, item.unit, item.descr, start_V, end_V))
            count +=1
        #------------------------------------------------------------------------------------------------------------------------------------------------------
        def onDoubleClk(treeviewdb : ttk.Treeview, event : Event):
            '''
            select logging curve in logcurve tab or in newlogs tab or CR_Tab
            opt = 0 use alias array  opt = 1  use crvnm   opt = 2 use cdescrvs
            '''
            row=treeviewdb.focus()
            value=treeviewdb.item(row,'values')[0]

            global_vars.project.currentWellList.list = global_vars.project.currentWellList.GetWellsByCurveAlias(value, Dir.In)
                        
            self.Update()
            global_vars.project.currentWellList.SaveAsPrompt()
        #------------------------------------------------------------------------------------------------------------------------------------------------------
        def Show_Exit(win):
            win.destroy()
        
        def onShowlog( mtreeview : ttk.Treeview, event : Event):
            '''
            select logging curve in logcurve tab or in newlogs tab or CR_Tab
            and show logcontent window
            '''

            #Get las_data for current well
            las_data = global_vars.currentWell.GetLASData(Dir.In)
            las_df=las_data.df()
            cstep=0.1
            #set depth interval
            las_start=las_data.well.STRT.value
            las_stop=las_data.well.STOP.value
            idx_top=0
            idx_bot=int((las_stop - las_start)/cstep)+1  #get very last of array

            #show toplevel window
            log_win = common.initCommonWindow(title='Show curve content', width=470, height=830, topMost = 2 )
            self.window.protocol("WM_DELETE_WINDOW", lambda:  Show_Exit(log_win))
            row=mtreeview.focus()
            #Get aka of curve from values on selected line
            values=mtreeview.item(row,'values')

            # get curve name
            C_label0=Label(log_win,text=values[0] + ' properties')
            C_label0.grid(row=0, column=0, pady=5)
            
            C_label1=Label(log_win,text='log Interval: ' + str(las_start) + ' to ' + str(las_stop) + 'm')
            C_label1.grid(row=1, column=0,padx=5)

            #List curve values in frame
            C_Frame=Frame(log_win, width=200,height= 700, bg= '#d7ffff')
            C_Frame.grid(row=3, column=0,padx=5, pady=10)

            '''
            fig, ax = plt.subplots(nrows=1, figsize=(13,20))
            Canvas=FigureCanvasTkAgg(fig, master=log_win)
            Canvas.get_tk_widget().grid(column=3, row=0)

            crv1=las_df[values[0]]

            max_y=las_stop
            min_y=las_start
            ax.set_ylim(max_y,min_y)
            #ax.set_xlim(float(tick_list[props[crv_idx][2]][0]), float(tick_list[props[crv_idx][2]][4]))
            ax.minorticks_on()
            ax.grid(which='major', linestyle='-', linewidth='0.5', color='silver')
            ax.grid(which='minor', linestyle=':', linewidth='0.35', color='silver')
            ax.grid(True)
            #ax.spines['top'].set_position(('outward',pos))
            #ax.spines['top'].set_color(color_list[props[0][0]])
            ax.set_xlabel(crv1.name) #,color=
            ax.set_ylabel('Depth (m)',color='black')
            ax.tick_params(axis='x', colors='green')
            ax.title.set_color('black')
            #ax.set_xticks(tick_list[props[crv_idx][2]])       

            #linestyle=line_list[props[crv_idx][1]]
            line, = ax.plot(crv1,crv1.index,label=crv1.name, color = 'magenta')



            grscrollbar = Scrollbar(Canvas, orient=VERTICAL)
            grscrollbar.grid(column=1, row=0, sticky=(NS))
            '''
            
            # Set Treeview and attributes
            #Create Scrollbar
            myscrollbarcrv = Scrollbar(C_Frame, orient=VERTICAL)
            myscrollbarcrv.grid(column=1, row=0, sticky=(NS))

                # Create a Tree in the fm_frame
            my_treecrv = ttk.Treeview(C_Frame, height =34,yscrollcommand=myscrollbarcrv.set,selectmode='browse')     # create a selectable tree view - single line
            # Add to lc_frame
            my_treecrv.grid(column=0, row=0,)  #sticky=(NSEW)

            myscrollbarcrv.config(command=my_treecrv.yview)

            # Working with data trees
            # clear old tree views
            my_treecrv.delete(*my_treecrv.get_children())

            # Set up New my_tree view in C_Frame
            #define colums

            my_treecrv['column'] = ['Dp','Vl']

            #format columns
            my_treecrv.column("#0",width=0,stretch=NO)     #stretch=NO
            my_treecrv.column('Dp', width=70,stretch=NO,anchor=W)
            my_treecrv.column('Vl', width=70,stretch=NO,anchor=W)


            #Create Headings
            my_treecrv.heading("#0", text="", anchor=W)
            my_treecrv.heading('Dp', text="Depth", anchor=W)
            my_treecrv.heading('Vl',text="Value", anchor=W)

            mlist= las_df[values[0]].tolist()
            mlist2=list(las_data.index)
            # loop through Curve data rows
            count=0
            for item in mlist2:
                if count>0:      #Not dept index
                    my_treecrv.insert(parent="", index= "end", iid=count, text="", values=(item, mlist[count]))
                count +=1

            # done
            b_done=Button(log_win, bg='cyan', text="Done", command=lambda: log_win.quit())
            b_done.grid(row=130,column=0,padx = 50, sticky=W)
            
            log_win.mainloop()
            #Update treeline  
            log_win.destroy()

        #select a log curve
        my_treelc.bind("<Button-2>", lambda e: onShowlog( my_treelc, e))             #click middle button
        my_treelc.bind("<Double-1>", lambda e: onDoubleClk(my_treelc, e))           #double click left button
        my_treelc.bind("<Button-3>", lambda e: self.changeCurveName(my_treelc, e, global_vars.currentWell)) #click right button
    #------------------------------------------------------------------------------------------------------------------
    
    def updateCalcLogTab(self):
        '''
        Define LC tab content
        '''
        
        # Set Treeview and attributes
        #Create Scrollbar
        myscrollbarlc = Scrollbar(self.calcLogTab, orient=VERTICAL)
        myscrollbarlc.grid(column=1, row=0, sticky=(NS))

        # Create a Tree in the fm_frame
        my_treeclc = ttk.Treeview(self.calcLogTab, height = 20,yscrollcommand=myscrollbarlc.set,selectmode='browse')     # create a selectable tree view - single line
        # Add to nwlc_frame
        my_treeclc.grid(column=0, row=0, sticky=(NSEW))

        myscrollbarlc.config(command=my_treeclc.yview)

        # Working with data trees
        # clear old tree views
        my_treeclc.delete(*my_treeclc.get_children())

        # Set up New my_tree view in nwlc_frame
        #define colums
        my_treeclc['column'] = ['Na','Un', 'Ds', 'Fv', 'Lv']

        #format columns
        my_treeclc.column("#0",width=0, stretch=NO)
        my_treeclc.column('Na',anchor=W, width=100, minwidth=25)
        my_treeclc.column('Un',anchor=CENTER, width=60)
        my_treeclc.column("Ds",anchor=W, width=230, minwidth=25)
        my_treeclc.column("Fv",anchor=W, width=80, minwidth=25)
        my_treeclc.column("Lv",anchor=W, width=80, minwidth=25)

        #Create Headings
        my_treeclc.heading("#0", text="", anchor=W)
        my_treeclc.heading('Na', text="Curve Name", anchor=W)
        my_treeclc.heading('Un',text="Units", anchor=W)
        my_treeclc.heading('Ds', text="Description", anchor=W)
        my_treeclc.heading('Fv', text="First Reading", anchor=W)
        my_treeclc.heading('Lv', text="Last Reading", anchor=W)

        #Get las_data for current well
        las_data = global_vars.currentWell.GetLASData(Dir.Out)
        if not las_data:   #las opening failed
            return
        
        df = las_data.df()

        # loop through Curve data rows
        start_V=0
        end_V=100
        count=0
        for item in las_data.curves:
            if count>0:      #Not dept index
                # get curve name
                c_name=item.mnemonic
                c = df[c_name]

                start_V=c.first_valid_index()
                end_V=c.last_valid_index()

                my_treeclc.insert(parent="", index= "end", iid=count, text="", values=(item.mnemonic, item.unit, item.descr, start_V, end_V))
            count +=1

        #------------------------------------------------------------------------------------------------------------------------------------------------------
        def myDoubleClk(my_treeclc : ttk.Treeview, event : Event):
            '''
            select logging curve in logcurve tab or in newlogs tab or CR_Tab
            opt = 0 use alias array  opt = 1  use crvnm   opt = 2 use cdescrvs
            '''
            NewList=[]
            row=my_treeclc.focus()
            value=my_treeclc.item(row,'values')[0]

            global_vars.project.currentWellList.list 
            mlist=global_vars.project.currentWellList.GetWellsByCurveName(value, Dir.Out)
            global_vars.project.currentWellList.list = mlist
            self.Update()
            global_vars.project.currentWellList.SaveAsPrompt()

        #------------------------------------------------------------------------------------------------------------------------------------------------------ 
        def onShowlog( mtreeview : ttk.Treeview, event : Event):
            '''
            select logging curve in logcurve tab or in newlogs tab or CR_Tab
            and show logcontent window
            '''
        
            #Get las_data for current well
            las_data = global_vars.currentWell.GetLASData(Dir.Out)
            las_df=las_data.df()
            cstep=0.1
            #set depth interval
            las_start=las_data.well.STRT.value
            las_stop=las_data.well.STOP.value
            idx_top=0
            idx_bot=int((las_stop - las_start)/cstep)+1  #get very last of array

            #show toplevel window
            log_win = common.initCommonWindow(title='Show curve content', width=470, height=830, topMost = 2 )

            row=mtreeview.focus()
            #Get aka of curve from values on selected line
            values=mtreeview.item(row,'values')

            # get curve name
            C_label0=Label(log_win,text=values[0] + ' properties')
            C_label0.grid(row=0, column=0, pady=5)
            
            C_label1=Label(log_win,text='log Interval: ' + str(las_start) + ' to ' + str(las_stop) + 'm')
            C_label1.grid(row=1, column=0,padx=5)

            #List curve values in frame
            C_Frame=Frame(log_win, width=200,height= 700, bg= '#d7ffff')
            C_Frame.grid(row=3, column=0,padx=5, pady=10)

            '''
            fig, ax = plt.subplots(nrows=1, figsize=(13,20))
            Canvas=FigureCanvasTkAgg(fig, master=log_win)
            Canvas.get_tk_widget().grid(column=3, row=0)

            crv1=las_df[values[0]]

            max_y=las_stop
            min_y=las_start
            ax.set_ylim(max_y,min_y)
            #ax.set_xlim(float(tick_list[props[crv_idx][2]][0]), float(tick_list[props[crv_idx][2]][4]))
            ax.minorticks_on()
            ax.grid(which='major', linestyle='-', linewidth='0.5', color='silver')
            ax.grid(which='minor', linestyle=':', linewidth='0.35', color='silver')
            ax.grid(True)
            #ax.spines['top'].set_position(('outward',pos))
            #ax.spines['top'].set_color(color_list[props[0][0]])
            ax.set_xlabel(crv1.name) #,color=
            ax.set_ylabel('Depth (m)',color='black')
            ax.tick_params(axis='x', colors='green')
            ax.title.set_color('black')
            #ax.set_xticks(tick_list[props[crv_idx][2]])       

            #linestyle=line_list[props[crv_idx][1]]
            line, = ax.plot(crv1,crv1.index,label=crv1.name, color = 'magenta')



            grscrollbar = Scrollbar(Canvas, orient=VERTICAL)
            grscrollbar.grid(column=1, row=0, sticky=(NS))
            '''
            
            # Set Treeview and attributes
            #Create Scrollbar
            myscrollbarcrv = Scrollbar(C_Frame, orient=VERTICAL)
            myscrollbarcrv.grid(column=1, row=0, sticky=(NS))

                # Create a Tree in the fm_frame
            my_treecrv = ttk.Treeview(C_Frame, height =34,yscrollcommand=myscrollbarcrv.set,selectmode='browse')     # create a selectable tree view - single line
            # Add to lc_frame
            my_treecrv.grid(column=0, row=0,)  #sticky=(NSEW)

            myscrollbarcrv.config(command=my_treecrv.yview)

            # Working with data trees
            # clear old tree views
            my_treecrv.delete(*my_treecrv.get_children())

            # Set up New my_tree view in C_Frame
            #define colums

            my_treecrv['column'] = ['Dp','Vl']

            #format columns
            my_treecrv.column("#0",width=0,stretch=NO)     #stretch=NO
            my_treecrv.column('Dp', width=70,stretch=NO,anchor=W)
            my_treecrv.column('Vl', width=70,stretch=NO,anchor=W)


            #Create Headings
            my_treecrv.heading("#0", text="", anchor=W)
            my_treecrv.heading('Dp', text="Depth", anchor=W)
            my_treecrv.heading('Vl',text="Value", anchor=W)

            mlist= las_df[values[0]].tolist()
            mlist2=list(las_data.index)
            # loop through Curve data rows
            count=0
            for item in mlist2:
                if count>0:      #Not dept index
                    my_treecrv.insert(parent="", index= "end", iid=count, text="", values=(item, mlist[count]))
                count +=1

            # done
            b_done=Button(log_win, bg='cyan', text="Done", command=lambda: log_win.quit())
            b_done.grid(row=130,column=0,padx = 50, sticky=W)
            
            log_win.mainloop()
            #Update treeline  
            log_win.destroy()

        #select a log curve
        my_treeclc.bind("<Double-1>", lambda e: myDoubleClk(my_treeclc, e))
        my_treeclc.bind("<Button-2>", lambda e: onShowlog( my_treeclc, e))             #click middle button
    
    #------------------------------------------------------------------------------------------------------------------------------------------------------
    def updateCoreTab(self):
        '''
        Define CR tab content
        '''
        
        global_vars.perfTest.Start("core_tab")
        # Set Treeview and attributes
        #Create Scrollbar
        myscrollbarlc = Scrollbar(self.coreTab, orient=VERTICAL)
        myscrollbarlc.grid(column=1, row=0, sticky=(NS))

        # Create a Tree in the fm_frame
        my_treelc = ttk.Treeview(self.coreTab, height = 20,yscrollcommand=myscrollbarlc.set,selectmode='browse')     # create a selectable tree view - single line
        # Add to cr_frame
        my_treelc.grid(column=0, row=0, sticky=(NSEW))

        myscrollbarlc.config(command=my_treelc.yview)

        # Working with data trees
        # clear old tree views
        my_treelc.delete(*my_treelc.get_children())

        # Set up New my_tree view in cr_frame
        #define colums
        my_treelc['column'] = ['Na','Un', 'Ds', 'Fv', 'Lv']

        #format columns
        my_treelc.column("#0",width=0, stretch=NO)
        my_treelc.column('Na',anchor=W, width=100, minwidth=25)
        my_treelc.column('Un',anchor=CENTER, width=60)
        my_treelc.column("Ds",anchor=W, width=230, minwidth=25)
        my_treelc.column("Fv",anchor=W, width=80, minwidth=25)
        my_treelc.column("Lv",anchor=W, width=80, minwidth=25)

        #Create Headings
        my_treelc.heading("#0", text="", anchor=W)
        my_treelc.heading('Na', text="Curve Name", anchor=W)
        my_treelc.heading('Un',text="Units", anchor=W)
        my_treelc.heading('Ds', text="Description", anchor=W)
        my_treelc.heading('Fv', text="First Reading", anchor=W)
        my_treelc.heading('Lv', text="Last Reading", anchor=W)

        # loop through column list for headers
        #for column in my_treelc['column']:
        #   my_treelc.heading(column, text=column)
        #my_treelc['show'] = 'headings'

        #Get CAS data
        cas_data = global_vars.currentWell.GetLASData(Dir.In, '.cas')
        if not cas_data:   #las opening failed
            return
        
        df=cas_data.df()

        # loop through Curve data rows
        start_V=0
        end_V=100
        count=0
        for item in cas_data.curves:
            if count>0:      #Not dept index
                # get curve name
                c_name=item.mnemonic
                c = df[c_name]

                start_V=c.first_valid_index()
                end_V=c.last_valid_index()

                my_treelc.insert(parent="", index= "end", iid=count, text="", values=(item.mnemonic, item.unit, item.descr, start_V, end_V))
            count +=1

        def onDoubleClk(treeview : ttk.Treeview, event : Event):
            '''
            remove all wells without core data
            '''
            new_Well_list : WellList = WellList()

            #row=my_treelc.focus()
            #value=my_treelc.item(row,'values')[0]
        
            for well in global_vars.project.currentWellList.GetWells():
                if well.GetWellFile(Dir.In, '.cas') is not None: 
                    new_Well_list.Add(well)

            # when done
            global_vars.project.currentWellList = new_Well_list
            self.Update()
            global_vars.project.currentWellList.SaveAsPrompt()

        #select a log curve
        my_treelc.bind("<Double-1>", lambda e: onDoubleClk(my_treelc, e,2))
        global_vars.perfTest.Stop("core_tab")

    #endregion tabs
    