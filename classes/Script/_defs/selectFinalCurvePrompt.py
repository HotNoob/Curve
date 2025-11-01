from tkinter import EW, Button, E, Label, W, ttk

import global_vars
from classes.Object import Object
from defs import common

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Script

#-------------------------------------------------------------------------------------------------------
def selectFinalCurve(self, cvr_list):
    '''
    Select final curve
    '''
    VCL_Fn=self.VCL_Fn
    if VCL_Fn in cvr_list:
        ccurv=VCL_Fn
    else:
        ccurv='None'

    # Set final curve_win toplevel window
    fn_win = common.initCommonWindow(title='Select final curve. Current: ' + ccurv, width=450, height=150, topMost=2)

    fn_lbl=Label(fn_win,text="Select Final Curve")
    fn_box=ttk.Combobox(fn_win,value=cvr_list)

    # done or cancel
    buttonResponses = Object()
    buttonResponses.cancel = False

    b_done=Button(fn_win, bg='cyan', text="Submit", padx=10, command=fn_win.quit)
    b_cancel=Button(fn_win, bg='pink', text='Cancel',padx=10,command= lambda:(setattr(buttonResponses, 'cancel', True), fn_win.quit()))

    fn_lbl.grid(row=0, column=0, padx=15, sticky=EW)
    fn_box.grid(row=1, column=0, padx=15, sticky=EW)
    b_done.grid(row=4, column=0, padx=5,pady=10, sticky=W)
    b_cancel.grid(row=4, column=0, pady=10, sticky=E)

    fn_win.mainloop()

    if buttonResponses.cancel:
        return 
    
    c_fn=fn_box.get()            #get current selection
    
    fn_win.destroy()
    if c_fn=='':
        return None
    return c_fn