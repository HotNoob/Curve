#this file holds common defs

import os
from tkinter import PhotoImage, Toplevel
from typing import Union  # use union until python 3.10

import global_vars

def listIndexOf(list : list, value, notFound = -1):
    try:
        return list.index(value)
    except ValueError:
        return notFound
        
def initCommonWindow(title : str = '', width : Union[int, float] = 600, height : Union[int, float] = 430, topMost : int = 1, x : Union[int, float] = -1, y : Union[int, float] = -1) -> Toplevel:
    '''creates a common Toplevel Window/Widget with Euc.ico and so forth.
        width and height can be an int for absolute size, or a float for a percentage of the screen size. ie: 0.25f for 25%
        y and x, by default center the window. if y or x is set with a int, position will be absolute, if float, position will be percentage of screen size
    '''

    screenWidth = global_vars.ui.Root.window.winfo_screenwidth()
    screenHeight = global_vars.ui.Root.window.winfo_screenheight()

    if(width <= 1 or (isinstance(width, float) and width < 2)):
        width = screenWidth * width

    if(height <= 1 or (isinstance(height, float) and height < 2)):
        height = screenHeight * height

    win = Toplevel()
    win.protocol("WM_DELETE_WINDOW", lambda:  win.quit()) #bug fix?

    #by default center
    if(x == -1):
        if(x <= 1):
            x=screenWidth/2 - width/2
        else:
            x=screenWidth*x

    if(y == -1):
        if(y <= 1):
            y=screenHeight/2 - height/2
        else:
            y=screenHeight*y


    win.geometry(f"{int(width)}x{int(height)}+{int(x)}+{int(y)}")
    win.attributes('-topmost', topMost)

    win.title(title)

    #iconphoto for linux compatability
    #win.iconbitmap(globals.rootDir + '/Euc.ico')
    win.iconphoto(False, PhotoImage(file=global_vars.rootDir+'/Euc.png'))

    return win

def cleanUWI(uwi : str):
    '''cleans input uwi, trim, upper, and remove file extensions'''
    dot = uwi.rfind('.') #find and remove file extension
    if(dot > 0):
        uwi = uwi[:dot]

    return uwi.strip().upper()

def cleanWellAlias(alias : str):
    '''cleans input alias / number'''

    alias = alias.lstrip('0') #remove padding
    alias = alias.zfill(4) #add padding

    return alias

    dot = alias.rfind('.') #find and remove file extension
    if(dot > 0):
        alias = alias[:dot]

    return alias.strip().upper().replace(' ', '_')

def cleanPath(path : str) -> str: 
    path = os.path.abspath(path)
    path = os.path.normpath(path)
    path = path.replace('\\', '/')
    if "." in os.path.basename(path) and os.path.isfile(path):
        path = os.path.dirname(path)
    return path