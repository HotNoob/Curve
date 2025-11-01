
import tkinter
import tkinter.ttk
from tkinter import SINGLE, Button, Label, Listbox, W
from typing import TYPE_CHECKING

import defs.alert as alert
import defs.common as common
import defs.main as main
import defs.prompt as prompt
import global_vars
import defs.program as program
from classes.MinMaxScale import MinMaxScale
from classes.Object import Object
from classes.Settings import Settings
from enumerables import PlotType

if TYPE_CHECKING:
    from .. import Plot


def newSettingsMenu(self : 'Plot'):
    '''
    plot settings in graphics module
    '''


    #make this a hashtable so we can ignore index bs, to keep the numbers the same
    curve_lists = {}

    curve_lists[1]=[]
    curve_lists[2]=[]
    curve_lists[3]=["","",""]
    curve_lists[4]=["","",""]
    curve_lists[5]=[]
    cmp_list =['<','>']


    curve_lists_defaults = {}
    curve_lists_defaults[1] = 0
    curve_lists_defaults[2] = 1
    curve_lists_defaults[3] = 1
    curve_lists_defaults[4] = -1
    curve_lists_defaults[5] = 0
    curve_lists_defaults[6] = 0

    cdir = {}

    ent_lst = tkinter.StringVar(value='0')


    settings_win = common.initCommonWindow('Plot Settings')

    if self.plotType==PlotType.CrossPlot or self.plotType==PlotType.ZPlot or self.plotType==PlotType.PK or self.plotType==PlotType.ThreeDPlot:
        #set first for cross plot
        #get overlay image
        if self.plotType==PlotType.CrossPlot or self.plotType==PlotType.ZPlot:
            overlayImageFile=prompt.get_image()
            if not overlayImageFile:
                overlayImageFile=''

        if self.plotType==PlotType.PK:
            curve_lists[5]=['VCL_FN','RT','PHI_FN','SW_FN']    #discriminator curve
            cdir[5]=global_vars.project.outDir
            curve_lists[1]=['RT']
            cdir[1]=global_vars.project.outDir
            curve_lists[2]=['PHI_FN']
            cdir[2]=global_vars.project.outDir
            curve_lists[4]=['SW_FN']
            cdir[4]=global_vars.project.outDir
            curve_lists[6]= cmp_list #hacking it in

        else:
            #Select input directory for each curve in plot type
            curve_lists[1]=program.get_crvlist(1)
            curve_lists[1].pop(0)    #remove None
            cdir[1]=global_vars.myDirC
            curve_lists[2]=program.get_crvlist(2)
            curve_lists[2].pop(0)    #remove None
            cdir[2]=global_vars.myDirC
            if self.plotType==PlotType.ZPlot:
                curve_lists[4]=program.get_crvlist('4 or Z-curve')
                cdir[4]=global_vars.myDirC

        if self.plotType==PlotType.ThreeDPlot:
            curve_lists[3]=program.get_crvlist(3)
            curve_lists[3].pop(0)    #remove None
            cdir[3]=global_vars.myDirC
            curve_lists[4]=program.get_crvlist('4 or Z-curve')
            curve_lists[4].pop(0)    #remove None
            cdir[4]=global_vars.myDirC

    if self.plotType==PlotType.Histogram:
        #set for histogram
        # #Select input directory for each curve in plot type
        curve_lists[1]=program.get_crvlist(1)
        curve_lists[1].pop(0)            #remove None
        cdir[1]=global_vars.myDirC

    #SET WIDGETS - DISABLED
    col_list=['#ff8000','#ff8040','#a42d0b','#804040','#008000','#80ff00','#004080','#0000ff','#0080ff','#ff80c0','#800080','#ff0000','#000000']
    pen_width_options = {}
    pen_width_options['narrow'] = 1
    pen_width_options['medium'] = 3
    pen_width_options['normal'] = 5
    pen_width_options['thick'] = 7
    t_opt=['none', 'linear', '2nd', '3rd']
    normzd=['False','True']
    bins = ['1','5','10','15','20','50']
    pen_type=['solid','dashed','dotted','dashdot']
    c_names=tkinter.StringVar(value=col_list)

    # create labels
    T_label=Label(settings_win, text="Select alias or curves")
    T_label2=Label(settings_win, text="X-axis",font=('Helvetica',16))
    T_label3=Label(settings_win, text="Y-axis",font=('Helvetica',16))
    T_label4=Label(settings_win, text="Z-axis",font=('Helvetica',16))
    T_label5=Label(settings_win, text="4rth-axis",font=('Helvetica',18))
    T_label6=Label(settings_win, text="Discriminating Curve",font=('Helvetica',18))


    curves : dict[str, tkinter.ttk.Combobox] = {}

    for key, value in curve_lists.items():
        curve_list_length = len(value)
        if(curve_list_length > 0):
            curves[key] = tkinter.ttk.Combobox(settings_win, value=value, state='disabled')
            if(curve_lists_defaults[key] > 0):
                if(curve_lists_defaults[key] < curve_list_length):
                    curves[key].current(curve_lists_defaults[key])
                else:
                    curves[key].current(0)
            elif (curve_lists_defaults[key] < 0 and curve_list_length + curve_lists_defaults[key] > 0 ):
                curves[key].current(curve_list_length + curve_lists_defaults[key])
            else:
                curves[key].current(0)

    if self.plotType==PlotType.PK:
        #comparitor
        cmp_combobox=tkinter.ttk.Combobox(settings_win, value=cmp_list, state='disabled')
        #entry value
        v_box=tkinter.ttk.Entry(settings_win,textvariable=ent_lst, width=23, state='disabled')

    colorResponses = {}
    colorListBoxes = {}

    def get_col(win, index):
        if win.curselection():
            sel=win.curselection()
        else:
            return
        colorResponses[index]=sel[0]
        win.select=None
        return

    for i in (1,2,3):
        colorListBoxes[i]=Listbox(settings_win, listvariable=c_names, height=13, selectmode=SINGLE, state='disabled')
        colorResponses[i] = Object()
        colorResponses[i].value = None
        colorListBoxes[i].bind('<<ListboxSelect>>', lambda event, i=i: (print(event.widget.curselection()), setattr(colorResponses[i], "value", event.widget.curselection()) if len(event.widget.curselection()) > 0 else None))


    #define buttons

    # assign color to each list item background
    for i in range(0,len(col_list)):
        colorListBoxes[1].itemconfigure(i,background=col_list[i])
        colorListBoxes[2].itemconfigure(i,background=col_list[i])
        colorListBoxes[3].itemconfigure(i,background=col_list[i])

    pen_widths = {}
    # Set pen width
    if self.plotType ==PlotType.Histogram:
        PW_label=Label(settings_win, text="Normalize Histogram")
        pen_widths[1]=tkinter.ttk.Combobox(settings_win,value=normzd,state='disabled')
        pen_widths[1].current(0)
    else:
        PW_label=Label(settings_win, text="Select line Width")
        for i in (1,2,3):
            pen_widths[i]=tkinter.ttk.Combobox(settings_win,value=list(pen_width_options.keys()),state='disabled')
            pen_widths[i].current(0)

    pen_types = {}
    # Set line type or number of bins
    if self.plotType ==PlotType.Histogram:
        PT_label=Label(settings_win, text="Select Number of Bins")
        pen_types[1]=tkinter.ttk.Combobox(settings_win,value=bins,state='disabled')
        pen_types[1].current(0)
    else:
        PT_label=Label(settings_win, text="Select line Width")
        for i in (1,2,3):
            pen_types[i]=tkinter.ttk.Combobox(settings_win,value=pen_type,state='disabled')
            pen_types[i].current(0)

    #  Set trendline
    if self.plotType ==PlotType.CrossPlot or self.plotType==PlotType.ZPlot:
        TL_label=Label(settings_win, text="Select trendline order")
        tl=tkinter.ttk.Combobox(settings_win,value=t_opt, state='disabled')
        tl.current(0)

    # for cross plots select track for each curve
    #if p_type==PlotType.CrossPlot:
        #c_track=IntVar()
        #track_1=Radiobutton(set_win,text='One Track',variable=c_track, value=0)
        #track_2=Radiobutton(set_win,text='Two Tracks',variable=c_track, value=1)

    # done

    cancelResponse = Object()
    cancelResponse.value = False

    b_done=Button(settings_win, bg='cyan', text="Submit", command=settings_win.quit)
    b_cancel=Button(settings_win, bg='pink', text='Cancel', command= lambda: (setattr(cancelResponse, 'value', True), settings_win.quit()))
    #+++++++++++++++++
    #PLACE WIDGETS BASED ON PLOT TYPE and SET STATE TO NORMALdef ca_button(win, idx):
    '''
    cancelled options
    1 = Plot settings/zone selection, 2=default, 3=Final curve/scale selection, 4=Normalize
    5 = answer plot settings  6=multimineral settings 7=ticks cancelled
    Quit dpt_window main loop and deiconify gr_win or nrm_win
    '''


    # Place T_Label
    T_label.grid(row=0,column=1, columnspan=2)
    if self.plotType==PlotType.CrossPlot:        # if cross plot
        T_label2.grid(row=1,column=0)
        T_label3.grid(row=1,column=1)
    elif self.plotType==PlotType.ZPlot or self.plotType==PlotType.PK:       #if Zaxis plot
        T_label2.grid(row=1,column=0)
        T_label3.grid(row=1,column=1)
        T_label5.grid(row=1,column=3)
        if self.plotType==PlotType.PK:
            T_label6.grid(row=4,column=3)
    elif self.plotType==PlotType.Histogram:      #If histogram
        T_label2.grid(row=1,column=0)
    else:   # if 3d
        T_label2.grid(row=1,column=0)
        T_label3.grid(row=1,column=1)
        T_label4.grid(row=1,column=2)
        T_label5.grid(row=1,column=3)

    #Place comboboxes, entry boxes and labels
    if self.plotType==PlotType.CrossPlot:     # if cross plot
        curves[1].grid(row=2, column=0)      # place crv selection box 1
        curves[2].grid(row=2, column=1)      # place crv selection box 2
        colorListBoxes[1].grid(row=3,column=0)       # place color list box 1
        colorListBoxes[2].grid(row=3,column=1)       # place color list box 2
        pen_widths[1].grid(row=5,column=0)        # place penn width box 1
        pen_widths[2].grid(row=5,column=1)        # place penn width box 2
        pen_types[1].grid(row=7,column=0)        #Place pen type combo c1
        pen_types[2].grid(row=7,column=1)        #Place pen type combo c2
        tl.grid(row=5, column=2)         #Place trendline combo tl
        PW_label.grid(row=4,column=0, sticky=W)     # place line width label
        PT_label.grid(row=6,column=0, sticky=W)     # place line type label
        TL_label.grid(row=4,column=2, sticky=W)     # place trendline label

    elif self.plotType==PlotType.ZPlot or self.plotType==PlotType.PK:     # if cross plot
        curves[1].grid(row=2, column=0)      # place crv selection box 1
        curves[2].grid(row=2, column=1)      # place crv selection box 2
        curves[4].grid(row=2, column=3)      # place crv selection box 4
        if self.plotType==PlotType.PK:
            curves[5].grid(row=5, column=3)              # place disc crv selection box 4
            cmp_combobox.grid(row=6, column=3)              # place comparitor"
            v_box.grid(row=7, column=3)             # value entry
        colorListBoxes[1].grid(row=3,column=0)       # place color list box 1
        colorListBoxes[2].grid(row=3,column=1)       # place color list box 2
        pen_widths[1].grid(row=5,column=0)        # place penn width box 1
        pen_widths[2].grid(row=5,column=1)        # place penn width box 2
        pen_types[1].grid(row=7,column=0)        #Place pen type combo c1
        pen_types[2].grid(row=7,column=1)        #Place pen type combo c2
        if self.plotType ==PlotType.ZPlot:
            tl.grid(row=5, column=2)         #Place trendline combo tl
        PW_label.grid(row=4,column=0, sticky=W)     # place line width label
        PT_label.grid(row=6,column=0, sticky=W)     # place line type label
        if self.plotType ==PlotType.ZPlot:
            TL_label.grid(row=4,column=2, sticky=W)     # place trendline lab

    elif self.plotType ==PlotType.Histogram: #If histogram
        curves[1].grid(row=2, column=0)     # place crv selection box 1
        colorListBoxes[1].grid(row=3,column=0)      # place color list box 1
        pen_widths[1].grid(row=5,column=0)       # place penn width box 1 for normalized choice
        pen_types[1].grid(row=7,column=0)        #Place pen type combo c1 fornumber of bins
        PW_label.grid(row=4,column=0, sticky=W)     # place line width label with Normalize choice
        PT_label.grid(row=6,column=0, sticky=W)     # place line type label with number of bins

    else:   # if  3d
        curves[1].grid(row=2, column=0)      # place crv selection box 1
        curves[2].grid(row=2, column=1)      # place crv selection box 2
        curves[3].grid(row=2, column=2)      # place crv selection box 3
        curves[4].grid(row=2, column=3)      # place crv selection box 4
        colorListBoxes[1].grid(row=3,column=0)       # place color list box 1
        colorListBoxes[2].grid(row=3,column=1)       # place color list box 2
        colorListBoxes[3].grid(row=3,column=2)       # place color list box 3
        pen_widths[1].grid(row=5,column=0)        # place penn width box 1
        pen_widths[2].grid(row=5,column=1)        # place penn width box 2
        pen_widths[3].grid(row=5,column=2)        # place penn width box 3
        pen_types[1].grid(row=7,column=0)        #Place pen type combo c1
        pen_types[2].grid(row=7,column=1)        #Place pen type combo c2
        pen_types[3].grid(row=7,column=2)        #Place pen type combo c3
        PW_label.grid(row=4,column=0, sticky=W)     # place line width label
        PT_label.grid(row=6,column=0, sticky=W)     # place line type label

    # for depth plots select track for each curve
    #if p_type==PlotType.CrossPlot:
        #track_1.grid(row=8,column=0)
        #track_2.grid(row=8,column=1)

    b_done.grid(row=8, column=2, pady=10)
    b_cancel.grid(row=8, column=3, pady=10)

    # for xp maximum of 2 curves vs MD (or SS)
    if self.plotType==PlotType.CrossPlot:
        #get curve 1 and 2
        curves[1].config(state='normal' )
        curves[2].config(state='normal' )
        colorListBoxes[1].config(state='normal')
        colorListBoxes[2].config(state='normal')
        pen_widths[1].config(state='normal')
        pen_widths[2].config(state='normal')
        pen_types[1].config(state='normal')
        pen_types[2].config(state='normal')
        tl.config(state='normal')

    elif self.plotType==PlotType.ZPlot or self.plotType==PlotType.PK:
        #get curve 1 and 2
        curves[1].config(state='normal' )
        curves[2].config(state='normal' )
        curves[4].config(state='normal' )
        if self.plotType==PlotType.PK:
            curves[5].config(state='normal' )
            cmp_combobox.config(state='normal' )
            v_box.config(state='normal' )
        colorListBoxes[1].config(state='normal')
        colorListBoxes[2].config(state='normal')
        pen_widths[1].config(state='normal')
        pen_widths[2].config(state='normal')
        pen_types[1].config(state='normal')
        pen_types[2].config(state='normal')
        if self.plotType ==PlotType.ZPlot:
            tl.config(state='normal')

    elif self.plotType==PlotType.Histogram:
        #get curve 1
        curves[1].config(state='normal' )
        colorListBoxes[1].config(state='normal')
        pen_widths[1].config(state='normal')
        pen_types[1].config(state='normal')

    else:   # ptype == 3d
        curves[1].config(state='normal' )
        curves[2].config(state='normal' )
        curves[3].config(state='normal' )
        curves[4].config(state='normal' )
        colorListBoxes[1].config(state='normal')
        colorListBoxes[2].config(state='normal')
        colorListBoxes[3].config(state='normal')
        pen_widths[1].config(state='normal')
        pen_widths[2].config(state='normal')
        pen_widths[3].config(state='normal')
        pen_types[1].config(state='normal')
        pen_types[2].config(state='normal')
        pen_types[3].config(state='normal')

        #show default scales and allow to alter

    #loop and destroy when done
    settings_win.mainloop()


    #set colors
    for i in (1,2,3):
        if colorResponses[i].value:
            colorResponses[i].value = colorResponses[i].value[0]
        else:
            colorResponses[i].value = 0
        print("selected color : " + str(col_list[colorResponses[i].value]))

    self.settings = Settings()
    plt_stgs=[]
    
    if cancelResponse.value==True:              # If plt_settings cancelled
        settings_win.destroy()
        self.settings.LoadFromArray(plt_stgs)
        return False
    crv = ''
    if self.plotType==PlotType.CrossPlot:
        #check for incorrect curve names
        for x in (1,2): #1,2
            crv=curves[x].get()
            if crv not in curve_lists[x]:
                #if curve name in combobox misspelled
                settings_win.destroy()
                alert.Error(f"spelling error in {crv} or not in combobox list")
                self.settings.LoadFromArray(plt_stgs)
                return False

        #get all plot parameters into a simple array before destroying the settings window and save ut as a default or settings file
        c1_scale,c2_scale,c3_scale, z_scale=main.get_scale(curves[1].get(),curves[2].get(),"","")

        plt_stgs=[['plot_type','xp'],
                ['curve1_dir',cdir[1]],
                ['curve1',curves[1].get()],
                ['c1_col',col_list[colorResponses[1].value]],
                ['c1_width',pen_width_options[pen_widths[1].get()]],
                ['c1_type',pen_types[1].get()],
                ['c1_scale',c1_scale],
                ['curve2_dir',cdir[2]],
                ['curve2',curves[2].get()],
                ['c2_col',col_list[colorResponses[2].value]],
                ['c2_width',pen_width_options[pen_widths[2].get()]],
                ['c2_type',pen_types[2].get()],
                ['c2_scale',c2_scale],
                ['tracks',str(2)],
                ['trend',tl.get()],
                ['overlay',overlayImageFile]
                ]
    elif self.plotType==PlotType.ZPlot or self.plotType==PlotType.PK:
        #check for incorrect curve names
        for x in (1,2,3):
            if curves[x].get() not in curve_lists[x]:
                #if curve name in combobox misspelled
                settings_win.destroy()
                alert.Error(f"spelling error in {crv} or not in combobox list")
                self.settings.LoadFromArray(plt_stgs)
                return False


        #get all plot parameters into a simple array before destroying the settings window and save ut as a default or settings file
        if self.plotType==PlotType.PK:
            crv=curves[5].get()
            if crv not in curve_lists[5]:
                #if curve name in combobox misspelled
                settings_win.destroy()
                alert.Error(f"spelling error in {crv} or not in combobox list")
                self.settings.LoadFromArray(plt_stgs)
                return False

            c1_scale= '0.1,1000.00,10'
            c2_scale= '0.01,1.00,10'
            z_scale= ''

            plt_stgs=[['plot_type','pk'],
                ['curve1_dir',global_vars.project.outDir],
                ['curve1',curves[1].get()],
                ['c1_col',col_list[colorResponses[1].value]],
                ['c1_width',pen_width_options[pen_widths[1].get()]],
                ['c1_type',pen_types[1].get()],
                ['c1_scale',c1_scale],
                ['curve2_dir',global_vars.project.outDir],
                ['curve2',curves[2].get()],
                ['c2_col',col_list[colorResponses[2].value]],
                ['c2_width',pen_width_options[pen_widths[2].get()]],
                ['c2_type',pen_types[2].get()],
                ['c2_scale',c2_scale],
                ['zcurve_dir',global_vars.project.outDir],
                ['zcurve',curves[4].get()],
                ['z_scale',z_scale],
                ['cp_crv_dir',global_vars.project.outDir],
                ['cp_crv',curves[5].get()],
                ['cp_col',''],
                ['cp_type',''],
                ['comparitor',cmp_combobox.get()],
                ['comp_val',v_box.get()],
                ['tracks',str(2)],
                ]

        else:
            c1_scale,c2_scale,c3_scale,z_scale=main.get_scale(curves[1].get(),curves[2].get(),"",curves[4].get())

            plt_stgs=[['plot_type','zp'],
                    ['curve1_dir',cdir[1]],
                    ['curve1',curves[1].get()],
                    ['c1_col',col_list[colorResponses[1].value]],
                    ['c1_width',pen_width_options[pen_widths[1].get()]],
                    ['c1_type',pen_types[1].get()],
                    ['c1_scale',c1_scale],
                    ['curve2_dir',cdir[2]],
                    ['curve2',curves[2].get()],
                    ['c2_col',col_list[colorResponses[2].value]],
                    ['c2_width',pen_width_options[pen_widths[2].get()]],
                    ['c2_type',pen_types[2].get()],
                    ['c2_scale',c2_scale],
                    ['zcurve_dir',cdir[4]],
                    ['zcurve',curves[4].get()],
                    ['z_scale',z_scale],
                    ['tracks',str(2)],
                    ['trend',tl.get()],
                    ['overlay',overlayImageFile]
                    ]
    elif self.plotType==PlotType.ThreeDPlot:
        #check for incorrect curve names
        for x in (1,2,3,4):
            crv=curves[x].get()
            if crv not in curve_lists[x]:
                #if curve name in combobox misspelled
                settings_win.destroy()
                alert.Error(f"spelling error in {crv} or not in combobox list")
                self.settings.LoadFromArray(plt_stgs)
                return False

        #get all plot parameters into a simple array before destroying the settings window and save ut as a default or settings file
        c1_scale,c2_scale,c3_scale,z_scale=main.get_scale(curves[1].get(),curves[2].get(),curves[3].get(),curves[4].get())
        #z_scale=get_z_scale(crv4,get())
        plt_stgs=[['plot_type','3d'],
                ['curve1_dir',cdir[1]],
                ['curve1',curves[1].get()],
                ['c1_col',col_list[colorResponses[1].value]],
                ['c1_width',pen_width_options[pen_widths[1].get()]],
                ['c1_type',pen_types[1].get()],
                ['c1_scale',c1_scale],
                ['curve2_dir',cdir[2]],
                ['curve2',curves[2].get()],
                ['c2_col',col_list[colorResponses[2].value]],
                ['c2_width',pen_width_options[pen_widths[2].get()]],
                ['c2_type',pen_types[2].get()],
                ['c2_scale',c2_scale],
                ['curve3_dir',cdir[3]],
                ['curve3',curves[3].get()],
                ['c3_col',col_list[colorResponses[3].value]],
                ['c3_width',pen_width_options[pen_widths[3].get()]],
                ['c3_type',pen_types[3].get()],
                ['c3_scale',c3_scale],
                ['curve4_dir',cdir[4]],
                ['zcurve',curves[4].get()],
                ['z_scale',z_scale],
                ['tracks',str(2)]
                ]
    elif self.plotType==PlotType.Histogram:
        #check for incorrect curve names
        crv=curves[1].get()
        if crv not in curve_lists[1]:
            #if curve name in combobox misspelled
            settings_win.destroy()
            alert.Error(f"spelling error in {crv} or not in combobox list")
            self.settings.LoadFromArray(plt_stgs)
            return False

        #get all plot parameters into a simple array before destroying the settings window and save ut as a default or settings file
        c1_scale,c2_scale,c3_scale,z_scale=main.get_scale(curves[1].get(),"","","")
        c1_scale = MinMaxScale.FromString(c1_scale)

        plt_stgs=[['plot_type','hg'],
                ['curve1_dir',cdir[1]],
                ['curve1',curves[1].get()],
                ['c1_col',col_list[colorResponses[1].value]],
                ['c1_Edge',"#000000"],
                ['c1_Norm',pen_widths[1].get()],
                ['c1_Bins',pen_types[1].get()],
                ['c1_scale',c1_scale.ToString()],           # don't forget histogram bins
                ['c1_min',c1_scale.min],
                ['c1_max',c1_scale.max],
                ['c1_base',c1_scale.base]
                ]
        

    if self.zoneDepths is not None:
        plt_stgs.append(['Zone',self.zoneDepths.name])

    self.settings.LoadFromArray(plt_stgs)

    if self.plotType!= PlotType.PK:
        # get scales ## where is this defined?
        self.plotScales() #default settings are saved in here. 
        settings_win.destroy() 
        return True
    
    #save default plot file ext . plot type xp, hg, zp, pk or 3d
    self.SaveDefaultSettings()
    #set_win destroy
    settings_win.destroy()
    return True
