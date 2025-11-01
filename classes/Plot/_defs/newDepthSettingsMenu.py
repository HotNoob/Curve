
import tkinter
import tkinter.ttk
from tkinter import E, END, SINGLE, Button, Entry, Label, Listbox, W, ttk
from typing import TYPE_CHECKING
from defs import excel, las

import defs.alert as alert
import defs.common as common
import global_vars
from classes.MinMaxScale import MinMaxScale
from classes.Object import Object
from classes.Settings import Settings
from enumerables import Dir, PlotType
from structs import ZoneDepths

if TYPE_CHECKING:
    from .. import Plot


#============================================================================================================================================
def newDepthSettingsMenu(self : 'Plot') -> bool:
    '''
    Set plot settings for Xplot Histogram Xplot with colorbar and 3_D plots in Graphics and Answer_plots
    To be used for Pickett plots????
    '''

               #Fm nomentclature and zone definition dataframe

    #from LAS get top and bottom get top at 100 above bottom or to top if less
    self.zoneDepths = None
    uwi=global_vars.project.currentWellList[0]
    well = global_vars.project.projectWellList.Get(uwi)
    las_data = well.GetLASHeaders(Dir.In)
    if las_data==None:
        return
    gr_top=las_data.well.STRT.value
    gr_base=las_data.well.STOP.value
    #gr_step=round(las_data.well.STEP.value,2) 
    #global_vars.dpt_int.append([gr_top, gr_base,gr_step]) # dpt_int[\d][2]i dont see gr_step being used anywhere
    self.zoneDepths = ZoneDepths(top=gr_top, base=gr_base, name='WELL')

    #create combobox list of zones with offsets
    z_list = list(global_vars.project.formationZones.keys())
    # Set dpt_win toplevel window
    dpt_win = common.initCommonWindow(f'Depth or Stratigraphic Interval for {well.uwi}({well.alias})', 400, 300, 3)

    # set Widget options
    t_options=[]   #initialize top and bottom options
    b_options=[]
    for i in range(8):
        t_options.append(str(gr_base - 50 - 25*i))
        b_options.append(str(gr_base - 25 *i))

    #--------------------------------------------------------------------------------------------------------------------------------------------
    def show_zspecs(slect : str , lb1 : Label, T_D : Entry, B_D : Entry):
        '''
        show selected zone properties in dpt_win
        '''
        formationZone = global_vars.project.GetFormationZone(slect)

        txt1=f"Top: {formationZone.TopFormation} + {formationZone.TopOffset}m Base: {formationZone.BaseFormation} + {formationZone.BaseOffset}m"
        lb1.config(text=txt1)
        
        # set DPR_int to zone depths for well
        count=0
        if global_vars.currentWell is None:
            uwi=global_vars.project.currentWellList[0]
            well = global_vars.project.projectWellList.Get(uwi)
        else:
            well=global_vars.currentWell
            
        self.zoneDepths = well.GetZoneDepths(slect)

        T_D.delete(0, END) #clear
        T_D.insert(0, self.zoneDepths.top)         # Update top Entrybox
        B_D.delete(0, END) # clear
        B_D.insert(0, self.zoneDepths.base)         # Update base Entrybox
    #--------------------------------------------------------------------------------------------------------------------------------------------
    def dpt_quit( win, top, base, dftop, dfbase, zone, opt):
        '''
        update depths and quit dpt_win mainloop
        '''

        if opt==1:                                  #if submitted
            if top:
                self.zoneDepths.top = float(top)
            elif dftop:
                self.zoneDepths.top = float(dftop)
            if base:
                self.zoneDepths.base = float(base)
            elif dfbase:
                self.zoneDepths.base = float(dfbase)
            if zone:
                self.zoneDepths.name = zone
                self.zone = zone
        else:
            self.zoneDepths = None

        win.quit()    # quit dpt_win mainloop

    #Define widgets
    T_dptl = Label(dpt_win, text = 'select TOP depth')
    B_dptl = Label(dpt_win, text = 'select Bottom depth')
    e_top=ttk.Combobox(dpt_win, value=t_options)
    e_top.current(0)
    e_base=ttk.Combobox(dpt_win, value=b_options)
    e_base.current(0)
    t_entryL=Label(dpt_win, text = 'OR enter Top Depth here')
    t_entry=Entry(dpt_win)
    b_entryL=Label(dpt_win, text = 'OR enter Bottom Depth here')
    b_entry=Entry(dpt_win)
    fm_label = Label(dpt_win, text = 'Select a zone to plot a stratigraphic interval')
    z_top : ttk.Combobox =ttk.Combobox(dpt_win, value=z_list)
    #z_top.current(0)    # set default selection
    z_top.bind('<<ComboboxSelected>>', lambda e: show_zspecs(z_top.get(),z1_lab, t_entry,b_entry ))
    z1_lab = Label(dpt_win, text = '')

    q_button = Button(dpt_win, text='Submit', bg='cyan', anchor = W, command= lambda: dpt_quit(dpt_win, t_entry.get(),b_entry.get(), e_top.get(),e_base.get(),z_top.get(),1))
    c_button = Button(dpt_win, text='Cancel', bg='pink', anchor = E, command= lambda: dpt_quit(dpt_win, t_entry.get(),b_entry.get(), e_top.get(),e_base.get(),z_top.get(),0))

    #Place widgets
    T_dptl.grid(row=0,column=0,sticky=W)
    B_dptl.grid(row=0,column=1, sticky=W)
    e_top.grid(row=1, column=0)
    e_base.grid(row=1, column=1)
    q_button.grid(row=6,column=0)
    c_button.grid(row=6,column=1)
    t_entryL.grid(row=2,column=0)
    t_entry.grid(row=3,column=0)
    b_entryL.grid(row=2,column=1)
    b_entry.grid(row=3,column=1)
    fm_label.grid(row=4,column=0, columnspan=2, pady=10)
    z_top.grid(row=5, column=0, pady=10)
    z1_lab.grid(row=5, column=1, pady=10)

    #update depth int list
    dpt_win.mainloop()
    dpt_win.destroy()
    # top depth deeper than bottom depth start over
    if self.zoneDepths is not None:    # If NOT canceled
        if (self.zoneDepths.top>self.zoneDepths.base):
            alert.Error("Top and Bottom depth are mixed up. Try again")
            self.zoneDepths = None
            raise Exception()
    else:
        raise Exception()
    
    return self.zoneDepths is not None