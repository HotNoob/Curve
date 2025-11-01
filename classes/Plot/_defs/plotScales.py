
import tkinter.ttk as ttk
from tkinter import Button, Label, StringVar, W
from typing import TYPE_CHECKING

import defs.common as common
import defs.main as main
from classes.MinMaxScale import MinMaxScale
from classes.Object import Object
from enumerables import PlotType

if TYPE_CHECKING:
    from .. import Plot

def plotScales(self : 'Plot'):
    '''
    Set custom scales for curves in plot
    '''

    sc_win = common.initCommonWindow('Set Scales', 650, 200)

    my_Name=''

    #Set Widgets
        # CUstom or default scale?
    SC_label=Label(sc_win, text="Accept Defautl Scale or Change.      Base=0 is linear; base=10 is logarithmic")
    CV_label=Label(sc_win, text= my_Name)
    S_l_label=Label(sc_win, text= "Left or Bottom")
    S_r_label=Label(sc_win, text= "Right or Top")
    S_b_label=Label(sc_win, text= "Base")
    if self.plotType==PlotType.Histogram:
        # get default scales PlotType.Histogram'
        crv1=self.settings.Get('curve1')
        my_Name=50*' '+ crv1
        CV_label.config(text=my_Name)
        S_l_label.config(text= "Min")
        S_r_label.config(text= "Max")
        S_b_label.config(text= "Base")
        c1_scale,c2_scale,c3_scale,z_scale=main.get_scale(crv1,"","","")
        c1_scale=MinMaxScale.FromString(c1_scale)
        var1=StringVar()
        var2=StringVar()
        var3=StringVar()
        var1.set(c1_scale.min)
        s1_min=ttk.Entry(sc_win,textvariable=var1,state='disabled')
        var2.set(c1_scale.max)
        s1_max=ttk.Entry(sc_win,textvariable=var2,state='disabled')
        var3.set(c1_scale.base)
        s1_base=ttk.Entry(sc_win,textvariable=var3,state='disabled')

    if self.plotType==PlotType.CrossPlot:
        crv1=self.settings.Get('curve1')
        crv2=self.settings.Get('curve2')
        my_Name=50*' '+ crv1 +40*' '+crv2
        CV_label.config(text=my_Name)
        # get default scales PlotType.CrossPlot
        c1_scale,c2_scale,c3_scale, z_scale=main.get_scale(crv1,crv2,"","")
        c1_scale=MinMaxScale.FromString(c1_scale)
        c2_scale=MinMaxScale.FromString(c2_scale)
        var1=StringVar()
        var2=StringVar()
        var3=StringVar()
        var4=StringVar()
        var5=StringVar()
        var6=StringVar()
        var1.set(c1_scale.min)
        s1_min=ttk.Entry(sc_win,textvariable=var1,state='disabled')
        var2.set(c1_scale.max)
        s1_max=ttk.Entry(sc_win,textvariable=var2,state='disabled')
        var3.set(c1_scale.base)
        s1_base=ttk.Entry(sc_win,textvariable=var3,state='disabled')
        var4.set(c2_scale.min)
        s2_min=ttk.Entry(sc_win,textvariable=var4,state='disabled')
        var5.set(c2_scale.max)
        s2_max=ttk.Entry(sc_win,textvariable=var5,state='disabled')
        var6.set(c2_scale.base)
        s2_base=ttk.Entry(sc_win,textvariable=var6,state='disabled')

    if self.plotType==PlotType.ZPlot:
        # get default scales PlotType.ZPlot
        crv1=self.settings.Get('curve1')
        crv2=self.settings.Get('curve2')
        crv4=self.settings.Get('zcurve')
        my_Name=50*' '+ crv1 +40*' '+crv2
        CV_label.config(text=my_Name)
        c1_scale,c2_scale,c3_scale,z_scale=main.get_scale(crv1,crv2,"",crv4)
        c1_scale=MinMaxScale.FromString(c1_scale)
        c2_scale=MinMaxScale.FromString(c2_scale)
        z_scale=MinMaxScale.FromString(z_scale)
        var1=StringVar()
        var2=StringVar()
        var3=StringVar()
        var4=StringVar()
        var5=StringVar()
        var6=StringVar()
        var1.set(c1_scale.min)
        s1_min=ttk.Entry(sc_win,textvariable=var1,state='disabled')
        var2.set(c1_scale.max)
        s1_max=ttk.Entry(sc_win,textvariable=var2,state='disabled')
        var3.set(c1_scale.base)
        s1_base=ttk.Entry(sc_win,textvariable=var3,state='disabled')
        var4.set(c2_scale.min)
        s2_min=ttk.Entry(sc_win,textvariable=var4,state='disabled')
        var5.set(c2_scale.max)
        s2_max=ttk.Entry(sc_win,textvariable=var5,state='disabled')
        var6.set(c2_scale.base)
        s2_base=ttk.Entry(sc_win,textvariable=var6,state='disabled')
        #z_entry=ttk.Entry(sc_win,textvariable=var,state='disabled')

    if self.plotType==PlotType.ThreeDPlot:
        # get default scales PlotType.ThreeDPlot
        crv1=self.settings.Get('curve1')
        crv2=self.settings.Get('curve2')
        crv3=self.settings.Get('curve3')
        crv4=self.settings.Get('zcurve')
        my_Name=40*' '+ crv1 +15*' '+crv2 +30*' '+crv3
        CV_label.config(text=my_Name)
        c1_scale,c2_scale,c3_scale,z_scale=main.get_scale(crv1,crv2,crv3,crv4)
        c1_scale=MinMaxScale.FromString(c1_scale)
        c2_scale=MinMaxScale.FromString(c2_scale)
        c3_scale=MinMaxScale.FromString(c3_scale)
        z_scale=MinMaxScale.FromString(z_scale)
        var1=StringVar()
        var2=StringVar()
        var3=StringVar()
        var4=StringVar()
        var5=StringVar()
        var6=StringVar()
        var7=StringVar()
        var8=StringVar()
        var9=StringVar()
        var1.set(c1_scale.min)
        s1_min=ttk.Entry(sc_win,textvariable=var1,state='disabled')
        var2.set(c1_scale.max)
        s1_max=ttk.Entry(sc_win,textvariable=var2,state='disabled')
        var3.set(c1_scale.base)
        s1_base=ttk.Entry(sc_win,textvariable=var3,state='disabled')
        var4.set(c2_scale.min)
        s2_min=ttk.Entry(sc_win,textvariable=var4,state='disabled')
        var5.set(c2_scale.max)
        s2_max=ttk.Entry(sc_win,textvariable=var5,state='disabled')
        var6.set(c2_scale.base)
        s2_base=ttk.Entry(sc_win,textvariable=var6,state='disabled')
        var7.set(c3_scale.min)
        s3_min=ttk.Entry(sc_win,textvariable=var7,state='disabled')
        var8.set(c3_scale.max)
        s3_max=ttk.Entry(sc_win,textvariable=var8,state='disabled')
        var9.set(c3_scale.base)
        s3_base=ttk.Entry(sc_win,textvariable=var9,state='disabled')
        #z_entry=ttk.Entry(set_win, state='disabled')

    # done
    cancelResponse = Object()
    cancelResponse.value = False

    b_done=Button(sc_win, bg='cyan', text="Submit", command=sc_win.quit)
    b_cancel=Button(sc_win, bg='pink', text='Cancel', command= lambda:(setattr(cancelResponse, 'value', True), sc_win.quit()))

    #PLACE WIDGETS
    #Place entry boxes and labels
    if self.plotType==PlotType.CrossPlot:     # if cross plot
        SC_label.grid(row=0,column=0, columnspan=3, sticky=W)     # Place Scale entry label'
        CV_label.grid(row=1,column=0, columnspan=3, sticky=W)     # Place curve name
        s1_min.grid(row=4, column=1, pady=10)        #Place min scale entry box 1
        s1_max.grid(row=5, column=1, pady=10)       #Place min scale entry box 1
        s1_base.grid(row=6, column=1, pady=10)      #Place min scale entry box 1
        s2_min.grid(row=4, column=2, pady=10)        #Place min scale entry box 2
        s2_max.grid(row=5, column=2, pady=10)       #Place min scale entry box 2
        s2_base.grid(row=6, column=2, pady=10)      #Place min scale entry box 2
        S_l_label.grid(row=4, column=0, pady=10, sticky=W)
        S_r_label.grid(row=5, column=0, pady=10, sticky=W)
        S_b_label.grid(row=6, column=0, pady=10, sticky=W)

    elif self.plotType==PlotType.ZPlot :     # if cross plot or p_type=='pk'
        SC_label.grid(row=0,column=0, columnspan=3, sticky=W)     # Place Scale entry label'
        CV_label.grid(row=1,column=0, columnspan=3, sticky=W)     # Place curve name
        s1_min.grid(row=4, column=1)        #Place min scale entry box 1
        s1_max.grid(row=5, column=1)       #Place min scale entry box 1
        s1_base.grid(row=6, column=1)      #Place min scale entry box 1
        s2_min.grid(row=4, column=2)        #Place min scale entry box 2
        s2_max.grid(row=5, column=2)       #Place min scale entry box 2
        s2_base.grid(row=6, column=2)      #Place min scale entry box 2
        S_l_label.grid(row=4, column=0, pady=10, sticky=W)
        S_r_label.grid(row=5, column=0, pady=10, sticky=W)
        S_b_label.grid(row=6, column=0, pady=10, sticky=W)

    elif self.plotType == PlotType.Histogram: #If histogram
        SC_label.grid(row=0,column=0, columnspan=3, sticky=W)     # Place Scale entry label
        CV_label.grid(row=1,column=0, columnspan=3, sticky=W)     # Place curve name
        s1_min.grid(row=4, column=1, pady=10)        #Place min scale entry box 1
        s1_max.grid(row=5, column=1, pady=10)       #Place min scale entry box 1
        s1_base.grid(row=6, column=1, pady=10)      #Place min scale entry box 1
        S_l_label.grid(row=4, column=0, pady=10, sticky=W)
        S_r_label.grid(row=5, column=0, pady=10, sticky=W)
        S_b_label.grid(row=6, column=0, pady=10, sticky=W)

    elif self.plotType==PlotType.ThreeDPlot:   # if  3d
        SC_label.grid(row=0,column=0, columnspan=3, sticky=W)     # Place Scale entry label'
        CV_label.grid(row=1,column=0, columnspan=3, sticky=W)     # Place curve name
        s1_min.grid(row=4, column=1)        #Place min scale entry box 1
        s1_max.grid(row=5, column=1)       #Place min scale entry box 1
        s1_base.grid(row=6, column=1)      #Place min scale entry box 1
        s2_min.grid(row=4, column=2)        #Place min scale entry box 2
        s2_max.grid(row=5, column=2)       #Place min scale entry box 2
        s2_base.grid(row=6, column=2)      #Place min scale entry box 2
        s3_min.grid(row=4, column=3)        #Place min scale entry box 1
        s3_max.grid(row=5, column=3)       #Place min scale entry box 1
        s3_base.grid(row=6, column=3)      #Place min scale entry box 1
        S_l_label.grid(row=4, column=0, pady=10, sticky=W)
        S_r_label.grid(row=5, column=0, pady=10, sticky=W)
        S_b_label.grid(row=6, column=0, pady=10, sticky=W)


    #set widgets to normal
    if self.plotType==PlotType.CrossPlot:     # if cross plot
        s1_min.config(state='normal' )       #min scale entry box 1
        s1_max.config(state='normal' )       #min scale entry box 1
        s1_base.config(state='normal' )      #min scale entry box 1
        s2_min.config(state='normal' )       #min scale entry box 2
        s2_max.config(state='normal' )       #min scale entry box 2
        s2_base.config(state='normal' )      #min scale entry box 2

    elif self.plotType==PlotType.ZPlot:     # if cross plot
        s1_min.config(state='normal')       #min scale entry box 1
        s1_max.config(state='normal')       #min scale entry box 1
        s1_base.config(state='normal')      #min scale entry box 1
        s2_min.config(state='normal')       #min scale entry box 2
        s2_max.config(state='normal')       #min scale entry box 2
        s2_base.config(state='normal')      #min scale entry box 2

    elif self.plotType == PlotType.Histogram: #If histogram
        s1_min.config(state='normal')       #min scale entry box 1
        s1_max.config(state='normal')       #min scale entry box 1
        s1_base.config(state='normal')      #min scale entry box 1

    elif self.plotType==PlotType.ThreeDPlot:   # if  3d
        s1_min.config(state='normal')       #min scale entry box 1
        s1_max.config(state='normal')       #min scale entry box 1
        s1_base.config(state='normal')      #min scale entry box 1
        s2_min.config(state='normal')       #min scale entry box 2
        s2_max.config(state='normal')       #in scale entry box 2
        s2_base.config(state='normal')      #min scale entry box 2
        s3_min.config(state='normal')       #min scale entry box 1
        s3_max.config(state='normal')       #min scale entry box 1
        s3_base.config(state='normal')      #min scale entry box 1


    b_done.grid(row=8, column=2, pady=10)
    b_cancel.grid(row=8, column=3, pady=10)

    #Update Plot files
    sc_win.mainloop()


    if cancelResponse.value == False:               # if plt_settings NOT cancelled
        #update plt_stgs
        if self.plotType==PlotType.CrossPlot:
            self.settings.Set('c1_scale', s1_min.get() + ',' + s1_max.get() + ','+s1_base.get())
            self.settings.Set('c2_scale', s2_min.get() + ',' + s2_max.get() + ','+s2_base.get())

        elif self.plotType==PlotType.ZPlot:
            self.settings.Set('c1_scale', s1_min.get() + ',' + s1_max.get() + ','+s1_base.get())
            self.settings.Set('c2_scale', s2_min.get() + ',' + s2_max.get() + ','+s2_base.get())

        elif self.plotType==PlotType.ThreeDPlot:
            #get all plot parameters into a simple array before destroying the settings window and save ut as a default or settings file
            self.settings.Set('c1_scale', s1_min.get() + ',' + s1_max.get() + ','+s1_base.get())
            self.settings.Set('c2_scale', s2_min.get() + ',' + s2_max.get() + ','+s2_base.get())
            self.settings.Set('c3_scale', s3_min.get() + ',' + s3_max.get() + ','+s3_base.get())

        elif self.plotType==PlotType.Histogram:
            #get all plot parameters into a simple array before destroying the settings window and save ut as a default or settings file
            #c1_scale,c2_scale,c3_scale,z_scale=get_scale(crv1.get(),"","","")
            #c1_min, c1_max, c1_base=get_minmaxscale(c1_scale)
            self.settings.Set('c1_min', s1_min.get())
            self.settings.Set('c1_max', s1_max.get())
            self.settings.Set('c1_base', s1_base.get())
            self.settings.Set('c1_scale', s1_min.get() + ',' + s1_max.get() + ','+s1_base.get())

        #save default plot file ext . plot type xp, hg, zp or 3d
        self.SaveDefaultSettings()

    else:   # if canceled
        sc_win.deiconify()

    sc_win.destroy()
