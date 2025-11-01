import os
from tkinter import (END, EW, Button, E, Entry, Label, StringVar, Toplevel, W,
                     filedialog, messagebox, ttk)

import Curve
from classes.Project.Well import Well
import global_vars
from classes.Object import Object

from . import alert, common, excel, las, main


def centerWindow(win : Toplevel):
    ''' requires globals.rootWindow to be set '''
    win_width = win.winfo_width()
    win_height = win.winfo_height()

    screen_width = global_vars.ui.Root.window.winfo_screenwidth()  # Width of the screen
    screen_height = global_vars.ui.Root.window.winfo_screenheight() # Height of the screen

    x = (screen_width // 2) - (win_height // 2)
    y = (screen_height // 2) - (win_height // 2)

    win.geometry('{}x{}+{}+{}'.format(win_width, win_height, x, y))

#----------------------------------------------------------------------------------------------------------------------
def yesno(myquestion):
    '''
     Ask a yes or no question
     returns True for yes and False for no
     '''

    myes=messagebox.askyesno('Yes or No',message=myquestion)
    return myes          #yes=True  no=False

def customButtonPrompt(question : str, buttons : list[str]) -> str:
    '''
        Ask a prompt with any number of buttons, the text in the button will be returned if pressed
    '''
    win = common.initCommonWindow(question, topMost=1, width=270, height=100)
    #create object to record button
    response = Object()
    response.value = ''

    padding = 10
    buttonHeight = 1
    buttonLen = len(buttons)
    colSpan = buttonLen
    if(colSpan > 7):
        colSpan = 7


    row = 0
    Label(win, text=question).grid(padx=padding, pady = padding, sticky='we', columnspan=colSpan)

    row += 1
    col = -1
    for text in buttons:
        col += 1
        if(col % 7 == 0):
            col = 0

        Button(win, text=text, height=buttonHeight, command=lambda t=text: (
            setattr(response, 'value', t),
            win.quit()
            )).grid(row = row, column = col, padx=padding, pady=padding)

    #center the window // call this after so that grid can set the size before centering
    win.after(10, lambda w=win: centerWindow(w))

    win.mainloop()

    win.destroy()

    print("answer: " + response.value)
    return response.value

def customYesNoPrompt(question : str, yesText : str, noText : str) -> bool:
    '''
     Ask a yes or no question
     returns True for yes and False for no
     yesText defines the text for Yes
     noText defines the text for No
     this requires a globals.rootWindow to be set.
     '''

    return (customButtonPrompt(question, [yesText, noText]) == yesText)

def customValuePrompt(question : str, defaultValue : str = '') -> str:
    ''' text prompt value '''
    win = common.initCommonWindow(question, topMost=1, width=270, height=130)
    #create object to record button
    response = Object()
    response.value = ''

    padding = 10
    buttonHeight = 1
    row = 0
    Label(win, text=question).grid(padx=padding, pady=padding, row=row, columnspan=2)

    strVar=StringVar()
    row += 1
    entry = ttk.Entry(win,textvariable=strVar)
    entry.grid(padx=padding, pady=padding, row=row, column=0, columnspan=2)
    if defaultValue:
        entry.insert(0, defaultValue)

    row += 1
    Button(win, 
           text="Submit", 
           height=buttonHeight, 
           command=lambda: (setattr(response, 'value', strVar.get()), win.quit())
           ).grid(row = row, column = 0, padx=padding, pady=padding)
    
    Button(win, 
           text="Cancel", 
           height=buttonHeight, 
           command=win.quit
           ).grid(row = row, column = 1, padx=padding, pady=padding)
    
     #center the window // call this after so that grid can set the size before centering
    win.after(10, lambda w=win: centerWindow(w))
    win.mainloop()
    win.destroy()
    
    return response.value.strip()

def customListPrompt(question : str, values : list[str]) -> str:
    win = common.initCommonWindow(question, topMost=1, width=270, height=130)
    #create object to record button
    response = Object()
    response.value = ''

    padding = 10
    buttonHeight = 1
    row = 0
    Label(win, text=question).grid(padx=padding, pady=padding, row=row, columnspan=2)

    row += 1
    combo = ttk.Combobox(win, value=values)
    combo.grid(padx=padding, pady=padding, row=row, column=0, columnspan=2)

    row += 1
    Button(win, 
           text="Submit", 
           height=buttonHeight, 
           command=lambda : (setattr(response, 'value', combo.get()), win.quit())
           ).grid(row = row, column = 0, padx=padding, pady=padding)
    
    Button(win, 
           text="Cancel", 
           height=buttonHeight, 
           command=win.quit
           ).grid(row = row, column = 1, padx=padding, pady=padding)
    
     #center the window // call this after so that grid can set the size before centering
    win.after(10, lambda w=win: centerWindow(w))
    win.mainloop()
    win.destroy()
    
    return response.value
#---------------------------------------------------------------------------------------------------------
def simpleQuestion(myquestion):
    '''
    return answer on a simple question
    '''
    my_answr=''

    curDir=os.getcwd()
    os.chdir(global_vars.rootDir)

    # Set zone_win toplevel window
    sq_win = common.initCommonWindow('Get Answer', int(len(myquestion)*8.35), 100)

    #Ask question
    sq_lbl = Label(sq_win, text=myquestion)
    var1=StringVar()
    var1.set(my_answr)
    M_entry=ttk.Entry(sq_win,textvariable=var1)

    # done or cancel
    b_done=Button(sq_win, bg='cyan', text="Submit", padx=10, command=sq_win.quit)
    b_cancel=Button(sq_win, bg='pink', text='Cancel',width=10, command=sq_win.quit)

    #place widgets
    sq_lbl.grid(row=0, column=1)
    M_entry.grid(row=1,column=1)

    b_done.grid(row=2, column=0, padx=10, sticky=W)
    b_cancel.grid(row=2, column=2, pady=10, sticky=E)

    sq_win.mainloop()
    #get my_answr
    my_answr=var1.get()

    sq_win.destroy()
    os.chdir(curDir)
    return my_answr


#---------------------------------------------------------------------------------------------------------
# ===============================================================================================
# Input and Output Directories and files
# ===============================================================================================
def InputDir():
    """ DIRECTORY FUNCTIONS INDIR"""

    try:

        global_vars.project.inDir = filedialog.askdirectory(
            title="Please, select an input folder",
            initialdir=global_vars.project.inDir[:-7])

        # Update status line
        main.stat_update(global_vars.project.inDir,0)

        global_vars.ui.Root.Update()  # set up well list  window    

    except FileNotFoundError:
        alert.Error('Directory could not be found. Please, try again.')
    except ValueError:
        alert.Error('File could not be opened. Please, try again.')
#---------------------------------------------------------------------------------------------------------
def OutputDir():
    """ DIRECTORY FUNCTIONS OUTDIR"""

    try:
        global_vars.project.outDir = filedialog.askdirectory(
            title="Please, select a folder to store results",
            initialdir=global_vars.project.inDir[:-7])

        # Update status line
        main.stat_update(global_vars.project.outDir,1)
    except FileNotFoundError:
        alert.Error('Directory could not be found. Please, try again.')
    except ValueError:
        alert.Error('File could not be opened. Please, try again.')
#-----------------------------------------------------------------------------------------------------------
def RawDir():
    """ DIRECTORY FUNCTIONS RAWDIR"""

    try:
        global_vars.project.rawDir = filedialog.askdirectory(
            title="Please, select a folder for RAW (IHS, client) LAS input",
            initialdir=global_vars.project.inDir[:-7])

        # Update status line
        main.stat_update( global_vars.project.rawDir,3)
    except FileNotFoundError:
        alert.Error('Directory could not be found. Please, try again.')
    except ValueError:
        alert.Error('File could not be opened. Please, try again.')
# ----------------------------------------------------------------------------------------------------------
def CoreDir():
    """ DIRECTORY FUNCTIONS COREDIR"""

    try:
        global_vars.project.coreDir = filedialog.askdirectory(
            title="Please, select a folder for Core Input",
            initialdir=global_vars.project.inDir[:-7])

        # Update status line
        main.stat_update( global_vars.project.coreDir,4)
    except FileNotFoundError:
        alert.Error('Directory could not be found. Please, try again.')
    except ValueError:
        alert.Error('File could not be opened. Please, try again.')
# ----------------------------------------------------------------------------------------------------------
def ClientDir():
    """ DIRECTORY FUNCTIONS CLIENT DIR"""

    try:
        global_vars.project.clientDir = filedialog.askdirectory(
            title="Please, select a folder Client data",
            initialdir=global_vars.project.inDir[:-7])


        # Update status line
        main.stat_update( global_vars.project.rawDir,3)
    except FileNotFoundError:
        alert.Error('Directory could not be found. Please, try again.')
    except ValueError:
        alert.Error('File could not be opened. Please, try again.')
    pass
# ----------------------------------------------------------------------------------------------------------
def InputFile():
    """ DIRECTORY FUNCTIONS INPUT FILE"""

    try:
        global_vars.inFile = filedialog.askopenfilename(
            #initialdir = inDir,
            title="Please, select an input file",
            filetype=(("LAS files", "*.las"), ("all files", "*.*"))
        )

        # Update status line
        main.stat_update(global_vars.inFile,2)
    except FileNotFoundError:
        alert.Error('Directory could not be found. Please, try again.')
    except ValueError:
        alert.Error('File could not be opened. Please, try again')


def get_image():
    '''
    Get back ground image for plot
    '''
    myyesno=yesno('Use overlay in plot (y or n)')
    if myyesno==1:                   # INDIR
        imdirc='//HPZ80001-PC/PetraData/Petrophysics/Charts'
        #select image file jpeg or tiff
        Imfile = filedialog.askopenfilename(
            initialdir=imdirc,
            #initialdir='c:/',
            title="Please, select image overlay file",
            filetype=(("Excel files", "*.jpg"), ("all files", "*.*")))
        if Imfile:
            return Imfile
        else:       #if canceled
            return