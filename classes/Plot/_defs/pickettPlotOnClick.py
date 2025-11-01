from tkinter import Button, Label, StringVar, ttk
from typing import TYPE_CHECKING

import matplotlib.pyplot as pyplot

import defs.common as common
import defs.excel as excel
import global_vars
from classes.Object import Object

if TYPE_CHECKING:
    from .. import Plot

def pickettPlotOnClick(self : 'Plot', zone):
    global_vars.tmp.append(0)

    pk_win = common.initCommonWindow(f'Set A, M, N and RWa for {zone}', 325, 200)

    #Set Widgets
    a_label=Label(pk_win, text="To change type new a")
    m_label=Label(pk_win, text="To change type new m")
    n_label=Label(pk_win, text="To change type new n")
    rw_label=Label(pk_win, text="To change type new Rw")

    #get new parms a m n and rw
    a_param = global_vars.project.formationZoneParameters.Get('a')
    m_param = global_vars.project.formationZoneParameters.Get('m')
    n_param = global_vars.project.formationZoneParameters.Get('n')
    rw_param = global_vars.project.formationZoneParameters.Get('rw')

    a_val=StringVar(value=a_param.Get(zone))
    m_val=StringVar(value=m_param.Get(zone))
    n_val=StringVar(value=n_param.Get(zone))
    rw_val=StringVar(value=rw_param.Get(zone))
    a_boxl=ttk.Entry(pk_win,textvariable=a_val)
    m_box=ttk.Entry(pk_win,textvariable=m_val)
    n_box=ttk.Entry(pk_win,textvariable=n_val)
    rw_box=ttk.Entry(pk_win,textvariable=rw_val)

    buttonResponses = Object()
    buttonResponses.done = False
    buttonResponses.cancel = False

    # done
    b_done=Button(pk_win, bg='cyan', text="Submit", command=lambda:(setattr(buttonResponses, 'submit', True), pk_win.quit()))
    b_cancel=Button(pk_win, bg='pink', text='Cancel', command= lambda:(setattr(buttonResponses, 'cancel', True), pk_win.quit()))

    #PLACE WIDGETS
    #Place entry boxes and labels
    a_label.grid(row=0,column=1, pady=10)       # Place entry labels
    m_label.grid(row=2,column=1, pady=10)
    n_label.grid(row=4, column=1, pady=10)
    rw_label.grid(row=6, column=1, pady=10)
    a_boxl.grid(row=0,column=2, pady=10)        #Place min scale entry box 1
    m_box.grid(row=2,column=2, pady=10)
    n_box.grid(row=4,column=2, pady=10)
    rw_box.grid(row=6,column=2, pady=10)

    b_done.grid(row=8, column=2, pady=10)
    b_cancel.grid(row=8, column=3, pady=10)

    pk_win.mainloop()
    if buttonResponses.cancel: #cancel
        # restore graphics window
        self.graphingWindow.deiconify()
        return

    #Update Plot files
    a=float(a_val.get())
    m=float(m_val.get())
    n=float(n_val.get())
    rw=float(rw_val.get())

    #objects are shared by reference, so this applies to global_vars.project.formationZoneParameters
    a_param.Set(zone, a)
    m_param.Set(zone, m)
    n_param.Set(zone, n)
    rw_param.Set(zone, rw)

    global_vars.project.formationZoneParameters.Save()


    pk_win.destroy()

    #close all figs
    for fn in range(1,len(self.figures)+1):
        pyplot.close(fig=fn)

    self.pickettPlot(self.graphingWindow)
    '''
    # restore graphics window
    while tmp[0]!=1:
        pass
    win.deiconify()
    '''