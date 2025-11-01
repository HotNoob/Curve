''' c_zones - class to edit excel spreadsheets'''

import os
from tkinter import BOTTOM, DISABLED, END, NORMAL, RIGHT, X, Y, Button, Entry, Frame, Label, LabelFrame, Scrollbar, ttk

import pandas as pd
from defs import common, excel
import global_vars

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tkinter import Toplevel


class ExcelEditor:
    def __init__(self, file : str) -> None:
        self.file : str = file

        self.df : pd.DataFrame = None

         #Create new top level window Z_window
        self.window : Toplevel = common.initCommonWindow(title='Examine or edit file', width=1, height=800, topMost=2)

        self.selectedRow = -1
        self.selectedCol  = -1

        # Create treeview frame
        my_frame=Frame(self.window)
        my_frame.pack()

        tvscrollbarY=Scrollbar(my_frame, orient='vertical')
        tvscrollbarY.pack(side=RIGHT, fill=Y)

        tvscrollbarX=Scrollbar(my_frame, orient='horizontal')
        tvscrollbarX.pack(side=BOTTOM, fill=X)

        self.treeview=ttk.Treeview(my_frame, yscrollcommand=tvscrollbarY.set, xscrollcommand=tvscrollbarX.set ,height=25, selectmode='browse')
        self.treeview.pack()

        tvscrollbarX.config(command=self.treeview.xview)
        tvscrollbarY.config(command=self.treeview.yview)


        edit_frame=LabelFrame(self.window, text="Edit Selected Item")
        edit_frame.pack(pady=10)

        myLabl=Label(edit_frame,text='')
        myLabl.pack(pady=10)

        myEntry=Entry(edit_frame,text="")
        myEntry.pack(pady=10)

        #Update Button
        myButton = Button(edit_frame, text="Update records", state=DISABLED ,command = lambda : self.zupdate(self.treeview, myButton, myEntry))
        myButton.pack(pady=10)

        self.treeview.bind("<Double-1>", lambda e: self.onDoubleClick(self.treeview, myEntry, myButton, myLabl, e))

    def Load(self):
        ''' loads / updates the data / view'''

        self.df = pd.read_excel(os.path.abspath(self.file))

        # clear any pre-existing tree view data
        self.treeview.delete(*self.treeview.get_children())

         # set up new tree view
        self.treeview['column']=list(self.df.columns)
        self.treeview['show']='headings'

        #loops through 'column' list for headers
        for column in self.treeview['column']:
            self.treeview.heading(column, text=column)

        # put data in my_treeview rows
        df_rows = self.df.to_numpy().tolist()
        for row in df_rows:
            self.treeview.insert('','end',values=row)

        #update window title
        self.window.title(f'Examine or edit file - {self.file}')

    def Show(self):
        ''' blocking'''
       
        if self.df == None: #autoload if not loaded
            self.Load()

        #---------blocking----------#
        self.window.mainloop()

    #-------------------------------------------------------------------------------------------------------------
    def onDoubleClick(self, treeview : ttk.Treeview, myentry, mybutton, mylabl, event):
        '''
        set edit frame, labels and entryboxes
        '''
        
        self.selectedRow=treeview.identify_row(event.y)               #row in tree
        self.selectedCol=int(treeview.identify_column(event.x)[1:])-1               #col in df

        mylabl.config(text=treeview['column'][self.selectedCol])

        #Edit value
        values=treeview.item(self.selectedRow,'values')

        #Output to Entry Box
        myentry.insert(0,values[self.selectedCol])

        mybutton.configure(state=NORMAL)            #activate update button in edit_frame
    #-------------------------------------------------------------------------------------------------------------
    def zupdate(self, my_tv, myButton, myentry):
        '''
        update treeview and save changes to file
        '''
        # get change
        changed=myentry.get()
        # empty Entry Box
        myentry.delete(0,END)

        #get vslues list in row
        #copy new values
        newvalues=list(my_tv.item(self.selectedRow,'values')).copy()


        #Update the treeview
        newvalues[self.selectedCol]=changed
        my_tv.item(self.selectedRow,text="",values=newvalues)

        #update data frame and save to spreadsheet
        ''' reload the dataframe from excel and then change the now original data frame and save it.  CRAZY  making a 'deep or shallow copy does not work'''

        self.selectedRow=int(self.selectedRow[1:])-1

        #apply changes to df
        self.df.iloc[self.selectedRow,self.selectedCol]=changed

        #save df to file
        self.df.to_excel(self.file,index=False)

        #todo, reload changes

        myButton.configure(state=DISABLED)
        return
    # ====================================================================================================