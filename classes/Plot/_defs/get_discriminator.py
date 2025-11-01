import traceback
from tkinter import LEFT, SOLID, Button, E, Label, StringVar, W, Event, Toplevel, ttk
from typing import TYPE_CHECKING, NamedTuple

#unused import numpy as np
#unused import pandas as pd
from matplotlib import pyplot as plt
from classes.Object import Object

import defs.alert as alert
import defs.main as main


import global_vars
from classes.MinMaxScale import MinMaxScale
import defs.common as common
from defs import program
from enumerables import PlotType, Dir
from structs import CurveSource

if TYPE_CHECKING:
    from .. import Plot
    from classes.Project.Well import Well



class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None
        self.x = 0
        self.y = 0

    def enter(self, event : Event):
        self.x = event.x_root
        self.y = event.y_root
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        #x = y = 0
        #x, y, cx, cy = self.widget.bbox("insert")
        #x += self.widget.winfo_rootx() + 25
        #y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (self.x, self.y+5))
        self.tw.attributes('-topmost', 1)
        label = Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

def get_discriminator(self : 'Plot', well : 'Well'):
    '''
    #get and return 4 discriminator properties from input window upon pressing 'd' in plot using plt_onKey
    '''

    global_vars.tmp=[]
    global_vars.tmp.append(0)

    disc1=[]
    disc2=[]

    curveLists = {}

    #get crv_list for wells in Well_List
    no_crvs=['DEPT']
    crv_list=[]
    #get crv list for Indir, core and Outdir
    curveLists['Input'] = program.com_crvs(no_crvs, [],1)   #get common crvs in Indir
    dirno1=len(crv_list)   #core dir
    # add cas file curves that wells in WELL_LIST have in common
    curveLists['CoreData'] = crv_list=program.comm_core([])
    dirno2=len(crv_list)   #outdir
    curveLists['Output']=program.com_crvs(no_crvs,[],3)           #add any common crvs in Outdir
    #crv_list is complete

    #for now. keep for code compatability
    crv_list = curveLists['Input'] + curveLists['CoreData'] + curveLists['Output']

    # Set dpt_win toplevel window
    dis_win = common.initCommonWindow('Select discriminator criteria for X and Y-axis', 380, 240)

    # set Widget options
    #--------------------------------------------------------------------------------------------------------------------------------------------
    def update_label(e, label,ingadget,mytxt):
        '''
        on eventclick update text in label
        '''
        # get selected curvename
        crv=ingadget.get()
        #get curve scales
        c1_scale,c2_scale,c3_scale,z_scale=main.get_scale(crv,"","","")
        scale = MinMaxScale.FromString(c1_scale)
        mytxt.set(f"Scale: Min:{scale.min} and Max:{scale.max}")
        pass

    curveSources = list(curveLists.keys())
    def sourceSelected(event : Event, curveListCombobox : ttk.Combobox):
        '''curveListCombobox is the combobox that will hold the curve list'''
        curveListCombobox.delete(0,'end')
        print(event.widget.get())
        curveListCombobox['values'] = curveLists[event.widget.get()]
        curveListCombobox['state'] = 'normal'
        

    #Define widgets
    Dl = Label(dis_win, text = 'Select first discrinator curve')
    D2 = Label(dis_win, text = 'Select second discrinator curve')

    d1_curveSource = ttk.Combobox(dis_win, value=curveSources)
    d2_curveSource = ttk.Combobox(dis_win, value=curveSources)
    d1_curveSourceTT = CreateToolTip(d1_curveSource, 'curve source')
    d2_curveSourceTT = CreateToolTip(d2_curveSource, 'curve source')

    d1_crv=ttk.Combobox(dis_win, value=crv_list, state='disabled')
    #d1_crv.current(0)
    d2_crv=ttk.Combobox(dis_win, value=crv_list, state='disabled')
    #d2_crv.current(0)
    
    mytxt1=StringVar()
    mytxt1.set("Default Scale")
    mytxt2=StringVar()
    mytxt2.set("Default Scale")
    sc1_lab=Label(dis_win,textvariable=mytxt1)
    sc2_lab=Label(dis_win,textvariable=mytxt2)
    d1_crv.bind("<<ComboboxSelected>>", lambda e: update_label(e, sc1_lab,d1_crv,mytxt1))
    d2_crv.bind("<<ComboboxSelected>>", lambda e: update_label(e, sc2_lab,d2_crv,mytxt2))
    d1_curveSource.bind("<<ComboboxSelected>>", lambda e: sourceSelected(e, d1_crv))
    d2_curveSource.bind("<<ComboboxSelected>>", lambda e: sourceSelected(e, d2_crv))
    
    lt1_lab=Label(dis_win,text="Less than")
    gt1_lab=Label(dis_win,text="Greater than")
    ltv1=StringVar()
    gtv1=StringVar()
    lt1=ttk.Entry(dis_win,textvariable=ltv1, width=23)
    gt1=ttk.Entry(dis_win,textvariable=gtv1, width=23)

    lt2_lab=Label(dis_win,text="Less than")
    gt2_lab=Label(dis_win,text="Greater than")
    ltv2=StringVar()
    gtv2=StringVar()
    lt2=ttk.Entry(dis_win,textvariable=ltv2, width=23)
    gt2=ttk.Entry(dis_win,textvariable=gtv2, width=23)

    buttonResponse : Object = Object()
    buttonResponse.value = ''

    #--------------------------------------------------------------------------------------------------------------------------------------------
    def submit(win,ds1,gt1,lt1,ds2,gt2,lt2):
        '''
        process submit
        '''
        ds1 = ds1.get()
        ds2 = ds2.get()

        #check if form correctly filled or return
        if ds1 !='None' and ds1 != '':
            if gt1.get()=='' or lt1.get()=='':
                alert.Error(f"Select 'LESS THAN' and 'GREATER THAN' values for {ds1}")
                return
        if ds2 !='None' and ds2 != '' :
            if gt2.get()=='' or lt2.get()=='':
                alert.Error(f"Select 'LESS THAN' and 'GREATER THAN' values for {ds2}")
                return
        if (ds1 =='None' or ds1 == '') and ( ds2 =='None' or ds2 == '' ):         #If no discriminator is selected
            alert.Error("Select at least one Discriminator curve or press <Cancel>")
            return
       
        setattr(buttonResponse, 'value', 'submit')
        win.quit()
        return

    q_button = Button(dis_win, text='Submit', bg='cyan', anchor = W, command= lambda: submit(dis_win,d1_crv,gt1,lt1,d2_crv,gt2,lt2))

    res_button = Button(dis_win, text='Reset', bg='palegreen', anchor = E, command= lambda: (setattr(buttonResponse, 'value', 'reset'), dis_win.quit()))
    c_button = Button(dis_win, text='Cancel', bg='pink', anchor = E, command= lambda: (setattr(buttonResponse, 'value', 'cancel'), dis_win.quit()))
    #c_button = Button(dis_win, text='Cancel', bg='pink', anchor = E, command= )

    #Place widgets
    row = 0
    Dl.grid(row=row,column=0,sticky=W)
    D2.grid(row=row,column=1, sticky=W)

    row += 1
    d1_curveSource.grid(row=row, column=0)
    d2_curveSource.grid(row=row, column=1)

    row += 1
    d1_crv.grid(row=row, column=0)
    d2_crv.grid(row=row, column=1)

    row += 1
    sc1_lab.grid(row=row,column=0, pady=2, sticky=W)
    sc2_lab.grid(row=row,column=1, pady=2, sticky=W)

    row += 1
    lt1_lab.grid(row=row,column=0, pady=2, sticky=W)
    lt2_lab.grid(row=row,column=1, pady=2, sticky=W)

    row += 1
    lt1.grid(row=row,column=0)
    lt2.grid(row=row,column=1)

    row += 1
    gt1_lab.grid(row=row,column=0, pady=2, sticky=W)
    gt2_lab.grid(row=row,column=1, pady=2, sticky=W)

    row += 1
    gt1.grid(row=row,column=0)
    gt2.grid(row=row,column=1)

    row += 1
    q_button.grid(row=row,column=0, padx=5, pady=20,sticky=W)
    res_button.grid(row=row,column=1,pady=20, sticky=E)
    c_button.grid(row=row,column=1,pady=20, sticky=W)

    #update depth int list
    dis_win.mainloop()

    match buttonResponse.value:
        case 'cancel':
            dis_win.destroy()
            return
        case 'reset':
            dis_win.destroy()
            fignum = plt.gcf().number
            if self.plotType == PlotType.Histogram or self.plotType == PlotType.ThreeDPlot:
                return self.resetDataFrames[fignum][0], self.resetDataFrames[fignum][0],0, 0, 0, 0
            else:
                return self.resetDataFrames[fignum][0], self.resetDataFrames[fignum][1], 0, 0, 0, 0
        case 'submit':
            pass

    ds1=d1_crv.get()
    ds2=d2_crv.get()
    if(ds1 == ''):
        ds1 = 'None'
    
    if(ds2 == ''):
        ds2 = 'None'

    if ds2!='None':
        min2=float(gt2.get())
        max2=float(lt2.get())
        ds2 = CurveSource(Dir.FromString(d2_curveSource.get()), ds2)
    else:
        min2=0
        max2=0
        ds2 = None

    if ds1!='None':
        min1=float(gt1.get())
        max1=float(lt1.get())
        ds1 = CurveSource(Dir.FromString(d1_curveSource.get()), ds1)
    else:
        min1=0
        max1=0
        d1 = None

    #get disc1 and disc2 dataframes
    try:
        disc1, disc2 = self.discrim_crv(ds1, ds2, crv_list, well)
    except Exception:
        print(traceback.print_exc())
        global_vars.tmp=[]
        dis_win.destroy()
        return

    dis_win.destroy()
    global_vars.tmp=[]
    return disc1, disc2, min1, max1, min2, max2
