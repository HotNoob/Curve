'''get_ticks'''
from typing import TYPE_CHECKING

from tkinter import Label, StringVar, Button, EW, W, E
import tkinter.ttk as ttk

import defs.common as common
import global_vars

from classes.Object import Object

if TYPE_CHECKING:
    from .. import DepthPlot

#-------------------------------------------------------------------------------------------
def getTicks(self : 'DepthPlot' ,scale) -> bool:
    '''
    get custom ticks
    scale = 0 linear
    scale = 1 logarithmic
    '''

    tk_win = common.initCommonWindow('Custom Ticks', 250, 200)

    #SET WIDGETS
    # create labels
    E_label=Label(tk_win, text="Enter Scale end points", font=('Helvetica',10))    #MAIN label
    E_label1=Label(tk_win, text="Scale minimum")         #Combobox label 1
    E_label2=Label(tk_win, text="Scale maximum")       #Combobox label 2

    # create Entryboxes
    tk1=StringVar()
    tk1.set('min')
    t_min=ttk.Entry(tk_win,textvariable=tk1)
    tk2=StringVar()
    tk2.set('max')
    t_max=ttk.Entry(tk_win,textvariable=tk2)

    buttonResponses : Object = Object()
    buttonResponses.submit = False
    buttonResponses.cancel = False

    # done
    b_done=Button(tk_win, bg='cyan', text="Submit", command= lambda:(setattr(buttonResponses, 'submit', True), tk_win.quit()))
    b_cancel=Button(tk_win, bg='pink', text='Cancel', command= lambda:(setattr(buttonResponses, 'cancel', True), tk_win.quit()))


    #+++++++++++++++++
    #PLACE WIDGETS BASED ON PLOT TYPE and SET STATE TO NORMAL

    # Place T_Label
    E_label.grid(row=0,column=0, columnspan=2, sticky=EW, pady=10)
    E_label1.grid(row=1,column=0, sticky=W)
    E_label2.grid(row=5,column=0, sticky=W)

    #Place  entry boxes and labels
    t_min.grid(row=4, column=0,pady=2, sticky=W)   # place Entry box scale min
    t_max.grid(row=4, column=1,pady=2)   # place Entry box scale max

    b_done.grid(row=11, column=0,pady=5, sticky=W)
    b_cancel.grid(row=11, column=0, pady=5, sticky=E)

    #loop and destroy when done
    tk_win.mainloop()
    
    if buttonResponses.cancel:
        tk_win.destroy()
        return False

    #Calulate custom scale
    tck_lft=float(t_min.get())
    tck_rgt=float(t_max.get())
    if scale == 'linear':
        tck_step=(tck_rgt-tck_lft)/5
        tck1=tck_lft + tck_step
        tck2=tck1 + tck_step
        tck3=tck2 + tck_step
    if scale =='logarithmic':
        tck_step=10
        tck1=tck_lft * tck_step
        tck2=tck1 * tck_step
        tck3=tck2 * tck_step

    global_vars.gticks.append([str(tck_lft), str(tck1),str(tck2), str(tck3), str(tck_rgt)])

    tk_win.destroy()
    return True