import tkinter.ttk as ttk
from tkinter import Button, Label
from typing import TYPE_CHECKING

import defs.alert as alert
import defs.common as common
import defs.excel as excel
import defs.prompt as prompt
import global_vars
from classes.Object import Object
from classes.Settings import Settings
from defs import program

if TYPE_CHECKING:
    from ...MultiMineral import MultiMineral


#was minsettings
def newSettingsMenu(self : 'MultiMineral') -> bool:
    '''
    Show and edit multimin dictionary
    '''

    zon=0
    yn=prompt.yesno('Use new settings (Y) or previous settings (N)')

    global_vars.ui.Root.window.iconify()

    if not yn:         #load mlt_settings
        self.LoadDefaultSettings()

    #create list of common curves
    crv_list=[]
    no_crvs=['DEPT','BIT','TEMP','RT','SW_FN','PHI_FN','PHIE_FN','K_FN','VCL_FN']
    crv_list=program.com_crvs(no_crvs,crv_list,0)

    crv_list1=[]
    crv_list2=[]
    crv_list3=[]
    crv_list4=[]
    crv_list5=[]

    if len(crv_list) < 4:
        global_vars.ui.Root.window.deiconify()
        alert.RaiseException("Wells have too few curves in common (in Outdir) for multimineral analysis")

    if 'GR' in crv_list:
        crv_list1.append('GR')
    if 'GR_NRM' in crv_list:
        crv_list1.append('GR_NRM')
    if 'GR' not in crv_list and 'GR_NRM' not in crv_list:
        global_vars.ui.Root.window.iconify()
        alert.RaiseException("GR curves missing cannot run Multimineral")
    if 'PEF' in crv_list:
        crv_list2.append('PEF')
    else:
        if 'RHOB' in crv_list:
            crv_list2.append('RHOB')
        if 'RHOB_NRM' in crv_list:
            crv_list2.append('RHOB_NRM')
        if 'RHOB' not in crv_list and 'RHOB_NRM' not in crv_list:
            global_vars.ui.Root.window.iconify()
            alert.RaiseException("PEF AND RHOB curves missing cannot run Multimineral")
    if 'PEF' in crv_list:
        if 'RHOB' in crv_list:
            crv_list3.append('RHOB')
        if 'RHOB_NRM' in crv_list:
            crv_list3.append('RHOB_NRM')
        if 'RHOB' not in crv_list and 'RHOB_NRM' not in crv_list:
            global_vars.ui.Root.window.iconify()
            alert.RaiseException("RHOB curves missing cannot run Multimineral")
        if 'NPHI' in crv_list:
            crv_list4.append('NPHI')
        if 'NPHI_NRM' in crv_list:
            crv_list4.append('NPHI_NRM')
        if 'NPHI' not in crv_list and 'NPHI_NRM' not in crv_list:
            global_vars.ui.Root.window.iconify()
            alert.RaiseException("NPHI curves missing cannot run Multimineral")
        if 'DT' in crv_list:
            crv_list5.append('DT')
        if 'DT_NRM' in crv_list:
            crv_list5.append('DT_NRM')
        if 'DT' not in crv_list and 'DT_NRM' not in crv_list:
            crv_list5.append('None')
    else:           #if PEF is missing
        if 'NPHI' in crv_list:
            crv_list3.append('NPHI')
        if 'NPHI_NRM' in crv_list:
            crv_list3.append('NPHI_NRM')
        if 'NPHI' not in crv_list and 'NPHI_NRM' not in crv_list:
            global_vars.ui.Root.window.iconify()
            alert.RaiseException("NPHI curves missing cannot run Multimineral")
        if 'DT' in crv_list:
            crv_list4.append('DT')
        if 'DT_NRM' in crv_list:
            crv_list4.append('DT_NRM')
        if 'DT' not in crv_list and 'DT_NRM' not in crv_list:
            crv_list4=crv_list
        crv_list5=crv_list

    crv_box : list[ttk.Combobox] = [None] * 5  #Create list of curve boxes

    #Create settings window
    mst_win = common.initCommonWindow(title= 'Multimineral Settings', width=800, height=200)

    #enter settings
    mst_list = list(global_vars.project.formationZones.keys())
    mst_lbl = Label(mst_win, text='Select Zone:')
    mst_box=ttk.Combobox(mst_win,value=mst_list)

    if yn==False: #get previous zone
        zon = common.listIndexOf(mst_list, self.settings.Get('Zone'), 0)

    mst_box.current(zon)
    crv_lbl = Label(mst_win, text='Select Input Curves:')
    crv_box[0]=ttk.Combobox(mst_win,value=crv_list1)
    #crv_box[0]=ttk.Combobox(mst_win,value=crv_list)
    if yn==False: #get previous zone
        zon = common.listIndexOf(crv_list1, self.settings.Get('Curve1'), 0)
        #zon=findinlist(mlt_set[1][1],crv_list)
    crv_box[0].current(zon)
    crv_box[1]=ttk.Combobox(mst_win,value=crv_list2)
    #crv_box[1]=ttk.Combobox(mst_win,value=crv_list)
    if yn==False: #get previous zone
        zon = common.listIndexOf(crv_list2, self.settings.Get('Curve2'), 0)
        #zon=findinlist(mlt_set[2][1],crv_list)
    crv_box[1].current(zon)
    crv_box[2]=ttk.Combobox(mst_win,value=crv_list3)
    #crv_box[2]=ttk.Combobox(mst_win,value=crv_list)
    if yn==False: #get previous zone
        zon = common.listIndexOf(crv_list3, self.settings.Get('Curve3'), 0)
        #zon=findinlist(mlt_set[3][1],crv_list)
    crv_box[2].current(zon)
    crv_box[3]=ttk.Combobox(mst_win,value=crv_list4)
    #crv_box[3]=ttk.Combobox(mst_win,value=crv_list)
    if yn==False: #get previous zone
        zon = common.listIndexOf(crv_list4, self.settings.Get('Curve4'), 0)
        #zon=findinlist(mlt_set[4][1],crv_list)
    crv_box[3].current(zon)
    crv_box[4]=ttk.Combobox(mst_win,value=crv_list5)
    #crv_box[4]=ttk.Combobox(mst_win,value=crv_list)
    if yn==False:  #get previous zone
        zon = common.listIndexOf(crv_list5, self.settings.Get('Curve5'), 0)
        #zon=findinlist(mlt_set[5][1],crv_list)
    crv_box[4].current(zon)

    my_list=['SS','LS']
    my_lbl = Label(mst_win, text='Select Lithology:')
    my_box=ttk.Combobox(mst_win,value=my_list)
    if yn==False:
        zon=0
        if self.settings.Get('Lithology')=='LS':
            zon=1
    my_box.current(0)

    mst_lbl.grid(row=4, column=0, padx=15,pady=15)
    mst_box.grid(row=5, column=0, padx=15,pady=5)

    crv_lbl.grid(row=2, column=0, padx=5)
    crv_box[0].grid(row=3, column=0, padx=5, pady=10)
    crv_box[1].grid(row=3, column=1, padx=5, pady=10)
    crv_box[2].grid(row=3, column=2, padx=5, pady=10)
    crv_box[3].grid(row=3, column=3, padx=5, pady=10)
    crv_box[4].grid(row=3, column=4, padx=5, pady=10)

    my_lbl.grid(row=4, column=1, padx=15, pady=15)
    my_box.grid(row=5, column=1, padx=15, pady=5)

    buttonResponses : Object = Object()
    buttonResponses.submit = False
    buttonResponses.cancel = False
    buttonResponses.save = False

    # done or cancel
    b_done=Button(mst_win, bg='cyan', width=20, text="Submit", padx=10, command=lambda:(setattr(buttonResponses, 'submit', True), mst_win.quit()))
    b_cancel=Button(mst_win, bg='pink', width=20, text='Cancel',command= lambda:(setattr(buttonResponses, 'cancel', True), mst_win.quit()))
    b_save=Button(mst_win, bg='palegreen',text='Save', width=20, command=lambda:(setattr(buttonResponses, 'save', True), mst_win.quit()))
    b_done.grid(row=6, column=0, pady=10)
    b_save.grid(row=6, column=1, pady=10)
    b_cancel.grid(row=6,column=3,pady=10)

    mst_win.mainloop()

    #Cancel minsettings
    if buttonResponses.cancel:
        mst_win.destroy()
        return False

        # Set mlt_set
    mlt_set=[]          #empty multimineral settings list
    mlt_set.append(['Zone',mst_box.get()])
    mlt_set.append(['Curve1',crv_box[0].get()])
    mlt_set.append(['Curve2',crv_box[1].get()])
    mlt_set.append(['Curve3',crv_box[2].get()])
    mlt_set.append(['Curve4',crv_box[3].get()])
    mlt_set.append(['Curve5',crv_box[4].get()])
    mlt_set.append(['Lithology',my_box.get()])
    self.settings = Settings()
    self.settings.LoadFromArray(mlt_set)

    #Save mlt file
    if buttonResponses.save:
        self.SaveDefaultSettings()

    mst_win.destroy()

    #update multimin parameter spreadsheet
    if not self.newParametersMenu():         # multimin parameters cancelled
        return False

    global_vars.ui.Root.window.deiconify()
    return True