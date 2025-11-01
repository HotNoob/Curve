'''Ans_Sett'''
import glob
import os
import tkinter.ttk as ttk
from tkinter import EW, Button, E, Label, Toplevel, W
from typing import TYPE_CHECKING

import lasio
import matplotlib.pyplot as pyplot
from classes.Plot.DepthPlot.DepthPlotSettings import DepthPlotProperties

from defs import program
import defs.alert as alert
import defs.common as common
import defs.excel as excel
import defs.las as las
import defs.main as main
import defs.prompt as prompt
from enumerables import Dir
import global_vars
from classes.Object import Object
from structs import ZoneDepths

from . import _enumerables

if TYPE_CHECKING:
    from .. import DepthPlot


def newSettingsMenu(self : 'DepthPlot') -> bool:
    '''
    Customize answer plot settings
    '''

    self.graphingWindow.iconify()

    #get current well
    global_vars.currentWell=global_vars.project.currentWellList.GetWell(0)

    #set working directories
    old_dir=os.getcwd()

    #load settings from database directory
    myesno=prompt.yesno("Load a depth plot file?")
    lines=[]
    if myesno==True:
        lines=self.loadSettings(_enumerables.DepthPlotType.DepthPlot)
        if lines==None:
            return

    '''
    character description'
    '-'       solid line style
    '--'      dashed line style
    '-.'      dash-dot line style
    ':'       dotted line style
    '.'       point marker
    ','       pixel marker
    'o'       circle marker
    'v'       triangle_down marker
    '^'       triangle_up marker
    '<'       triangle_left marker
    '>'       triangle_right marker
    '1'       tri_down marker
    '2'       tri_up marker
    '3'       tri_left marker
    '4'       tri_right marker
    's'       square marker
    'p'       pentagon marker
    '*'       star marker
    'h'       hexagon1 marker
    'H'       hexagon2 marker
    '+'       plus marker
    'x'       x marker
    'D'       diamond marker
    'd'       thin_diamond marker
    '|'       vline marker
    '_'       hline marker
    '''

    # get parameters from Depth Plot Settings
    global_vars.color_list=['green', 'palegreen','red','lightcoral','olive','blue','cyan' ,'magenta','purple','gold','lightgrey', 'black', 'darkblue', 'lightblue', 'gray','yellow','orange']
    global_vars.line_list=['dotted','solid','dashed','dashdot',(0,(3,1,1,1)),(0,(4, 2, 1, 2)),(0,(3,1,1,1,1,1))]
    global_vars.line_style=['dotted','solid','dashed','dashdot', 'loosely dotted','longdash dotted','densely dashdotdotted']
    #marker_list=['o','O','s','d','D','x','X','h','+','*','^','']
    global_vars.marker_style=['None','circle','thin diamond','diamond','thin X','big X','hex 1', 'hex 2', 'plus','triangle','star']
    global_vars.tick_list=[[0, 50, 100, 150, 200],[0.45, 0.3, 0.15, 0, -0.15],[0.60, 0.45, 0.30, 0.15, 0],[1.95, 2.2, 2.45, 2.7, 2.95],[500,400,300,200,100],[0.1,1,10,100,1000],[0.2,2,20,200,2000],[1.65, 1.90, 2.15, 2.4, 2.65],[0, 0.25, 0.5, 0.75, 1],[-2,0,2,4,6]]
    global_vars.mtick_list=['0 50 100 150 200','0.45 0.3 0.15 0 -0.15','0.60 0.45 0.30 0.15 0','1.95 2.2 2.45 2.7 2.95','500 400 300 200 100','0.1 1 10 100 1000','0.2 2 20 200 2000','1.65 1.90 2.15 2.4 2.65','0 0.25 0.5 0.75 1','-2 0 2 4 6','CUSTOM']
    global_vars.scale_list=['linear','logarithmic']

    curvs=[]
    props=[]
    track=[]
    fcrvs=[]    #Fill curves
    l_col=[]
    l_styl=[]
    l_tick=[]
    l_scale=[]
    l_mark=[]
    l_fill=[]

    # initial settings lists
    for x in range(25):
        #create curve list
        curvs.append(None)
        #create proporties lists
        props.append(None)
        track.append(None)
        l_col.append(None)
        l_styl.append(None)
        l_tick.append(None)
        l_scale.append(None)
        l_mark.append(None)
        l_fill.append(None)

    # create curve lists
    core_flag = 0
    inDirCurves : set = self.wellList.GetCommonCurves(Dir.In) - {'DEPT'}
    coreCurves : set = set()
    if global_vars.currentWell.GetWellFile(Dir.In, '.cas') is not None:
        core_flag = 1
        coreCurves = set(global_vars.cdescrvs) - {'DEPT', 'S_TP','S_TCK', 'COREDEPT','SAMPLE','ACCESSORIES','SEDSTRUCT'} - inDirCurves

    outDirCurves : set = self.wellList.GetCommonCurves(Dir.Out) - {'DEPT'} - inDirCurves

    crv_list = list(inDirCurves) + ['CORE DATA'] + list(coreCurves) + ['OUTDIR CURVES'] + list(outDirCurves)
    crv_end=0                       #for plt-plot

    #Create Top level window
    ans_win = common.initCommonWindow(f'Settings for {global_vars.currentWell.uwi}({global_vars.currentWell.alias})', 0.75, 0.9)

    #window expansion
    ans_win.rowconfigure(0,weight=1)
    ans_win.columnconfigure([0,1,2,3],weight=1, uniform=1)

    #select no of tracks
    cmb_list=[1,2,3,4,5,6,7]
    tr_lbl = Label(ans_win, text='Select number of tracks (between 2 and 7): ')
    tr_box=ttk.Combobox(ans_win,value=cmb_list[1:])
    if lines!=[]:           # if plot settings loaded
        mych=int(lines[0][:-1])-2    # remove new line
        tr_box.current(mych)
    tr_lbl.grid(row=0, column=0)
    tr_box.grid(row=1, column=0)

    #Select Zone
    zn_list=list(global_vars.project.formationZones.keys())
    if core_flag==1:
        zn_list.append('CORE')
    zn_lbl = Label(ans_win, text='Select Zone:')
    zn_box=ttk.Combobox(ans_win,value=zn_list)
    if lines!=[]:               # if plot settings loaded
        myzone=lines[1][:-1]
        cnt=0
        for x in zn_list:        #If zone OTHER THAN Core selected
            if x==myzone:
                zn_box.current(cnt)
                break
            cnt +=1
    zn_lbl.grid(row=0, column=1, sticky=W)
    zn_box.grid(row=1, column=1, sticky=W)

    ans_frame=ttk.LabelFrame(ans_win,text='Enter Curves (max=25) and properties')
    ans_frame.grid(row=2, column=0, pady=10, columnspan=4)
    ans_ttl=Label(ans_frame, text='Curve                                     track                                    color                                        style                             scale (log or lin)                       tick option                            marker style                              fill'  )
    ans_ttl.grid(row=0, column=0, columnspan=8, sticky=EW)

    ans_frame.columnconfigure([0,1,2,3,4,5,6,7], weight=1, uniform=True)
    if lines!=[]:           #With load Dpt-settings first 3 lines already read
        lnix=2
        cix=0
        for x in lines:
            if x[:-1]=='END_CRVS':
                crv_end=cix
                pr_jmp = crv_end-1
            cix +=1
    else:
        lnix=0             # create lnix
        col=0
        pr_jmp=0
    for c_row in range(25):
        #create input widget row     if   curvs[c_row].curselect() next row?
        #create a crv_list  - postponed.  You can always copy a curve from one to another directory
        #get_crvlist(many or 1)
        curvs[c_row]=ttk.Combobox(ans_frame,value=crv_list)
        if lnix>=2 and lnix<crv_end:                 # read curves in settings file
            mcrv=lines[lnix][:-1]
            cnt=0
            for x in crv_list:          #If zone OTHER THAN Core selected
                if x==mcrv:
                    curvs[c_row].current(cnt)
                    break
                cnt +=1
        curvs[c_row].grid(row=c_row+3, column=0, pady=3)

        # set mprops read settings file if exists
        if lnix>=2 and lnix<crv_end:        # if settings file
            mprops=lines[lnix+pr_jmp][:-1].split(',')

        else:
            mprops=["","","","","","","","","","","",""]     #list lenght=12

        track[c_row]=ttk.Combobox(ans_frame,value=cmb_list)
        if lines != [] and lnix<crv_end:      #if settings file
            track[c_row].current(int(mprops[5])-1)
        track[c_row].grid(row=c_row+3, column=1, pady=3)

        l_col[c_row]=ttk.Combobox(ans_frame,value=global_vars.color_list)
        if lnix>=2 and lnix<crv_end:
            if mprops[0]=='':         # if default
                l_col[c_row].current(col)
                col +=1
                if col>(len(global_vars.color_list)-1):
                    col=0
            else:
                cnt=0
                for x in global_vars.color_list:
                    if x == mprops[0]:
                        l_col[c_row].current(cnt)
                        break
                    cnt +=1
        l_col[c_row].grid(row=c_row+3, column=2, pady=3)

        l_styl[c_row]=ttk.Combobox(ans_frame,value=global_vars.line_style)
        if lnix>=2 and lnix<crv_end:
            if mprops[1]=='':         # if default
                l_styl[c_row].current(1)
            else:
                cnt=0
                for x in global_vars.line_style:
                    if x == mprops[1]:
                        l_styl[c_row].current(cnt)
                    cnt +=1
        l_styl[c_row].grid(row=c_row+3, column=3, pady=3)

        l_scale[c_row]=ttk.Combobox(ans_frame,value=global_vars.scale_list)
        if lnix>=2 and lnix<crv_end:
            if (mprops[3]=='') or (mprops[3]== 'linear'):         # if default
                l_scale[c_row].current(0)
            else:
                l_scale[c_row].current(1)
        l_scale[c_row].grid(row=c_row+3, column=4, pady=3)

        #update tick_list and mtick_list for custom additions
        if mprops[2] != '' and mprops[2] not in global_vars.mtick_list :
            global_vars.mtick_list.insert(-1,mprops[2])
            mlist= mprops[2].split(' ')
            del mlist[-1]
            #convert to float
            for midx in range(0,5):
                mlist[midx]=float(mlist[midx])
            global_vars.tick_list.append(mlist)

        l_tick[c_row]=ttk.Combobox(ans_frame,value=global_vars.mtick_list)
        if lnix>=2 and lnix<crv_end:
            if mprops[2]=='':         # if default
                l_tick[c_row].current(0)
            else:
                cnt=0
                for x in global_vars.mtick_list:
                    if x == mprops[2]:
                        l_tick[c_row].current(cnt)
                    cnt +=1
        l_tick[c_row].grid(row=c_row+3, column=5, pady=3)

        l_mark[c_row]=ttk.Combobox(ans_frame,value=global_vars.marker_style)
        if lnix>=2 and lnix<crv_end:
            if mprops[4]=='':         # if default
                l_mark[c_row].current(0)
            else:
                cnt=0
                for x in global_vars.marker_style:
                    if x == mprops[4]:
                        l_mark[c_row].current(cnt)
                    cnt +=1
        l_mark[c_row].grid(row=c_row+3, column=6, pady=3)

        l_fill[c_row]=ttk.Combobox(ans_frame,value=['Yes', 'No'])
        if lnix>=2 and lnix<crv_end:
            if mprops[6]=='':         # if default
                l_fill[c_row].current(1)
            else:
                cnt=0
                for x in ['Yes','No']:
                    if x == mprops[6]:
                        l_fill[c_row].current(cnt)
                    cnt +=1
        l_fill[c_row].grid(row=c_row+3, column=7, pady=3)

        if lnix<crv_end:
            lnix +=1    #next line of curve properties

    buttonResponses : Object = Object()
    buttonResponses.done = False
    buttonResponses.cancel = False

    # done
    b_done=Button(ans_frame, bg='cyan', text="Submit", command= lambda: (setattr(buttonResponses, 'done', True), ans_win.quit()))
    b_cancel=Button(ans_frame, bg='pink', text='Cancel', command= lambda: (setattr(buttonResponses, 'cancel', True), ans_win.quit()))
    b_done.grid(row=28,column=6, pady=5,sticky=E)
    b_cancel.grid(row=28,column=7,padx=5, pady=5, sticky=E)

    ans_win.mainloop()


    if buttonResponses.cancel: #cancel
        ans_win.destroy()
        ans_win.deiconify()
        global_vars.currentWell = global_vars.project.currentWellList.GetWell(0)
        return False


    #--------------------------------------------------------------------------------------------------
    #region handleInput
    #    ans_subm(Cur_dir, old_dir, ans_win, win ,lines, pr_jmp, crv_end, tr_box,zn_box, crv_list, curvs,track,l_col,l_styl,l_scale,l_tick,l_mark,l_fill)
    #def ans_subm(Cur_dir, old_dir, ans_win, win, lines, pr_jmp, crv_end ,tr_box,zn_box, crv_list, curvs,track,l_col,l_styl,l_scale,l_tick,l_mark,l_fill):
    '''
    Input settings into dpt plot file
    lines = dpt plot properties
    pr_jmp = idx plus offset to properties in lines

    props[color, linestyle, ticks, scale , marker, track]

    '''

    old_list=crv_list.copy() #back_up

    ynfill=prompt.yesno('change fill Yes or No')

    #plt_set=[]
    crvs=[]             #Curve list for Dpt_plt Settings
    fcrvs=[]             #curvs for fills
    mycrvs=[]           #list of crv dfs to be plotted
    mprops=[]          #curve properties for Dpt_plt
    prps=[]             #Curve property list
    # get wells with core (i.e. have cas files in Indir)

    zone=zn_box.get()
    if zone=='':                #Zone not selected
        ans_win.iconify()
        ans_win.deiconify()
        return alert.Error("Select first a zone")

    #Get input screen data
    no_trcks= int(tr_box.get())
    if no_trcks<2:              #minimum = 2 tracks
        no_trcks=2

    c_idx=0         #Set Curve index
    for c_row in range(25):
        if (curvs[c_row].get()!=None) and (curvs[c_row].get()!='') :               #Curve row is used
            c_idx +=1
            m_crv=curvs[c_row].get()
            #sort by trak
            for trk in range(1,no_trcks+1):
                if trk==int(track[c_row].get()):        # if in same track
                    crvs.append(curvs[c_row].get())
                    prps.append([l_col[c_row].get(),l_styl[c_row].get(),l_tick[c_row].get(),l_scale[c_row].get(),l_mark[c_row].get(), track[c_row].get(),l_fill[c_row].get(),"","","","",""])
            #get_fills(lines,pr_jmp, mprops, m_crv, c_idx, trk_list, color_list)
    crv_no=c_idx

    msave=prompt.yesno('Save settings? Y/N')

    for well in global_vars.ui.Graphing.wellList.GetWells():
        zoneDepths : ZoneDepths = None
        mycrvs=[]
        properties : DepthPlotProperties = []
        mprops=[]
        fcrvs=[]
        #Create a list of FMs and tops to be displayed in DptPlt
        fm_list=[]

        if zoneDepths is None:
            zoneDepths = well.GetZoneDepths(zone)

            if zoneDepths is None:     # if top or base depth not found
                alert.Error(f'Zone {zone} not in {well.uwi}({well.alias}) - remove from well list')
                return
        
        #load plot data from LAS and/or core
        c_idx=0
        for m_crv in crvs:
            '''
            #set curves that need markers
            marklist=['KMAX','KVRT','K90',
            'CPOR','GDEN','BDEN','RSO','RSW']
            '''
            #First check if crvs are in cdescrvs
            if m_crv in global_vars.cdescrvs:  #load cas and set DPT interval
                #ensure well is also in Well List
                coreFile = well.GetCoreFile()
                if coreFile is not None:
                    #get cas_data and create core_df
                    cas_data = coreFile.GetLASData()
                    core_df = cas_data.df()
                    #get cas_data and create core_df
                    cr_shft=cas_data.params.csh.value
                    # shift core in df
                    cshift=round(round(cr_shft/0.1,0)*0.1,1)
                    core_df.index=core_df.index+cshift
                    dir = Dir.In
            else:
                #if curve in Indir or OutDir
                al_list=[]
                found=0   #set foundflag
                opt1=0 #In Alias or outDir
                dir = Dir.In
                al_list = global_vars.project.curveNameTranslator.GetNames()
                crv_list=old_list.copy()     #only for Indir
                for crv in crv_list:
                    if crv=='OUTDIR CURVES':
                        #found Outdir curves
                        found=1
                    if  found==1 and m_crv==crv:
                        dir = Dir.Out
                        opt1=2 #In Outdir for find AKA
                        #crv_list=old_list.copy()

                if dir == Dir.In:  #If Indir
                    crv_list=al_list.copy()     #only for Indir

                las_data = well.GetLASData(dir)
                ls_strt=las_data.well.strt.value
                ls_stop=las_data.well.stop.value
                wellname=las_data.well.well.value

            if zone != 'CORE':         #if not core then set LAS depth interval
                #set depth interval]
                if zone=='WELL':
                    zoneDepths = ZoneDepths(top=ls_strt, base=ls_stop, name=zone)


            found_fl=0                 #clear found flag
            if m_crv not in global_vars.cdescrvs:   # if m_crv not core data
                c1,found_fl= main.find_aka(m_crv, crv_list, 1, las_data, opt1, zoneDepths)
            else:
                #get core data curve
                c1=core_df[m_crv]
                if c1.empty==False:                  # if curve not found
                    found_fl=1

            if found_fl!=1:                        #if crv NOT found
                message= f'{m_crv} not in {well.uwi}({well.alias})'
                alert.Error(message)
                break

            mycrvs.append(c1)           #list of crv dfs to be plotted
            mprops.append(['','','','','','','','','','','',''])         #12 curve properties for Dpt_plt

            #Fill in properties
            #[l_col[c_row].get(),l_styl[c_row].get(),l_tick[c_row].get(),l_scale[c_row].get(),l_mark[c_row].get(), track[c_row].get(), l_fill[c_row].get()]
            idx=0
            if prps[c_idx][0]=='':
                mprops[c_idx][0]=0
                prps[c_idx][0]=global_vars.color_list[0]

            for col in global_vars.color_list:
                if col==prps[c_idx][0]:     #if col found in color list
                    mprops[c_idx][0]=idx
                    break
                idx +=1

            idx=0
            if prps[c_idx][1]=='':
                mprops[c_idx][1]=1             #default style
                prps[c_idx][1]=global_vars.line_style[1]
            else:
                for style in global_vars.line_style:
                    if style==prps[c_idx][1]:     #if style found in line style list
                        mprops[c_idx][1]=idx
                        break
                    idx +=1
            idx=0
            if prps[c_idx][2]=='':
                mprops[c_idx][2]=idx
                prps[c_idx][2]=global_vars.mtick_list[idx]
            elif prps[c_idx][2] =='CUSTOM':
                #Get custom scales
                self.getTicks(prps[c_idx][3])
                if global_vars.gticks!=[]:
                    #check for similar scale in current tick_list
                    fndfl=False
                    idx=0
                    for old_tick in global_vars.tick_list:
                        if float(old_tick[0])==float(global_vars.gticks[0][0]):
                            if float(old_tick[4])==float(global_vars.gticks[0][4]):
                                #found
                                fndfl=True
                                break
                        idx +=1
                    if fndfl==False:   #If not already in tick list
                        p_string=''
                        for mtick in global_vars.gticks[-1]:
                            p_string= p_string + mtick + ' '
                        idx = len(global_vars.tick_list)-1+len(global_vars.gticks)
                        prps[c_idx][2]=p_string
                        mprops[c_idx][2]=idx
                        #update tick_list and mtick_list for custom additions
                        global_vars.mtick_list.insert(-1,prps[c_idx][2])
                        mlist= prps[c_idx][2].split(' ')
                        del mlist[-1]
                        #convert to float
                        for midx in range(0,5):
                            mlist[midx]=float(mlist[midx])
                        global_vars.tick_list.append(mlist)
                        fndfl=True      # reset flag
                    else:
                        prps[c_idx][2]=global_vars.mtick_list[idx]
                        mprops[c_idx][2]=idx
            else:
                for tick in global_vars.mtick_list:
                    if tick==prps[c_idx][2]:     #if tick found in mtick list
                        mprops[c_idx][2]=idx
                        break
                    idx +=1
            idx=0
            if prps[c_idx][3]=='':
                mprops[c_idx][3]=0
                prps[c_idx][3]=global_vars.scale_list[0]
            else:
                for mscale in global_vars.scale_list:
                    if mscale==prps[c_idx][3]:     #if scale found in scale list
                        mprops[c_idx][3]=idx
                        break
                    idx +=1
            idx=0
            if (prps[c_idx][4]=='None') or (prps[c_idx][4]==''):
                mprops[c_idx][4]=11
                prps[c_idx][4]='None'
            else:
                for mymark in global_vars.marker_style:
                    if mymark==prps[c_idx][4]:     #if mark found in market list
                        mprops[c_idx][4]=idx-1
                        break
                    idx +=1

            if prps[c_idx][5]=='':
                message= f'{m_crv} not assigned a track'
                alert.Error(message)
                return
            else:
                mprops[c_idx][5]=int(prps[c_idx][5])

            if prps[c_idx][6]=='Yes' :
                mprops[c_idx][6]=0          #fill
            elif prps[c_idx][6]=='No' or prps[c_idx][6]=='':
                mprops[c_idx][6]=1          # No fill

            global_vars.gticks=[]               #reset
            c_idx +=1               #next curve to be plotted

        ans_win.destroy()             #close settings window
        #Fill settings
        t_idx=0             #curve line counter
        for crv in crvs:
            if mprops[t_idx][6]==0:              #get fill settings
                trk=mprops[t_idx][5]   #first track
                #find curves in same track
                trk_list=[]    #reset track curve list
                trk_list.append('Constant = ')      #if constant selected
                q_idx=0
                for crv1 in crvs:
                    if q_idx!=t_idx:
                        if trk==mprops[q_idx][5]:
                            trk_list.append(crv1)
                            break
                    q_idx +=1
                #get fill settings
                os.chdir(old_dir)

                if mprops[t_idx][6]==0:
                    if ynfill==True:
                        props = self.getFills(lines, pr_jmp, mprops, crv, t_idx, trk_list, global_vars.color_list)
                        if(props is not []): #was not cancelled, so apply new props
                            mprops = props
                            prps[t_idx][7]=str(mprops[t_idx][7])    #fill curve name
                            prps[t_idx][8]=str(mprops[t_idx][8])    #constant
                            prps[t_idx][9]=str(mprops[t_idx][9])    #greater or less than fill curve
                            prps[t_idx][10]=str(mprops[t_idx][10])  #fill color
                            prps[t_idx][11]=str(mprops[t_idx][11])  #fill alpha or transparency
                        else:
                            #do not change fills
                            #loop through lines and find curve
                            lno=0
                            for myprop in lines:
                                if myprop[:-1]==crv:   #remove end of line and find curve
                                    mline=lines[lno+pr_jmp].split(',')
                                    prps[t_idx][6]=mline[6]
                                    prps[t_idx][7]=mline[7]
                                    prps[t_idx][8]=mline[8]
                                    prps[t_idx][9]=mline[9]
                                    prps[t_idx][10]=mline[10]
                                    prps[t_idx][11]=mline[11]
                                    break
                                lno +=1
                            mprops[t_idx][7]=prps[t_idx][7]
                            if prps[t_idx][8]=='None' or prps[t_idx][8]=='':         # Constant
                                mprops[t_idx][8]=None
                            else:
                                mprops[t_idx][8]=float(prps[t_idx][8])
                            mprops[t_idx][9]=int(prps[t_idx][9])
                            mprops[t_idx][10]=prps[t_idx][10]
                            mprops[t_idx][11]=float(prps[t_idx][11])

                            if mprops[t_idx][7]!='None': # if not a constant then curve
                                for fc in mycrvs:               #check list of crv dataframes
                                    if fc.name==prps[t_idx][7]:
                                        fcrvs.append(fc)
                                        break

                    else:    #do not change fills
                        #loop through lines and find curve
                        lno=0
                        for myprop in lines:
                            if myprop[:-1]==crv:   #remove end of line and find curve
                                mline=lines[lno+pr_jmp].split(',')
                                prps[t_idx][6]=mline[6]
                                prps[t_idx][7]=mline[7]
                                prps[t_idx][8]=mline[8]
                                prps[t_idx][9]=mline[9]
                                prps[t_idx][10]=mline[10]
                                prps[t_idx][11]=mline[11]
                                break
                            lno +=1
                        mprops[t_idx][7]=prps[t_idx][7]
                        if prps[t_idx][8]=='None' or prps[t_idx][8]=='':         # Constant
                            mprops[t_idx][8]=None
                        else:
                            mprops[t_idx][8]=float(prps[t_idx][8])
                        mprops[t_idx][9]=int(prps[t_idx][9])
                        mprops[t_idx][10]=prps[t_idx][10]
                        mprops[t_idx][11]=float(prps[t_idx][11])

                        if mprops[t_idx][7]!='None': # if not a constant then curve
                            for fc in mycrvs:               #check list of crv dataframes
                                if fc.name==prps[t_idx][7]:
                                    fcrvs.append(fc)
                                    break
            t_idx +=1
        #Plot Current Well_List
        # create depth plots Plot type = 0    Dpt_plt(wellname, curvs, fcrvs, props, trcks, pltype=0, Fms)
        self.depthPlot(f'{wellname} - {well.uwi}({well.alias}) - Curve {global_vars.SoftwareVersion}', mycrvs, fcrvs, mprops, no_trcks, _enumerables.DepthPlotType.MutlipleDepthPlot, well.formations, zoneDepths)
        #DepthPlot.newDepthPlot(wellname, mycrvs, fcrvs, mprops, no_trcks, 2, fm_list)
        #Dpt_plt(wellname, mycrvs, fcrvs, mprops, no_trcks, 2, fm_list)

    pyplot.show(block=True)

    if msave==True:
        self.saveSettings(old_dir,crv_no, no_trcks, zone, crvs,prps)
        msave==False
    os.chdir(old_dir)               #Back to working dir
    self.graphingWindow.deiconify()

    #endregion handleInput



    tr_box.focus_set()
    return True
