

import glob
import os
from tkinter import EW, Button, E, Label, StringVar, W, ttk

import numpy as np
import pandas as pd
from matplotlib import pyplot as pyplot

from enumerables import Dir
#import matplotlib.pyplot as plt
import global_vars
from classes.Object import Object
from classes.Settings import Settings
from defs import alert, common, excel, las, main, program, prompt, tools


class Normalizer:
    def __init__(self):
        self.settings : Settings = None

    @classmethod
    def newNormalize(cls):
        normalizer = cls()
        normalizer.normalize()
        return normalizer

    def normalize(self):
        '''
        Create Normalize window to select well_list
        Open toplevel window to enter options and curve to be normalized
        '''
        #load_wellist(0)        #get suitable well list
        if len(global_vars.project.currentWellList)>15:
            alert.Error("Your test well list exceeds 15 wells")
            return

        global_vars.ui.Root.window.iconify()

        # Get or set settings
        #Ask for default settings
        if not prompt.yesno('Use Default Plot Settings?'):
            # re-enter settings
            if not self.newSettingsMenu(): #if settings cancelled
                global_vars.ui.Root.window.deiconify()
                return
        else:
            if not self.Load(): #if settings failed to load / empty
                alert.Message('Default Settings Failed to Load, or Are Empty')
                global_vars.ui.Root.window.deiconify()
                return

        # Get Zone Data
        excel.get_zone()

        #load Alias settings with previous selected path or default path
        crv_list=[]

        no_crvs=['DEPT','RT','DT','TEMP','BIT']
        crv_list=program.com_crvs(no_crvs,crv_list,1)

        crv1=self.settings.Get('curve')
        zone=self.settings.Get('zone')

        #initialize dfs
        global_vars.las_df=pd.DataFrame(None)
        # Create a list of data frames for each well
        df_list = []
        count = 0
        for well in global_vars.project.currentWellList.GetWells():        #cycle through wells and loadLAS
            zoneDepths = None

            #Set measured, core or formation depth interval interval
            if zoneDepths is None:                      #If dpt_int empty
                zoneDepths = well.GetZoneDepths(zone)

                if zoneDepths is None:
                    global_vars.ui.Root.window.deiconify()
                    alert.RaiseException(f'Zone {zone} not in {well.uwi} - remove from well list')

            las_data = well.GetLASData(Dir.In)
            #load plot data from LAS and/or core
            if las_data is None:   #No las file in Indir
                global_vars.ui.Root.window.deiconify()
                return

            # get las data frame
            #df = las_data.df()

            # Find alias curve names for selected zone
            global_vars.las_df,found_fl= main.find_aka(crv1, crv_list, 1, las_data, 1, zoneDepths)
            #opt 1 is for normalizing plots
            if found_fl!=1:                   # crv1 was NOT found
                alert.Error(f"{crv1} was not in {well.uwi}({well.alias})")
                main.show_las(well.uwi+".las")
                global_vars.ui.Root.window.deiconify()
                return     # go back to graphs and start over

            df_list.append(global_vars.las_df.copy(deep=True))
            #count +=1

        #Now we should be ready to run Normal
        # sizing script
        # Working data frame
        
        #data = df_list[0]+df_list[1]+df_list[2]+df_list[3]+df_list[4]
        data=pd.concat(df_list,sort=True)    #convert to a concatenated dataframe
        data.replace(-999.25, np.NaN, inplace=True)
        data['UWI'].unique()
        mwells = data.groupby('UWI')

        #Kernel Density Estimation (KDE) Distribution
        #Plotting the Raw Data
        fig, ax = pyplot.subplots(figsize=(10,8))
        ''' Where is the BUG???   Set in Anaconda P10_euky Aug 28 2023 Environment'''
        for label, dfw in mwells:
            try:
                dfw[crv1].plot(kind ='kde', ax=ax, label=label)
                
                #sns.distplot(df[crv1],bins=20,kde=True,ax=ax)
            except Exception:
                alert.Error(f"{label} caused error in plot data - delete from well list")
                global_vars.ui.Root.window.deiconify()
                #continue
                #return
            
        pyplot.xlim(float(self.settings.Get('c_min')), float(self.settings.Get('c_max')))
        pyplot.xlabel(crv1)
        ax.minorticks_on()
        ax.grid(which='major', linestyle='-', linewidth='0.75', color='silver')
        ax.grid(which='minor', linestyle=':', linewidth='0.5', color='silver')
        ax.set_axisbelow(True)
        pyplot.legend()
        pyplot.tight_layout()
        fig.canvas.mpl_connect('button_press_event',lambda e: self.on_mclick(fig,data))            #on click left mouse button

        pyplot.show(block=True)

        mwells.min()

        """
        Calculating the Percentiles - Quantile function

        The first step is to calculate the percentile (or quantile as pandas refers to it) by grouping the data by wells
        and then applying the .quantile() method to a specific column.
        In this case, GR. The quantile function takes in a decimal value,
        so a value of 0.05 is equivalent to the 5th percentile and 0.95
        is equivalent to the 95th percentile

        """
        #Plow
        percentile_low = data.groupby('UWI')[crv1].quantile(float(self.settings.Get('p_low'))/100)

        # the map() will combine two data series that share a common column
        data['LO_PERC'] = data['UWI'].map(percentile_low)

        #Phigh
        percentile_high = data.groupby('UWI')[crv1].quantile(float(self.settings.Get('p_high'))/100)
        data['HI_PERC'] = data['UWI'].map(percentile_high)

        #collect well highs and lows
        # Normalization Equation also to be used for 'Rescale' but with different
        def normalise(curve, ref_low, ref_high, well_low, well_high):
            return ref_low + ((ref_high - ref_low) * ((curve - well_low) / (well_high - well_low)))

        #Using the percentiles calculated in the previous step
        #we can set our reference high and low values:

        key_well_low = float(self.settings.Get('key_low'))
        key_well_high = float(self.settings.Get('key_high'))

        c_name=crv1+"_NRM"             # create normalized curve name

        #apply the function to each value and use the correct percentiles for each well we can use the .apply() method
        #to the pandas dataframe and then a lamda function for our custom function.
        data[c_name] = data.apply(lambda x: normalise(x[crv1], key_well_low, key_well_high, x['LO_PERC'], x['HI_PERC']), axis=1)
        # Final plots
        fig = pyplot.figure(figsize=(14,6))
        fig.subplots_adjust(top=0.85, wspace=0.3)

        ax0 = fig.add_subplot(1, 2, 1)
        for label, dfw in mwells:
            dfw[crv1].plot(kind ='kde', ax=ax0, label=label)

        pyplot.xlim(float(self.settings.Get('c_min')), float(self.settings.Get('c_max')))
        pyplot.xlabel(crv1)
        ax0.minorticks_on()
        ax0.grid(which='major', linestyle='-', linewidth='0.75', color='silver')
        ax0.grid(which='minor', linestyle=':', linewidth='0.45', color='silver')
        ax0.set_axisbelow(True)
        pyplot.legend()

        ax1 = fig.add_subplot(1, 2, 2)
        for label, df in mwells:
            df[c_name].plot(kind ='kde', ax=ax1, label=label)

        pyplot.xlim(float(self.settings.Get('c_min')), float(self.settings.Get('c_max')))
        pyplot.xlabel(c_name)
        ax1.minorticks_on()
        ax1.grid(which='major', linestyle='-', linewidth='0.75', color='silver')
        ax1.grid(which='minor', linestyle=':', linewidth='0.45', color='silver')
        ax1.set_axisbelow(True)
        pyplot.legend()
        #cid = fig.canvas.mpl_connect('button_press_event',pyplot.close())            #on click left mouse button
        pyplot.show()
        #fig.canvas.mpl_connect('button_press_event',lambda e: pyplot.close())            #on click left mouse button
        myes = prompt.yesno('Normalize a well list with these settings?')
        pyplot.close()
        #curDir=os.getcwd()
        if myes==True:
            global_vars.ui.Root.window.deiconify()
            #Curve.load_wellist(0)
            global_vars.project.loadWellListPrompt()
            crv_list=[]   #reset curve list
            crv_list=program.com_crvs(no_crvs,crv_list,1)
            if self.settings.Get('curve') not in crv_list:
                alert.Error(self.settings.Get('curve')+' not in Well_list, select or edit lis')
                return

            #remove data dataframe
            del data

            count=0
            myes=False
            total_wells=str(len(global_vars.project.currentWellList))
            global_vars.ui.Root.c_mylabel.configure(text='start normalizing '+ total_wells + " wells")  # clear my label
            for well in global_vars.project.currentWellList.GetWells():        #cycle through wells and loadLAS
                #clear well depthzone interval
                zoneDepths = None
                zone='WELL'   #normalize entire well

                #get crv1 for entire well
                las_data = well.GetLASData(Dir.In)

                #get min and max for each well IN NORMALIZING ZONE
                if zoneDepths is None:                      #If dpt_int empty
                    zoneDepths = well.GetZoneDepths(zone)

                if zoneDepths is None:
                    global_vars.ui.Root.window.deiconify()
                    alert.RaiseException(f'Zone {zone} not in {well.uwi}({well.alias}) - remove from well list')

                global_vars.las_df,found_fl= main.find_aka(crv1, crv_list, 1, las_data, 1, zoneDepths)   #find las_df accross selected zone
                if found_fl!=1:                   # crv1 was NOT found
                    alert.Error(f"{crv1} was not in {well.uwi}({well.alias})")
                    main.show_las(well.uwi + ".las")
                    global_vars.ui.Root.window.deiconify()
                    return     # go back to graphs and start over

                prc_hig=global_vars.las_df.quantile(float(self.settings.Get('p_high'))/100)
                prc_low=global_vars.las_df.quantile(float(self.settings.Get('p_low'))/100)
                
                #get las already in Outdir or create a new one
                new_las = well.GetLASData(Dir.Out)
                if new_las is None:
                    if myes==False:
                        myes=prompt.yesno(f"Creating new {well.uwi}.las in Outdir.  Show this prompt again (Y/N)?")
                        #get cleaned up lasfile
                    new_las = tools.cln_las(well.uwi + '.las')

                new_df=new_las.df()      #.iloc[idx_top:idx_bot]
                new_df[c_name]=np.nan       #create empty normalized curve
                new_df[c_name].to_frame()   #convert series to dataframe

                global_vars.las_df[crv1].replace(-999.25,np.nan,inplace=True)     #replace all -999.25 with p.nan in crv1
                #add normalized curve to new_las curve, ref_low, ref_high, well_low, well_high
                new_df[c_name]=global_vars.las_df.apply(lambda x: normalise(x[crv1], key_well_low, key_well_high, prc_low, prc_hig), axis=1)
                #new_df.iloc[idx_top:idx_bot][c_name] = prc_low + ((prc_hig - prc_low) * ((las_df[crv1] - key_well_low) / (key_well_high - key_well_low)))

                # save to filename
                new_las.set_data(new_df)
                crv2=program.get_aka(crv1, las_data)
                new_las.curves[c_name].unit=las_data.curves[crv2].unit
                new_las.curves[c_name].descr=f'{c_name} BY EUCALYPTUS CONSULTING INC'
                newFile = global_vars.project.outDir + '/' + well.uwi + '.las'
                new_las.write(newFile, fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)

                if well.GetWellFile(Dir.Out) is None:
                    well.AddWellFile(newFile)

                count +=1
                global_vars.ui.Root.c_mylabel.configure(text='Well '+str(count) + ' of ' + total_wells)
                global_vars.ui.Root.window.update_idletasks()
                
        alert.Message('Done')
        global_vars.ui.Root.c_mylabel.configure(text="")
        global_vars.ui.Root.window.update_idletasks()
        global_vars.project.Scan()
        #root.deiconify()
    #-----------------------------------------------------------------------------------------------------------------------
    def on_mclick(self, fig, data):
        '''
        Update settings and close plot
        '''

        nrm_win = common.initCommonWindow('Update settings', 250, 300)

        #Select Key Well
        #create combobox well list
        w_list=[]
        for uwi in global_vars.project.currentWellList:
            w_list.append(uwi)
        idx=0
        if self.settings.Get('KeyWell')!='0':
            key_well=self.settings.Get('KeyWell')
            for uwi in w_list:
                if uwi == key_well:
                    break
                idx +=1
        else:
            idx=0

        T_label0=Label(nrm_win, text="Select Benchmark Well")           #Entrybox label 3
        key_well=ttk.Combobox(nrm_win, value=w_list)
        key_well.current(idx)
        k_well=key_well.get()
        self.settings.Set('KeyWell', k_well)
        key_well.bind('<<ComboboxSelected>>', lambda e: self.kwell_select(key_well.get(),var1,var2, data))

        crv1=self.settings.Get('curve')

        if self.settings.Get('method')=='Percentile':
            #calculate P10 and p90 for key well
            percentile_low = data.groupby('UWI')[crv1].quantile(0.1)
            percentile_high = data.groupby('UWI')[crv1].quantile(0.9)

            T_label=Label(nrm_win,text="Update Key Well parameters")

            var1=StringVar()
            var2=StringVar()
            var3=StringVar()
            var4=StringVar()
            T_label1=Label(nrm_win, text="Well Low")      #Entrybox label 1
            T_label2=Label(nrm_win, text="Well High")     #Entrybox label 2
            T_label3=Label(nrm_win, text="P low")         #Entrybox label 6
            T_label4=Label(nrm_win, text="P high")        #Entrybox label 7

            var1.set(percentile_low[k_well])
            w_low=ttk.Entry(nrm_win,textvariable=var1)
            var2.set(percentile_high[k_well])
            w_high=ttk.Entry(nrm_win,textvariable=var2)
            var3.set(self.settings.Get('p_low'))
            p_low=ttk.Entry(nrm_win,textvariable=var3)
            var4.set(self.settings.Get('p_high'))
            p_high=ttk.Entry(nrm_win,textvariable=var4)

            # done
            b_done=Button(nrm_win, bg='cyan', text="Submit", command = lambda: self.upd_quit(var1.get(), var2.get(),var3.get(), var4.get(),nrm_win))
            b_cancel=Button(nrm_win, bg='pink', text='Cancel', command=nrm_win.quit)

            T_label.grid(row=0,column=0)
            T_label0.grid(row=1,column=0, sticky=W)
            T_label1.grid(row=3, column=0, sticky=W, pady=5)
            T_label2.grid(row=5, column=0, sticky=W, pady=5)
            T_label3.grid(row=3,column=1, sticky=W)
            T_label4.grid(row=5,column=1, sticky=W)                     #key well

            key_well.grid(row=2,column=0, pady=5)                       # place Key Well combo
            w_low.grid(row=4,column=0,padx=5, pady=5, sticky=W)         # place Entry box Key_Low
            w_high.grid(row=6,column=0, padx=5,pady=5, sticky=W)          # place Entry box Key High
            p_low.grid(row=4,column=1,padx=5, pady=5, sticky=W)         # place Entry box Key_Low
            p_high.grid(row=6,column=1, padx=5,pady=5, sticky=W)          # place Entry box Key High

            b_done.grid(row=7, column=0,pady=5)
            b_cancel.grid(row=8, column=0, pady=5)

            nrm_win.mainloop()
        else:
            return

        pyplot.close(fig)
        nrm_win.destroy()
    #-----------------------------------------------------------------------------------------------------------------------
    def upd_quit(self, keyLow, keyHigh, pLow, pHigh, nrm_win):

        self.settings.Set('Key_Low', keyLow)
        self.settings.Set('Key_high', keyHigh)
        self.settings.Set('P_Low', pLow)
        self.settings.Set('P_high', pHigh)
        self.Save()
        nrm_win.quit()
    #=======================================================================================================================
    def newSettingsMenu(self) -> bool:
        # Get Zone Data
        excel.get_zone()

        crv_list=[]

        no_crvs=['DEPT','RT','DT','TEMP','BIT']
        crv_list=program.com_crvs(no_crvs,crv_list,1)


        #create combobox list of zones
        z_list= list(global_vars.project.formationZones.keys())

        meth_list=['Percentile', 'Rescale']

        #create Toplevel
        nrm_win = common.initCommonWindow('Normalizing Options', 430, 320)

        #SET WIDGETS
        # create labels
        T_label=Label(nrm_win, text="Select Normalizing Options", font=('Helvetica',12))    #MAIN label
        T_label1=Label(nrm_win, text="Select curve (alias)")         #Combobox label 1
        T_label2=Label(nrm_win, text="Select Normalizing Zone")       #Combobox label 2
        T_label3=Label(nrm_win, text="Select Method")                 #Combobox label 3
        T_label8=Label(nrm_win, text="Set Scale")        #Entrybox label 7

        # create comboboxes
        crv=ttk.Combobox(nrm_win, value=crv_list)
        crv.current(0)
        sc1=StringVar()
        sc1.set('min')
        c_scmin=ttk.Entry(nrm_win,textvariable=sc1)
        sc2=StringVar()
        sc2.set('max')
        c_scmax=ttk.Entry(nrm_win,textvariable=sc2)
        zone=ttk.Combobox(nrm_win, value=z_list)
        zone.current(0)
        meth=ttk.Combobox(nrm_win, value=meth_list)
        meth.current(1)

        # done
        buttonResponses = Object()
        buttonResponses.cancel = False

        b_done=Button(nrm_win, bg='cyan', text="Submit", command=nrm_win.quit)
        b_cancel=Button(nrm_win, bg='pink', text='Cancel', command=lambda:(setattr(buttonResponses, 'cancel', True), nrm_win.quit()) )
        #+++++++++++++++++
        #PLACE WIDGETS BASED ON PLOT TYPE and SET STATE TO NORMAL

        # Place T_Label
        T_label.grid(row=0,column=0, columnspan=2, sticky=EW, pady=10)
        T_label1.grid(row=1,column=0, sticky=W)
        T_label2.grid(row=5,column=0, sticky=W)
        T_label3.grid(row=7,column=0, sticky=W)
        T_label8.grid(row=3,column=0, sticky=W)       #scale labels

        #Place comboboxes, entry boxes and labels
        crv.grid(row=2, column=0, pady=5)      # place crv selection box 1
        c_scmin.grid(row=4, column=0,pady=2, sticky=W)   # place Entry box scale min
        c_scmax.grid(row=4, column=1,pady=2)   # place Entry box scale max
        zone.grid(row=6, column=0, pady=2)     # place zone selection box 2
        meth.grid(row=8,column=0, pady=5)      # place method selection box 3

        b_done.grid(row=11, column=0,pady=5, sticky=W)
        b_cancel.grid(row=11, column=0, pady=5, sticky=E)

        #loop and destroy when done
        nrm_win.mainloop()

        if buttonResponses.cancel:
            return False
        else:
            #record nrm_settings
            self.settings = Settings(global_vars.project.inDir+'/databases/default.nrm')
            self.settings.LoadFromArray([
                                                        ['curve',crv.get()],
                                                        ['C_min',sc1.get()],
                                                        ['C_max',sc2.get()],
                                                        ['Zone',zone.get()],
                                                        ['method',meth.get()],
                                                        ['KeyWell','0'],
                                                        ['Key_Low','0'],
                                                        ['Key_high','0'],
                                                        ['P_Low','10'],
                                                        ['P_high','90']
                                                    ])

            # save and close nrm_win
            self.Save()
            nrm_win.destroy()
            return True
    #-------------------------------------------------------------------------------------------
    def Save(self):
        self.settings.Save()
    #-------------------------------------------------------------------------------------------------
    def Load(self) -> bool:
        '''
        load settings from default.nrm
        '''
        self.settings = Settings(global_vars.project.inDir+'/databases/default.nrm')

        return self.settings.Load()
    #-------------------------------------------------------------------------------------------
    def kwell_select(self, keywell,var1, var2, data):

        self.settings.Set('KeyWell', keywell)
        crv1=self.settings.Get('curve')

        if self.settings.Get('method')=='Percentile':
            #calculate P10 and p90 for key well
            percentile_low = data.groupby('UWI')[crv1].quantile(0.1)
            percentile_high = data.groupby('UWI')[crv1].quantile(0.9)
            var1.set(percentile_low[keywell])
            var2.set(percentile_high[keywell])