'''Las_Win'''

from glob import glob
import os
import threading
from tkinter import Button, Event, IntVar, StringVar, Toplevel, ttk
from typing import TYPE_CHECKING
from defs.prompt import InputFile
from enumerables import Dir

import global_vars
from classes.Object import Object
from defs import alert

if TYPE_CHECKING:
    from .. import LASConverter

def newSettingsMenu(self : 'LASConverter'):
    """ Select options for LAS conversions """

    if self.__class__.workerThread is not None and self.__class__.workerThread.is_alive():
        return alert.Error("Files are already converting, please wait for conversion to finish")

    # First create toplevel window
    # Top level windows
    global_vars.ui.Root.window.update()  # to get the height and the offset of Tk window
    window = Toplevel()
    toplevel1_offsetx = global_vars.ui.Root.window.winfo_x() + global_vars.ui.Root.window.winfo_width()
    toplevel1_offsety = global_vars.ui.Root.window.winfo_y()
    padx = 0  # the padding you need.
    pady = 0
    window.geometry('200x180'+f"+{toplevel1_offsetx + padx}+{toplevel1_offsety + pady}")
    window.resizable(False, False)
    # toplevel1.iconbitmap('Euc.ico')  # File in path (run directory)
    window.title("")
    window.attributes('-topmost', 1)
    window.overrideredirect(1)   # removes window top bar
    """toplevel1.attributes('-toolwindow', True)  # deactivates mini/maximizing """
    # Next create the window widgets
    # Conversion Option Selector TopLevel1
    #region checkbox events
    def checkAllOnChange():    
        if all.get():
            des.set(0)
            nwc.set(0)
            uni.set(0)

    def checkOtherOnChange():
        if all.get():
            all.set(0)

    #endregion checkbox events
    #region checkboxes
    row = 0
    all = StringVar(value='a')
    checkall = ttk.Checkbutton(
                                window, 
                                text="All conversions", 
                                variable=all, 
                                command=checkAllOnChange)
    checkall.grid(column=0, row=row, sticky='we')

    row += 1
    ttk.Separator(window, orient='horizontal').grid(column=0, row=row, sticky='we', columnspan=1)

    row += 1
    des = StringVar()
    checkdesc = ttk.Checkbutton(
                                window, 
                                text="Curve Descriptions", 
                                variable=des, 
                                command=checkOtherOnChange)
    checkdesc.grid(column=0, row=row, sticky='we')

    row += 1
    nwc = StringVar()
    checknew = ttk.Checkbutton(
                                window, 
                                text="New Curves", 
                                variable=nwc, 
                                command=checkOtherOnChange)
    checknew.grid(column=0, row=row, sticky='we')

    row += 1
    uni = StringVar()
    checkunit = ttk.Checkbutton(
                                window, 
                                text="Curve units", 
                                variable=uni, 
                                command=checkOtherOnChange)
    checkunit.grid(column=0, row=row, sticky='we')

    #endregion checkboxes

    row += 1
    sep = ttk.Separator(window, orient='horizontal')
    sep.grid(column=0, row=row, sticky='we', columnspan=2)

    row += 1
    bol = IntVar()
    checkbulk = ttk.Checkbutton(window, text="Bulk - All Files in rawDir", variable=bol)
    checkbulk.grid(column=0, row=row, sticky='we')

    row += 1
    overwriteIntVar = IntVar()
    overwriteCheckbox = ttk.Checkbutton(window, text="Overwrite Files", variable=overwriteIntVar)
    overwriteCheckbox.grid(column=0, row=row, sticky='we')

    buttonResponses = Object()
    buttonResponses.cancel = False

    row += 1
    okButton = Button(window, text="Ok",
                     bg='cyan', command=window.quit)
    okButton.grid(column=0, row=row, sticky='we')

    cancelButton = Button(window, text="Cancel", bg='red', command=lambda: (setattr(buttonResponses, 'cancel', True) , window.quit()))
    cancelButton.grid(column=1, row=row, sticky='we')

    window.mainloop()

    if buttonResponses.cancel:
        window.destroy()
        return

    # get answers
    self.convertAll             = bool(all.get())
    self.convertDescriptions    = bool(des.get())
    self.convertNewCurves       = bool(nwc.get())
    self.convertCurveUnits      = bool(uni.get())

    bulk = bool(bol.get())
    overwrite = bool(overwriteIntVar.get())

    #do all gets before closing
    window.destroy()

    if (    not self.convertAll 
    and not self.convertDescriptions 
    and not self.convertNewCurves 
    and self.convertCurveUnits):
        return #no conversion options selected


    global_vars.ui.Root.c_mylabel.configure(text='Calculating Temperature Gradiant')  # clear my label

    #TGRAD_Av = global_vars.project.projectWellList.CalculateTemperatureGradiantAverage(Dir.In)
    TGRAD_Av = 0.04
    
    if not bulk:
        if not global_vars.inFile:
            alert.Error('Select Input File First! File -> Directories -> Input File')
            InputFile() #prompt for input file. lets do it for them
            if not global_vars.inFile:
                return
        lasFiles = [global_vars.inFile]
    else:
        lasFiles = glob(global_vars.project.rawDir+"/*.las")               #Wells in RAW Dir

    #start conversion
    self.__class__.workerThread = threading.Thread(target=self.las_convert, args=(lasFiles, TGRAD_Av, overwrite))
    self.__class__.workerThread.daemon = True
    self.__class__.workerThread.start()

    while(self.__class__.workerThread.is_alive()):
        with self.__class__.workerLock:
            if self.statusMessage:
                global_vars.ui.Root.c_mylabel.config(text=self.statusMessage)
                self.statusMessage = ''
        
        global_vars.ui.Root.window.update()


    self.statusMessage = f"Converted Files {len(lasFiles)} "
    global_vars.ui.Root.c_mylabel.config(text=self.statusMessage)



