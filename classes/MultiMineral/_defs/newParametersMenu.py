'''minparms'''
import tkinter.ttk as ttk
from tkinter import (BOTH, END, LEFT, RIGHT, VERTICAL, Button, Canvas, E,
                     Entry, Frame, Label, Y)
from typing import TYPE_CHECKING

import defs.common as common
import global_vars
from classes.Object import Object

if TYPE_CHECKING:
    from ...MultiMineral import MultiMineral

def newParametersMenu(self: 'MultiMineral') -> bool:
    '''
    set base parameters for multiminerals, returns false if menu cancelled
    '''

    #if tmp[0]!=None:   #it not already set in minsettings

    pnam=[]
    pval=[]
    pdes=[]
    plab=[]
    pentry=[]
    mlab=[]

    self.LoadDefaultParameters()
    self.parameters = self.defaltParameters.copy(deep=False)

    '''
    pnam=x_df.iloc[:]['PAR'].tolist()
    pval=x_df.iloc[:]['VAL'].tolist()
    pdes=x_df.iloc[:]['DES'].tolist()
    '''

    mycurve=[]
    for c in range(1,6):
        curveName = self.settings.Get('Curve' + str(c))
        if curveName != 'None':
            mycurve.append(curveName)

    for crv in mycurve:
        #get parameters
        pindex=0
        #remove '_NRM'
        if 'NRM' in crv:
            pcrv=crv[:-4]
        else:
            pcrv=crv
        if pcrv=='RHOB':
            pcrv='RHOM'
        if pcrv=='NPSS':
            pcrv='NPHI'

        for ploc in self.parameters['PAR']:        #loop through Column of Par names
            if pcrv in ploc: #select curve related parms
                pnam.append(self.parameters.iloc[pindex]['PAR'])
                pval.append(self.parameters.iloc[pindex]['VAL'])
                pdes.append(self.parameters.iloc[pindex]['DES'])
            pindex +=1
    pindex -=3 # reset to ratios
    pnam.append(self.parameters.iloc[pindex]['PAR'])
    pval.append(self.parameters.iloc[pindex]['VAL'])
    pdes.append(self.parameters.iloc[pindex]['DES'])
    pindex +=1
    pnam.append(self.parameters.iloc[pindex]['PAR'])
    pval.append(self.parameters.iloc[pindex]['VAL'])
    pdes.append(self.parameters.iloc[pindex]['DES'])
    pindex +=1
    pnam.append(self.parameters.iloc[pindex]['PAR'])
    pval.append(self.parameters.iloc[pindex]['VAL'])
    pdes.append(self.parameters.iloc[pindex]['DES'])

    par_count=len(pnam)     #Number of inputcurves

    #Create Top level window
    # First create toplevel window
    # Top level window
    par_win = common.initCommonWindow(title='Multimineral Analysis Parameters', width=700, height=0.6)

    #window expansion  Does this really work?
    par_win.rowconfigure(0,weight=1)
    par_win.columnconfigure([0,1,2,3],weight=1, uniform=1)

    #create frames
    main_frame=Frame(par_win)
    main_frame.pack(fill=BOTH, expand=1)

    #Create a Canvas within main_frame
    mycanvas=Canvas(main_frame)
    mycanvas.pack(side=LEFT, fill=BOTH, expand=1)

    #Adding a scroll bar
    ans_scrollbar=ttk.Scrollbar(main_frame,orient=VERTICAL,command=mycanvas.yview)
    ans_scrollbar.pack(side=RIGHT, fill=Y)

    #Configure mycanvas
    mycanvas.configure(yscrollcommand=ans_scrollbar.set)
    mycanvas.bind('<Configure>',lambda e: mycanvas.configure(scrollregion=mycanvas.bbox('all')))

    #Create another frame inside mycanvas
    #,text='select parameter to be edited'
    secnd_frame=Frame(mycanvas)

    #Add other second frame to a new window
    mycanvas.create_window((0,0),window=secnd_frame, anchor='nw')

    #Add Entry Widgets
    for c_row in range(par_count):
        plab.append(None)
        pentry.append(None)
        mlab.append(None)

        #create input widget row     if   curvs[c_row].curselect() next row?
        #create a crv_list  - postponed.  You can always copy a curve from one to another directory

        plab[c_row]=Label(secnd_frame,text=pnam[c_row])
        plab[c_row].grid(row=c_row+1, column=0, pady=3)

        pentry[c_row]=Entry(secnd_frame,width=15, borderwidth=5)
        pentry[c_row].delete(0,END)
        pentry[c_row].insert(0,pval[c_row])
        pentry[c_row].grid(row=c_row+1, column=1, pady=3)

        mlab[c_row]=Label(secnd_frame,text=pdes[c_row])
        mlab[c_row].grid(row=c_row+1, column=2, pady=3)

    #ans_frame.configure(yscrollcommand=ans_scrollbar.set)

    buttonResponses : Object = Object()
    buttonResponses.submit = False
    buttonResponses.cancel = False
    buttonResponses.save = False

    # done
    b_done=Button(secnd_frame, bg='cyan', text="Submit", width=10, command=lambda:(setattr(buttonResponses, 'submit', True), par_win.quit()))
    b_cancel=Button(secnd_frame, bg='pink', text='Cancel', width=10, command= lambda:(setattr(buttonResponses, 'cancel', True), par_win.quit()))
    b_save=Button(secnd_frame, bg='palegreen',text='Save', width=10, command=lambda:(setattr(buttonResponses, 'save', True), par_win.quit()))
    '''
    b_load=Button(secnd_frame, bg='palegreen',text='Load', width=10, command= lambda:mlt_load(mlt_set))
    b_load.grid(row=2, column=4, padx=5, pady=5, sticky=E)
    '''
    b_done.grid(row=3,column=4,padx=5, pady=5, sticky=E)
    b_cancel.grid(row=4,column=4,padx=5, pady=5, sticky=E)
    b_save.grid(row=2, column=4, padx=5, pady=5, sticky=E)
    par_win.mainloop()

    #handle button responses
    if  buttonResponses.cancel:
        par_win.destroy()
        return False

    for c_row in range(par_count):
        pval[c_row]=pentry[c_row].get()

    #update x_df
    pindex=0
    lindex=0
    for ploc in self.parameters['PAR']:        #loop through Column of Par names
        lindex=0    #reset pnam pval list index
        for pm in pnam:         #for each x_df item loop through the Pnam list
            if pm in self.parameters.iloc[pindex]['PAR']: #found pnam in x_df
                self.parameters.iloc[pindex,1]=float(pval[lindex])
            lindex +=1
        pindex +=1

    if buttonResponses.save:    #save
        self.SaveDefaultParameters()
        
    #call multimineral x_df is global
    par_win.destroy()
    self.analyze()