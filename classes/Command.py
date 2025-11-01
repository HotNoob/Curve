import tkinter as tk
from tkinter import (END, Button, Entry, Label, filedialog, messagebox, StringVar)
from typing import Type

import numpy as np
from enumerables import Dir

from tkinter import ttk

import global_vars
from defs import alert, common, las, prompt,program


class Command:
    def __init__(self):
        self.lines : list[str] = []

    @classmethod
    def newCommand(cls : Type['Command'] ) -> 'Command':
        newCommand = cls()
        newCommand.newCommandMenu()
        return newCommand
    
    def newCommandMenu(self):
        '''
        make_scripts
        Create and run scripts for simple calculations
        '''
        global_vars.ui.Root.window.iconify()
        #create top level window to enter a quick script
        # Set List Dir toplevel window
        scp_win = common.initCommonWindow(title='Quick Scripts', width=425, height=250, topMost=2)

        #Save or get command line file

        #LoadCommand
        mLoadCom= Button(scp_win, text="Load Command File", command = lambda: self.load_cmnd(myEntry))
        mLoadCom.grid(column=1,row=3, pady=20, padx=15)

        #mcommandline='Enter command line'
        myLabel=Label(scp_win,text='Enter a command line:')
        myLabel.grid(column=1,row=1, pady=10)
        myEntry=Entry(scp_win,width=40, borderwidth=5)
        myEntry.grid(column=0,row=2, columnspan=3)

        #SaveCommand
        mSaveCom= Button(scp_win, text="Save Command File", command = lambda: self.save_cmnd(myEntry))
        mSaveCom.grid(column=0,row=3, pady=20, padx=15)

        #Done Buttonb
        b_done = Button(scp_win,bg='cyan', text="Run", width= 10, command = lambda : self.scp_done(scp_win, myEntry))
        b_done.grid(column=1,row=4, pady=20, padx=15)
        
        #Cancel Button
        b_cancel = Button(scp_win,bg='pink', text="Cancel", width= 10, command = scp_win.quit)
        b_cancel.grid(column=2,row=4, pady=20, padx=15)

        scp_win.mainloop()
        scp_win.destroy()
        global_vars.ui.Root.window.deiconify()

        #save as a py file using lines of text
        # run in Jupitor Note Book
    #-------------------------------------------------------------------------------------------------------
    def scp_done(self, scp_win,myEntry):
        '''
        Get command line - parse and loop through Well_List with interpreter
        '''      
        global_vars.func_id = []
        '''
        #CREATE CURVE LISTS
        # create curve lists
        core_flag = 0
        inDirCurves : set = global_vars.project.currentWellList.GetCommonCurves(Dir.In) - {'DEPT'}
        coreCurves : set = set()

        for well in global_vars.project.currentWellList.GetWells():
            if well.GetWellFile(Dir.In, '.cas') is not None:
                core_flag = 1
                coreCurves = set(global_vars.cdescrvs) - {'DEPT', 'S_TP','S_TCK', 'COREDEPT','SAMPLE','ACCESSORIES','SEDSTRUCT'} - inDirCurves 
                break

        outDirCurves : set = global_vars.project.currentWellList.GetCommonCurves(Dir.Out) - {'DEPT'} - inDirCurves

        crv_list = list(inDirCurves) + ['CORE DATA'] + list(coreCurves) + ['OUTDIR CURVES'] + list(outDirCurves)
        clist= StringVar()
        clist.set(value=crv_list)
        
        #Create Top level window
        selcrv_win = common.initCommonWindow(title='Select Input Curve', width=100, height=200, topMost=2)
        

        #Select Curve'
        crv_list_length = len(crv_list)            
        if(crv_list_length > 0):
            crv_bx = tk.Listbox(selcrv_win, listvariable=clist, height=20, selectmode='browse')
            crv_bx.pack(expand=True, padx=10, pady=10, fill=tk.BOTH, side='left')
            crv_list_defaults=100

        # link a scrollbar to a list
            scrollbar = ttk.Scrollbar(
            crv_bx,
            orient=tk.VERTICAL,
            ycommanL=crv_bx.yview
            )

            crv_bx['yscrollcommand'] = scrollbar.set

            scrollbar.pack(side=tk.LEFT, expand=True, fill=tk.Y)
        '''
        
        #COMMAND PARSER
        terms=myEntry.get().split(" ")
        t_len=len(terms)
        scp_win.destroy()

        #create list of common curves
        crvnames=[]
        no_crvs=['DEPT']
        crvnames=program.com_crvs(no_crvs,crvnames,0)

        D_bug=0    #Not yet debugged
        for well in global_vars.project.currentWellList.GetWells():      #Loop through well_list
            yn=False
            #get lass file from OutDir use only approved curves
            lasData = well.GetLASData(Dir.Out)
            global_vars.las_df=lasData.df()
            if D_bug==0:
                #DEBUGGER
                for Tm in range(t_len):
                    myErr=1
                    if len(terms[Tm])>1:     #possible bug
                        if terms[Tm] in crvnames:  #calculated curve
                            myErr=0    # no Error
                        if self.is_number(terms[Tm]):
                            myErr=0    # no Error
                        if myErr == 1:
                            myTXT = terms[Tm] + ' Possible Curve or Number error - Continue?'
                            MsgBox = messagebox.askquestion (message=myTXT,icon = 'warning')
                            if MsgBox == 'yes':
                                myErr = 0    # New Curve Name
                    else:
                        if terms[Tm] in '=+-*/^()':          #Not an operator
                            myErr=0    # no Error
                        if self.is_number(terms[Tm]):
                            #at first sight fine
                            myErr=0
                            if Tm == t_len-1:
                                continue
                            if self.is_number(terms[Tm+1]):
                                myErr=1     # missing operator
                                global_vars.ui.Root.window.deiconify()
                                alert.RaiseException(terms[Tm] + "and "+ terms[Tm+1] +"   Miss operator - edit command line")
                            if terms[Tm] in crvnames:
                                myErr=0      #One letter curvename?
                    if myErr==1:    #general Error
                        global_vars.ui.Root.window.deiconify()
                        alert.RaiseException(terms[Tm] + " Syntax Error - edit command line")
                D_bug=1     #Debugged
            Ans=[]      #Reset Answer curves
            Aid=0
            Tid=0

            if terms[Tid] not in crvnames:         #create new curve
                global_vars.las_df[[terms[Tid]]]=np.nan
            Ans.append(global_vars.las_df[terms[Tid]])   #pointer to las_df

            Tid +=1   #Next terms
            if terms[Tid]!='=':       #if 2nd terms not = then return error
                global_vars.ui.Root.window.deiconify()
                alert.RaiseException(" Second command line item MUST be '=' ")

            Tid +=1 #Next terms
            global_vars.func_id.append('start')
            while Tid<t_len-1:
                Tid_fl=0
                Ans,Aid,Tid = self.get_nexT(Ans,Aid, Tid, terms, crvnames, t_len,Tid_fl)
            Ans[Aid-1].iloc[:]=Ans[Aid].iloc[:]      #update las_df
            Aid -=1             #Get Aid to equal 0
            if Aid != 0:    #Aid should be 0
                #level of precendence problem
                alert.RaiseException(f'{Aid} should be 0 - precedence problem in script')
            #save las_df
            yn = prompt.yesno("Save results, yes or no ")
            if yn==True:
                lasData.set_data(global_vars.las_df)    #update las_data
                las.save_curves(well.uwi + ".las", Ans[Aid].name, Ans[Aid].name)

            #Done with interpreter calculations    
            
            alert.Message("Scan")   
            global_vars.project.Scan ()
            alert.Message("Updating Project")
            global_vars.ui.Root.Update()  
            global_vars.ui.Root.window.deiconify()

    
    #-------------------------------------------------------------------------------------------------------
    def load_cmnd(self, myEntry):
        try:
            Infile = filedialog.askopenfilename(
                initialdir = global_vars.project.inDir + '/databases',
                title="Please, select a command file",
                filetype=(("command files", "*.cmdl"), ("all files", "*.*"))
                )
        except FileNotFoundError:
            alert.Error('Directory could not be found. Please, try again.')
        except ValueError:
            alert.Error('File could not be opened. Please, try again.')
        if Infile==None:                     #canceled
            return
        with open(Infile, "r", encoding=global_vars.fileEncoding) as f:
            mcommandline = f.readlines()
        #Ask for Command Line
        if mcommandline=='':
            return
        #Done
        myEntry.delete(0,END)
        myEntry.insert(0,mcommandline[0])
    #-------------------------------------------------------------------------------------------------------
    def save_cmnd(self, myEntry):

        mpath = global_vars.project.inDir + '/databases'
        try:
            Infile = filedialog.asksaveasfile(
                initialdir = mpath,
                mode='w',
                confirmoverwrite=True,
                defaultextension="*.cmdl",
                title="Please, select a command file",
                filetypes=(("Command files", "*.cmdl"), ("all files", "*.*"))
                )
        except FileNotFoundError:
            alert.Error('Directory could not be found. Please, try again.')
        except ValueError:
            alert.Error('File could not be opened. Please, try again.')
        if Infile==None:                     #canceled
            return

        mcommandline=myEntry.get()
        #with open(Infile,'w') as f:
        # write settings to project file
        Infile.write(mcommandline)
    #-------------------------------------------------------------------------------------------------------
    def get_nexT(self, Ans,Aid, Tid, mterms, crvnames, tlen, Tid_fl):

        global_vars.func_id.append(mterms[Tid])                # count returns
        if mterms[Tid]=='(':       #opening brackets
            crv_fl=0               #opening brackets
            if mterms[Tid+1] in crvnames:
                Tid +=1
                Ans.append(global_vars.las_df[mterms[Tid]].copy())
                Aid +=1 #Next order of preference
                Tid +=1  #Get ready for next term
                Tid_fl=1
                crv_fl=1

                if Tid>=tlen-1:
                    global_vars.ui.Root.window.deiconify()
                    alert.RaiseException(" No closing bracket - edit command line")
            if self.is_number(mterms[Tid+1])and crv_fl==0:
                Tid +=1
                Ans.append(global_vars.las_df[mterms[0]].copy())   # create series length Ans[0]
                Aid +=1 #next precedent level
                Ans[Aid].name=mterms[Tid]
                Ans[Aid].iloc[:] = float(mterms[Tid])
                Tid +=1  #Get ready for next term
                Tid_fl=1
                if Tid>=tlen-1:  #last term not a closing braket
                    global_vars.ui.Root.window.deiconify()
                    alert.RaiseException(" No closing bracket - edit command line")
        if mterms[Tid]==')':                #closing brackets
            Tid +=1
            if Tid>=tlen-1:   # if no next term
                Tid = tlen-1        #Reset to final term
                del global_vars.func_id[-1]
                return Ans, Aid, Tid
            Tid_fl=0 #Reset Tid error flag
        if mterms[Tid] in crvnames:
            Ans.append(global_vars.las_df[mterms[Tid]].copy())
            Aid +=1
            Tid +=1 #next terms
            if Tid>=tlen-1:   # if no next term
                Tid = tlen-1        #Reset to final term

            Tid_fl=1
        if self.is_number(mterms[Tid]):
            Ans.append(global_vars.las_df[mterms[0]].copy())   # create series length Ans[0]
            Aid +=1 #next precedent level
            Ans[Aid].name=mterms[Tid]
            Tid +=1 #next terms
            if Tid>=tlen-1:   # if no next term
                Tid = tlen-1        #Reset to final term
                del global_vars.func_id[-1]
                return Ans, Aid, Tid
            Tid_fl=1

        if mterms[Tid] == '+':
            #Is there a base number or curve prior to +
            Tid -=1
            if mterms[Tid] =='(' or mterms[Tid-1] in '=+-*/^()': #If a new level of precedence
                if Ans[Aid].name != mterms[Tid]:   #If curve not yet created
                    if mterms[Tid] in crvnames:
                        Ans.append(global_vars.las_df[mterms[Tid]].copy())
                        Aid +=1 #Add curve
                if self.is_number(mterms[Tid]):
                    if Ans[Aid].name != mterms[Tid]:   #If curve with number not yet created
                        Aid +=1
                        Ans.append(global_vars.las_df[Ans[0].name].copy())
                        Ans[Aid].iloc[:] =float(mterms[Tid])
                        Ans[Aid].name=mterms[Tid]

            # get addition
            Tid +=2
            if mterms[Tid] in crvnames:
                Aid +=1 #Add curve
                Ans.append(global_vars.las_df[mterms[Tid]].copy())
                Tid +=1 #Add term
                if Tid>=tlen-1:   # if no next term
                    Tid = tlen-1        #Reset to final term
            if self.is_number(mterms[Tid]):
                Aid +=1
                Ans.append(global_vars.las_df[Ans[0].name].copy())
                Ans[Aid].name=mterms[Tid]
                Ans[Aid].iloc[:] =float(mterms[Tid])
            if tlen>Tid+1:  #if not at end of terms
                if mterms[Tid+1] in'=+-*/^(':     #Next level of preference
                    Tid +=1
                    Tid_nw=0
                    Ans, Aid, Tid = self.get_nexT(Ans,Aid, Tid, mterms, crvnames, tlen, Tid_nw)   #Nesting function
            old_name = Ans[Aid-1].name
            #ready to add
            Ans[Aid-1]=Ans[Aid-1]+Ans[Aid]
            Ans[Aid-1].name=old_name
            del Ans[-1]
            Aid -=1
            #if mterms[Tid-1] not in "+-":        #if not operator
            Tid +=1
            if tlen>Tid+1:  #if not at end of terms
                if mterms[Tid+1]!='^' and mterms[Tid+1]!='*' and mterms[Tid+1]!='/': #of precedential operator follows skip
                    if mterms[Tid] in crvnames:
                        if len(Ans)<Aid:
                            Ans[Aid] += Ans[Aid+1]
                        else:
                            Ans[Aid] = Ans[Aid] + Ans[Aid-1] #Add constant prior to curve
                    if self.is_number(mterms[Tid]):
                        Ans[Aid] +=float(mterms[Tid])
                        Ans[Aid].name=str(Ans[Aid].iloc[0])
            else:           #if final term it must be a ) or number or curve
                if tlen==Tid:   #Done
                    Tid = tlen-1 # reset to final term
                    del global_vars.func_id[-1]
                    return Ans, Aid, Tid
                if mterms[Tid] in crvnames:
                    #create final curve
                    Ans.append(global_vars.las_df[mterms[Tid]].copy())
                    Aid +=1 #Next order of preference
                    Tid +=1  #Get ready for next term
                    Tid_fl=1
                    crv_fl=1
                    if Tid>=tlen-1:   # if no next term
                        Tid = tlen-1        #Reset to final term

                if tlen>Tid+1:   #if not end of terms
                    if mterms[Tid+1] == '(':    # next level of precendence
                        Tid +=1
                    elif mterms[Tid] == ')':    #next operation
                        pass                #keep Tid
                    else:
                        Tid -=1
                    Tid_nw=0
                    Ans, Aid, Tid =self.get_nexT(Ans,Aid, Tid, mterms, crvnames, tlen, Tid_nw)   #Nesting function
                if Aid<2:  #if precedence level back to 1
                    #No previous operations
                    del global_vars.func_id[-1]
                    return Ans, Aid, Tid
                #complete previous operation
                Ans, Aid, Tid = self.comp_op(Ans, Aid, Tid, mterms,tlen,Tid_fl)

        if mterms[Tid] == '-':
            #Is there a base number or curve prior to +
            Tid -=1
            if mterms[Tid] =='(' or mterms[Tid-1] in '=+-*/^()': #If a new level of precedence
                if Ans[Aid].name != mterms[Tid]:   #If curve not yet created
                    if mterms[Tid] in crvnames:
                        Ans.append(global_vars.las_df[mterms[Tid]].copy())
                        Aid +=1 #Add curve
                if self.is_number(mterms[Tid]):
                    if Ans[Aid].name != mterms[Tid]:   #If curve with number not yet created
                        Aid +=1
                        Ans.append(global_vars.las_df[Ans[0].name].copy())
                        Ans[Aid].iloc[:] =float(mterms[Tid])
                        Ans[Aid].name=mterms[Tid]

            # getsubstract
            Tid +=2
            if mterms[Tid] in crvnames:
                Aid +=1 #Add curve
                Ans.append(global_vars.las_df[mterms[Tid]].copy())
                Tid +=1 #Add term
                if Tid>=tlen-1:   # if no next term
                    Tid = tlen-1        #Reset to final term
            if self.is_number(mterms[Tid]):
                Aid +=1
                Ans.append(global_vars.las_df[Ans[0].name].copy())
                Ans[Aid].name=mterms[Tid]
                Ans[Aid].iloc[:] =float(mterms[Tid])
            if tlen>Tid+1:  #if not at end of terms
                if mterms[Tid+1] in'=+-*/^(':     #Next level of preference
                    #Aid +=1
                    Tid +=1
                    Tid_nw=0
                    Ans, Aid, Tid =self.get_nexT(Ans,Aid, Tid, mterms, crvnames, tlen, Tid_nw)   #Nesting function
            old_name = Ans[Aid-1].name
            #ready to subtract
            Ans[Aid-1]=Ans[Aid-1]-Ans[Aid]
            Ans[Aid-1].name=old_name
            del Ans[-1]
            Aid -=1
            if mterms[Tid] not in "+-":        #if not operator
                Tid +=1
            if tlen>Tid+1:  #if not at end of terms
                if mterms[Tid+1]!='^' and mterms[Tid+1]!='*' and mterms[Tid+1]!='/': #of precedential operator follows skip
                    if mterms[Tid] in crvnames:
                        if len(Ans)<Aid:
                            Ans[Aid] += Ans[Aid+1]
                        else:
                            Ans[Aid] = Ans[Aid] + Ans[Aid-1] #Add constant prior to curve
                    if self.is_number(mterms[Tid]):
                        Ans[Aid] +=float(mterms[Tid])
                        Ans[Aid].name=str(Ans[Aid].iloc[0])
            else:           #if final term it must be a ) or number or curve
                if tlen==Tid:   #Done
                    Tid = tlen-1 # reset to final term
                    del global_vars.func_id[-1]
                    return Ans, Aid, Tid
                if mterms[Tid] in crvnames:
                    #create final curve
                    Ans.append(global_vars.las_df[mterms[Tid]].copy())
                    Aid +=1 #Next order of preference
                    Tid +=1  #Get ready for next term
                    Tid_fl=1
                    crv_fl=1
                    if Tid>=tlen-1:   # if no next term
                        Tid = tlen-1        #Reset to final term

                if tlen>Tid+1:   #if not end of terms
                    if mterms[Tid+1] == '(':    # next level of precendence
                        Tid +=1
                    elif mterms[Tid] == ')':    #next operation
                        pass                #keep Tid
                    else:
                        Tid -=1
                    Tid_nw=0
                    Ans, Aid, Tid = self.get_nexT(Ans,Aid, Tid, mterms, crvnames, tlen, Tid_nw)   #Nesting function

                if Aid<2:  #if precedence level back to 1
                    #No previous operations
                    del global_vars.func_id[-1]
                    return Ans, Aid, Tid

                Ans, Aid, Tid = self.comp_op(Ans, Aid, Tid, mterms,tlen,Tid_fl)

        if mterms[Tid] == '*':          #special rules of precendenc
            #Is there a base number or curve prior to *
            Tid -=1
            if mterms[Tid] =='(' or mterms[Tid-1] in '=+-*/^()': #If a new level of precedence
                if Ans[Aid].name != mterms[Tid]:   #If curve not yet created
                    if mterms[Tid] in crvnames:
                        Ans.append(global_vars.las_df[mterms[Tid]].copy())
                        Aid +=1 #Add curve
                if self.is_number(mterms[Tid]):
                    if Ans[Aid].name != mterms[Tid]:   #If curve with number not yet created
                        Aid +=1
                        Ans.append(global_vars.las_df[Ans[0].name].copy())
                        Ans[Aid].iloc[:] =float(mterms[Tid])
                        Ans[Aid].name=mterms[Tid]

            # get multiplier
            Tid +=2
            if mterms[Tid] in crvnames:
                Aid +=1 #Add curve
                Ans.append(global_vars.las_df[mterms[Tid]].copy())
                Tid +=1 #Add term
                if Tid>=tlen-1:   # if no next term
                    Tid = tlen-1        #Reset to final term

            if self.is_number(mterms[Tid]):
                Aid +=1
                Ans.append(global_vars.las_df[Ans[0].name].copy())
                Ans[Aid].name=mterms[Tid]
                Ans[Aid].iloc[:] =float(mterms[Tid])
            if mterms[Tid]=='(':     #Next level of preference
                Aid +=1
                Tid +=1
                Tid_nw=0
                Ans, Aid, Tid = self.get_nexT(Ans,Aid, Tid, mterms, crvnames, tlen, Tid_nw)   #Nesting function

            #ready to Multiply
            Ans[Aid-1]=Ans[Aid-1]*Ans[Aid]
            if Ans[Aid-1].name not in crvnames:
                if Ans[Aid].name in crvnames:
                    Ans[Aid-1].name=Ans[Aid].name

            del Ans[-1]
            Aid -=1 #restore order of preference
            Tid +=1     #next terms
            if Tid>=tlen-1:   # if no next term
                Tid = tlen-1        #Reset to final term
                del global_vars.func_id[-1]
                return Ans, Aid, Tid
            Tid_fl=1
            if tlen>Tid+1:   #if not end of terms
                if mterms[Tid+1] == '(':    # next level of precendence
                    Tid +=1
                elif mterms[Tid] == ')':    #next operation
                    del global_vars.func_id[-1]
                    return Ans, Aid, Tid    #previous level of precedence
                else:
                    Tid -=1
                Tid_nw=0
                Ans, Aid, Tid = self.get_nexT(Ans,Aid, Tid, mterms, crvnames, tlen, Tid_nw)   #Nesting function/Next precedenc level

            if Aid<2:  #if precedence level back to 1
                #No previous operations
                del global_vars.func_id[-1]
                return Ans, Aid, Tid
            #complete previous operation
            Ans, Aid, Tid = self.comp_op(Ans, Aid, Tid, mterms,tlen, Tid_fl)

        if mterms[Tid] == '/':      #special rules of precendenc
            #Is there a base number or curve prior to /
            Tid -=1
            if mterms[Tid] =='(': #If a new level of precedence
                if Ans[Aid].name != mterms[Tid]:   #If curve not yet created
                    if mterms[Tid] in crvnames:
                        Ans.append(global_vars.las_df[mterms[Tid]].copy())
                        Aid +=1 #Add curve
                if self.is_number(mterms[Tid]):
                    if Ans[Aid].name != mterms[Tid]:   #If curve not yet created
                        Aid +=1
                        Ans.append(global_vars.las_df[Ans[0].name].copy())
                        Ans[Aid].name=mterms[Tid]
                        Ans[Aid].iloc[:] =float(mterms[Tid])
            # get divider
            Tid +=2
            if mterms[Tid] in crvnames:
                Aid +=1 #Add curve
                Ans.append(global_vars.las_df[mterms[Tid]].copy())
                Tid +=1 #Add term
                if Tid>=tlen-1:   # if no next term
                    Tid = tlen-1        #Reset to final term

            if self.is_number(mterms[Tid]):
                Aid +=1
                Ans.append(global_vars.las_df[Ans[0].name].copy())
                Ans[Aid].name=mterms[Tid]
                Ans[Aid].iloc[:] =float(mterms[Tid])
            if mterms[Tid]=='(':     #Next level of preference
                Aid +=1
                Tid +=1
                Tid_nw=0
                Ans, Aid, Tid = self.get_nexT(Ans,Aid, Tid, mterms, crvnames, tlen, Tid_nw)   #Nesting function

            #ready to Divide
            Ans[Aid-1]=Ans[Aid-1]/Ans[Aid]
            del Ans[-1]
            Aid -=1 #restore order of preference
            Tid +=1             #next terms
            if Tid>=tlen-1:   # if no next term
                Tid = tlen-1        #Reset to final term
                del global_vars.func_id[-1]
                return Ans, Aid, Tid
            Tid_fl=1
            if tlen>Tid+1:   #if not end of terms
                if mterms[Tid+1] == '(':    # next level of precendence
                    Tid +=1
                elif mterms[Tid] == ')':    #next operation
                    return Ans, Aid, Tid    #previous level of precedence
                else:
                    Tid -=1
            if Aid<2:  #if precedence level back to 1
                #No previous operations
                del global_vars.func_id[-1]
                return Ans, Aid, Tid

            #complete previous operation
            Ans, Aid, Tid = self.comp_op(Ans, Aid, Tid, mterms,tlen, Tid_fl)

        if mterms[Tid] == '^':    #special rules of precendence
            #Get base value
            Tid -=1
            if mterms[Tid] in crvnames:
                if Ans[Aid].name != mterms[Tid]:   #If curve not yet created
                    Ans.append(global_vars.las_df[mterms[Tid]].copy())
                    Aid +=1 #Add curve
            if self.is_number(mterms[Tid]):
                if Ans[Aid].name != mterms[Tid]:   #If curve not yet created
                    Ans.append(global_vars.las_df[Ans[0].name].copy())
                    Aid +=1
                    Ans[Aid].name=mterms[Tid]
                    Ans[Aid].iloc[:] =float(mterms[Tid])
            #get exponent
            Tid +=2
            if mterms[Tid] in crvnames:
                Aid +=1 #Add curve
                Ans.append(global_vars.las_df[mterms[Tid]].copy())
                Tid +=1 #Add term
                if Tid>=tlen-1:   # if no next term
                    Tid = tlen-1        #Reset to final term
            if self.is_number(mterms[Tid]):
                Aid +=1
                Ans.append(global_vars.las_df[Ans[0].name].copy())
                Ans[Aid].iloc[:] =float(mterms[Tid])
                Ans[Aid].name=mterms[Tid]
            if mterms[Tid]=='(':     #Next level of preference
                #Aid +=1
                Tid +=1
                Tid_nw=0
                Ans, Aid, Tid = self.get_nexT(Ans,Aid, Tid, mterms, crvnames, tlen, Tid_nw)   #Nesting function/next precedence level
            #ready to raise power
            Ans[Aid-1] = np.power(Ans[Aid-1],Ans[Aid])
            del Ans[-1]
            Aid -=1 #restore order of preference
            Tid +=1                 #Next term
            if tlen>Tid+1:   #if not end of terms
                if mterms[Tid+1] == '(':    # next level of precendence
                    Tid +=1
                elif mterms[Tid] == ')':    #next operation
                    return Ans, Aid, Tid                    #Previous level of precedence
                else:
                    Tid -=1
                Tid_nw=0
                Ans, Aid, Tid = self.get_nexT(Ans,Aid, Tid, mterms, crvnames, tlen, Tid_nw)   #Nesting function
            if Aid<2:  #if precedence level back to 1
                #No previous operations
                del global_vars.func_id[-1]
                return Ans, Aid, Tid
            #complete previous operation
            if Tid>=tlen:               # if at end of mterms
                Tid=Tid-1

            Ans, Aid, Tid = self.comp_op(Ans, Aid, Tid, mterms,tlen, Tid_fl)
        if global_vars.func_id:
            del global_vars.func_id[-1]
        return Ans, Aid, Tid
    #-------------------------------------------------------------------------------------------------------
    def comp_op(self, Ans, Aid, Tid, mterms,tlen,Tid_fl):
        '''
        complete previous operation
        '''

        if mterms[Tid]==')':
            #find operation prior to (
            for Tim in range(Tid,0,-1):
                if mterms[Tim]=='(':
                    break
            Tadj=(Tid-Tim)+1
            if mterms[Tid-Tadj] not in '+-*/^':  # if loop within operation
                Tadj=Tid-Tim-2
                Tid_fl=1
        elif tlen==Tid+1:   #If last term
            return Ans, Aid, Tid    #complete previous precedence
        else:
            Tadj=len(mterms[Tid-2])+2
        if mterms[Tid-Tadj] != '(' or mterms[Tid-Tadj] != '=':        # If + - or * or /
            if mterms[Tid-Tadj]==')':                #closing brackets
                #Tid +=1
                if Tid>=tlen-1:   # if no next term
                    Tid = tlen-1        #Reset to final term
                    del global_vars.func_id[-1]
                    return Ans, Aid, Tid
                Tid_fl=0 #Reset Tid error flag
            if mterms[Tid-Tadj]=='+':
                if tlen<=Tid+1:   #If last term in commandline
                    Tid -=1 #Adjustment for indexes
                else:
                    Ans[Aid-1] +=Ans[Aid]
                    del Ans[-1]
                    Aid -=1
            if mterms[Tid-Tadj]=='-':
                if tlen<=Tid+1:   #If last term in commandline
                    Tid -=1 #Adjustment for indexes
                else:
                    Ans[Aid-1] -=Ans[Aid]
                    del Ans[-1]
                    Aid -=1
            if mterms[Tid-Tadj]=='*':
                if tlen<=Tid+1:   #If last term in commandline
                    Tid -=1 #Adjustment for indexes
                else:
                    Ans[Aid-1] *=Ans[Aid]
                    del Ans[-1]
                    Aid -=1
            if mterms[Tid-Tadj]=='/':
                if tlen<=Tid+1:   #If last term in commandline
                    Tid -=1 #Adjustment for indexes
                else:
                    Ans[Aid-1] /=Ans[Aid]
                    del Ans[-1]
                    Aid -=1
            if mterms[Tid-Tadj]=='^':
                if tlen<=Tid+1:   #If last term in commandline
                    Tid -=1 #Adjustment for indexes
                else:
                    Ans[Aid-1]=np.power(Ans[Aid-1],Ans[Aid])
                    del Ans[-1]
                    Aid -=1
        Tid +=1 #next terms
        if Tid>=tlen-1:   # if no next term
            Tid = tlen-1        #Reset to final term
            #del func_id[-1]
            return Ans, Aid, Tid
        if Tid_fl==0 or len(mterms[Tid-1])>1:   #syntax error
            if not self.is_number(mterms[Tid - 1]):
                Tid_fl=0   #Syntax Errordi
                Tid -=1
        if Tid_fl==0 or len(mterms[Tid])>1:   #syntax error
            global_vars.ui.Root.window.deiconify()
            alert.RaiseException(mterms[Tid] + "   Syntax Error - edit command line")
        #func_id.append('comp')

        #Done
    #-------------------------------------------------------------------------------------------------------
    def is_number(self, s):
        '''
        Check is string is convertable into a float
        '''
        try:
            float(s)
            return True
        except ValueError:
            return False
