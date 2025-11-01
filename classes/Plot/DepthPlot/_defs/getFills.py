'''get_fills'''
import tkinter.ttk as ttk
from tkinter import Button, E, Label, W
from typing import TYPE_CHECKING

import defs.common as common
import global_vars

from classes.Object import Object

if TYPE_CHECKING:
    from .. import DepthPlot

#---------------------------------------------------------------------------------------------------------------------------------
def getFills(self : 'DepthPlot',lines,pr_jmp, mprops : list,curv, idx, trk_list, color_list) -> list:
    '''
    Get fill properties and update myprops before returning
    '''

    #alpha list
    alp_list=[0, 0.10, 0.20,0.30,0.40,0.50,0.60,0.70,0.80,0.90, 1]

    #Open toplevel form
    fill_win = common.initCommonWindow(f'Fill settings for {curv}', int(global_vars.ui.Root.window.winfo_screenwidth()*0.25), int(global_vars.ui.Root.window.winfo_screenheight()*0.25))

    #window expansion  Does this really work?
    fill_win.rowconfigure([0,1,2,3,4,5,6,7],weight=1)
    fill_win.columnconfigure(1,weight=1)
    trkl_idx=0
    col_idx=0
    gt_idx=0
    alp_idx=0
    if lines!=[]:               #if fill settings in dpt file
        #copy fill settings into toplevel widgets
        line=lines[idx+pr_jmp+2][:-1].split(',')
        if line[7]=='None' or line[7]=='':
            trkl_idx=0
            trk_list[0]='Constant = ' + line[8]
        else:
            for tr in trk_list:
                if tr==line[7]:
                    break
                trkl_idx +=1
            trkl_idx -=1      #correct for final loop

        if line[9]!='':
            gt_idx=int(line[9])

        if line[10]!='':
            mcolor=line[10]
            for c in color_list:
                if c==mcolor:
                    break
                col_idx +=1

        if line[10]!='':
            alph = round(float(line[11]),1)
            for a in alp_list:
                if a==alph:
                    break
                alp_idx += 1

    crvlbl = Label(fill_win,text='Select constant or second curve:')
    crvbox = ttk.Combobox(fill_win, values=trk_list)
    crvlbl.grid(row=0, column=1, sticky=W)
    crvbox.current(trkl_idx)
    crvbox.grid(row=1, column=1, pady=3, padx=5, sticky=E)
    gtlbl = Label(fill_win,text='Greater or less than above curve:')
    gtbox = ttk.Combobox(fill_win, values=['none','greater', 'less'])
    gtbox.current(gt_idx)
    gtlbl.grid(row=2, column=1, sticky=W)
    gtbox.grid(row=3, column=1, pady=3, padx=5, sticky=E)
    collbl = Label(fill_win,text='Select fill color')
    colbox = ttk.Combobox(fill_win, values=color_list)
    colbox.current(col_idx)
    collbl.grid(row=4, column=1, sticky=W)
    colbox.grid(row=5, column=1, pady=3, padx=5, sticky=E)
    alplbl = Label(fill_win,text='Degree of transparancy (0 - 1; average = 0.5)')
    alpbox = ttk.Combobox(fill_win, values=alp_list)
    alpbox.current(alp_idx)
    alplbl.grid(row=6, column=1, sticky=W)
    alpbox.grid(row=7, column=1, pady=3, padx=5, sticky=E)

    buttonResponses : Object = Object()
    buttonResponses.done = False
    buttonResponses.cancel = False

    b_done=Button(fill_win, text="Submit",bg='cyan', command= lambda:(setattr(buttonResponses, 'done', True), fill_win.quit()))
    b_done.grid(row=8,column=1, pady=5,sticky=E)

    b_cancel=Button(fill_win, text="Cancel",bg='pink', command= lambda:(setattr(buttonResponses, 'cancel', True), fill_win.quit()))
    b_cancel.grid(row=8,column=1, padx=10, pady=5,sticky=W)

    fill_win.mainloop()

    #Cancel
    if buttonResponses.cancel:
        fill_win.destroy()
        return [] #return empty of cancel

    # update mprops
    myconstant=''
    fill_crv=crvbox.get()
    if 'Constant' in fill_crv:
        if myconstant != '':
            myconstant=fill_crv.strip(' ')  #remove all blanks
            myconstant= round(float(myconstant[10:]),4)
            mprops[idx][7]='None'
            mprops[idx][8]=myconstant
        else:
            mprops[idx][7]=crvbox.get()
            mprops[idx][8]='None'
    else:
        mprops[idx][7]=crvbox.get()
        mprops[idx][8]='None'

    gtr=gtbox.get()
    if gtr=="greater":
        mprops[idx][9]=1
    elif gtr=="less":
        mprops[idx][9]=2
    else:
        mprops[idx][9]=0
    col=colbox.get()
    if col=='':
        col='yellow'
    mprops[idx][10]=col

    alpha=alpbox.get()
    if alpha=='':
        alpha=0.5
    mprops[idx][11]=float(alpha)

    fill_win.destroy()
    return mprops