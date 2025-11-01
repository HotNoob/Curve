import glob
import os
from tkinter import END, MULTIPLE, NS, VERTICAL, Frame, Listbox, Menu, Scrollbar, StringVar, ttk, Toplevel
import Curve
from classes.Plot import Plot
from classes.Plot.DepthPlot import DepthPlot
from classes.Project.WellList import WellList
from defs import alert, common, main
import global_vars

class Graphing:
    def __init__(self) -> None:
        self.wellList : WellList = None
        self.window : Toplevel = None
        self.well_frame : Frame = None
        self.well_listBox : Listbox = None
        self.well_scrollBar : Scrollbar = None

    def Check_Disabled(self, event):
        ''' force minimize if not logged in '''
        
        if not global_vars.login.loggedIn:
            self.window.iconify()
        
    def Load(self):
        # First create toplevel window
        self.window = common.initCommonWindow('Graphs - Curve ' + global_vars.SoftwareVersion, 250, 600, 2)
        self.window.wm_protocol("WM_DEICONIFY", self.Check_Disabled)
        self.window.bind("<FocusIn>", self.Check_Disabled)


        #window expansion
        self.window.rowconfigure(0,weight=1)
        self.window.columnconfigure(0,weight=1)

        #closing with x in upper right window corner
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.Close())

        self.window.option_add('*tearOff', False)
       
        #region menus
        gr_menubar = Menu(self.window)
        self.window['menu'] = gr_menubar

        # Top Menus
        menu_file = Menu(gr_menubar)
        menu_plot = Menu(gr_menubar)
        menu_help = Menu(gr_menubar)

        # Menubar
        #gr_menubar.config(font=("Verdana", 14))
        gr_menubar.add_cascade(menu=menu_file, label='File')
        gr_menubar.add_cascade(menu=menu_plot, label='Plots')
        gr_menubar.add_cascade(menu=menu_help, label='Help')


        # plot sub menus
        menu_plot.add_command( label='All wells',command= lambda: self.AllWells())
        menu_plot.add_separator()
        menu_plot.add_command( label="Single well Histogram", command= lambda: Plot.newSingleWellHistogram(self.window, wellList=self.wellList))
        menu_plot.add_command( label="Multiple Well Histograms", command= lambda: Plot.newMultipleWellHistograms(self.window, wellList=self.wellList))
        menu_plot.add_command( label="Multi-Well Histogram", command= lambda:  Plot.newMultiWellHistogram(self.window, wellList=self.wellList))
        menu_plot.add_separator()
        menu_plot.add_command( label="Single Well Crossplots", command= lambda: Plot.newSingleWellCrossPlot(self.window, wellList=self.wellList))
        menu_plot.add_command( label="Multiple Well Crossplots", command= lambda: Plot.newMultipleWellCrossPlot(self.window, wellList=self.wellList))
        menu_plot.add_command( label="Multi-Well Crossplot", command= lambda:  Plot.newMultiWellCrossPlot(self.window, wellList=self.wellList))
        menu_plot.add_separator()
        menu_plot.add_command( label="Single Well Zplots", command= lambda: Plot.newSingleWellZPlot(self.window, wellList=self.wellList))
        menu_plot.add_command( label="Multiple Well Zplots", command= lambda: Plot.newMultipleWellZPlots(self.window, wellList=self.wellList))
        menu_plot.add_command( label="Multi-Well Zplot", command= lambda:  Plot.newMultiWellZplot(self.window, wellList=self.wellList))
        menu_plot.add_separator()
        menu_plot.add_command( label="Single Well 3D plots", command= lambda: Plot.newSingleWellThreeDPlot(self.window, wellList=self.wellList))
        menu_plot.add_command( label="Multiple Well 3D plots", command= lambda: Plot.newMultipleWellThreeDPlot(self.window, wellList=self.wellList))
        menu_plot.add_command( label="Multi-Well 3Dplot", command= lambda:  Plot.newMultiWellThreeDPlot(self.window, wellList=self.wellList))
        menu_plot.add_separator()
        menu_plot.add_command( label="Depth plot", command= lambda: DepthPlot.newDepthPlot(self.window, wellList=self.wellList))
        menu_plot.add_separator()
        menu_plot.add_command( label="Pickett plot", command= lambda:  Plot.newPickettPlot(self.window, wellList=self.wellList))
        menu_plot.add_separator()
        menu_plot.add_command( label="Help", command= lambda:  main.c_help(1))

        menu_file.add_command(label='Exit', command= lambda: self.Close())
        #endregion menus

        #region well list box                
        self.well_frame=Frame(self.window)
        ''' holds the well_listBox'''

        self.well_frame.grid(column=0,row=0, sticky=NS)

        #self.well_listBox : Listbox = Listbox(self.well_frame,listvariable=global_vars.w_names, selectmode=MULTIPLE)
        self.well_listBox : Listbox = Listbox(self.well_frame, selectmode=MULTIPLE)
        ''' holds the well list'''

        self.well_scrollBar = Scrollbar(self.well_frame,orient=VERTICAL)

        self.well_listBox.pack()
        self.well_listBox['yscrollcommand'] = self.well_scrollBar.set
        self.well_listBox.bind("<Button-3>", lambda e: self.final_wells())          #left mouse double click
        self.well_listBox.bind("<Double-Button-1>", lambda e:  self.Close())     # right mouse button

        #install scrollbar to wellbox
        self.well_scrollBar.pack(side='right', fill='y')
        self.well_scrollBar.config( command=self.well_listBox.yview) # select one or more wells
        
        #well_box.bind("<Button-1>", lambda e: blblabla   # Select single well for overlay on multiwell plot
        #endregion well list box


    def Show(self):
        '''
        Select well or wellist for graphics
        '''
        
        if self.window is None:
            self.Load()

        #Hide root
        global_vars.ui.Root.window.iconify()

        # Get well list to display
        if global_vars.project.inDir == 'c:/':
            alert.Error("Please, select the input directory in the File menu")
            return
        
        self.wellList = global_vars.project.currentWellList.copy()
        self.Update()

        self.window.deiconify() #show graphing window incase minimized


    def SetWellList(self, newList : WellList):
        self.wellList = newList.copy()
        self.Update()

    # --------------------------------------------------------------------------------------------
    
    def Update(self):
        #clear listbox
        self.well_listBox.delete(0, END)  

        maxWellNameLen = 0
        for index, well in enumerate(self.wellList.GetWells()):
            item = well.alias + ': ' + well.uwi
            self.well_listBox.insert(END,item)

            #Colorize alternating lines of the listbox
            if index % 2 == 0:
                self.well_listBox.itemconfigure(index, background='#f0f0ff') 

            if len(item) > maxWellNameLen:
                maxWellNameLen = len(item)

        self.well_listBox.config(height=self.well_listBox.size(), width=maxWellNameLen)

        # If wells selected
        self.well_listBox.selection_clear(0,'end')
        self.well_listBox.focus_set()

    def Close(self):
        self.window.destroy()
        self.window = None
        global_vars.ui.Root.window.deiconify()

    
    def AllWells(self):
        '''resets the currentWellList and self.wellList to show all project wells '''
        global_vars.project.resetWellList()
        self.ResetWellList()

    def ResetWellList(self):
        self.wellList =global_vars.project.currentWellList.copy()
        self.Update()
        self.well_listBox.selection_clear(0,END)
        self.well_listBox.pack()
    
    def final_wells(self):
        ''' sets the well list to be only the selected wells'''

        select_list = self.well_listBox.curselection()
        if len(select_list)==0:  # if no selection
            return
        
        self.wellList = WellList()
        for i in self.well_listBox.curselection():
            parts = str(self.well_listBox.get(i)).split(':',2)
            uwi = parts[1]
            self.wellList.Add(uwi) 

        global_vars.currentWell = self.wellList.GetWell(0) #set to first well in list

        # Refresh ui
        self.Update()
                
