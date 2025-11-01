#----------------------------------------------------------------------------------------------------------
def c_collect(opt):
    '''
    collect basic parameteres and list of curves in Indir (P_crvs)
    option 0: refresh - load lists
    option 1: update lists
    '''
    global P_crvs    #List of all Indir Curves in Project
    global T_grad   #List of gradients per well
    global c_fm
    global alias_arr

    Curdir = os.getcwd()
    os.chdir(Indir)

    #update c_fm for Start and TD
    if c_fm == []:   #If not yet loaded
        loadFM()
    P_crvs=[]        #Reset Curve List
    alias_arr=load_alias()
    if opt==0: #load P_crvs
        loadCL()
        if P_crvs==[]:
            opt=1
        else:
            return
    for t_alias in alias_arr:       #get alias and AKA fir 'TEMP'
        if t_alias[0]=='TEMP':
            break

    #if PetroNinja data (or GeoScout??)
    PN_flag=True
    try:
        # Create filelist
        os.chdir(Indir)
        las_list = glob.glob("*.las")               #Wells in RAW Dir
    except Exception:
        c_Message('Not a PetroNinja source')
        print(traceback.format_exc())
        PN_flag=False

    if PN_flag==False:
        try:
            # Create filelist
            os.chdir(Rawdir)
            las_list = glob.glob("*.las")               #Wells in RAW Dir
        except Exception:
            c_Message('First select Rawdir for input and Indir for output Directories at File menu>Directories or load project')
            print(traceback.format_exc())
    mylen = len(las_list)
    counter = 0   # intialize file counter
    if c_fm==[]:    #if new c_fm
        Ncfm=1
    else:
        Ncfm=0

    for file in las_list:
        counter += 1
        # Report progress
        myTXT = 'File '+ str(counter) +  ' of '  + str(mylen) + ' files into ' + Indir + ": " + file
        c_mylabel.configure(text=myTXT)

        # Open and read file with LASIO library as LS
        las_data = LS.read(file)      
        
        muwi=file[:16]
        mstart = las_data.well.STRT.value
        mTD = las_data.well.STOP.value
            
        #find well in c_fm
        index=0
        foundFlag=0
        foundWell=0        
        
        if Ncfm==1:    #If new curve 3 Tops file
            c_fm.append([muwi,"START","EUC",str(mstart)])
            c_fm.append([muwi,"TD","EUC",str(mTD)])
        for well in c_fm:           #look for wells in c_fm
            if muwi==well[0]:
                foundWell=1
                break
        if foundWell==0:   #if well not in c_fm then add
            c_fm.append([muwi,"START","EUC",str(mstart)])
            c_fm.append([muwi,"TD","EUC",str(mTD)])            
        else:
            for well in c_fm:    #cycle throug all UWI rows
                if well[0]==muwi and well[1]=='START' :    #skip
                    foundFlag=1     #Well found
                    index +=1
                    if index==len(c_fm)-1:            #end of c_fm
                        index -=1    #prevent exceeding c_fm
                    continue  #next line
                if well[0]==muwi and well[1]!='START' and foundFlag==0:
                    c_fm.insert(index,[muwi,"START","EUC",str(mstart)])
                    foundFlag=1     #Well found
                if foundFlag==1 and c_fm[index+1][0]!=muwi :
                    if well[1]=='TD':
                        well[3]=str(mTD)
                        index +=1
                        foundFlag=0 #reset
                        if index==len(c_fm)-1:            #end of c_fm
                            continue  #next line
                    else: 
                        c_fm.insert(index+1,[muwi,"TD","EUC",str(mTD)])
                index +=1
                if index==len(c_fm)-1:            #end of c_fm
                    if well[0]==muwi:
                        if well[1]=='TD':
                            well[3]=str(mTD)
                        else:
                            c_fm.append([muwi,"TD","EUC",str(mTD)])
                        break

        ##ALL curvenames in INDIR 
        index=0
        T_found=0
        for crv in las_data.curves:
            if index>0:
                P_crvs.append([muwi,crv.mnemonic])
                if T_found==0:
                    for T in t_alias:
                        if crv.mnemonic==T:
                            T_found=1
            index +=1
        #check for BIT.MM and TEMP.C  or aka
        P_crvs.append([muwi,'BIT'])
        if T_found==0:
            P_crvs.append([muwi,'TEMP'])    

        if 'TMAX' in las_data.params and 'TDD' in las_data.params:    #no TMAX and TDD in kas file skip
            if las_data.params.TMAX.value>0 and las_data.params.TDD.value>0:
                mT_grad = (las_data.params.TMAX.value - 6) / mTD
                T_grad.append([muwi,mT_grad])

            tlist=T_grad
            tlen=len(tlist)
            if tlen>1:
                TGRAD_Av=0  # reset average gradient
                for t in tlist:
                    TGRAD_Av=TGRAD_Av + t[1]   #sum tlist column 1

                TGRAD_Av=TGRAD_Av/tlen
            else:
                TGRAD_Av=tlist[0][1]
        else: 
            pass
            
        c_mylabel.configure(text='Done')

    os.chdir(Indir)    #change back from RAWdir to Indir to save results
    mpath='databases/Curve 3 Tops.TXT'
    with open(mpath,'w') as f:
        for mline in c_fm:
            record=''
            for it in mline: #Create a string
                record=record + it+ ','
            # write Frm data 
            record=record[:-1]+'\n'    
            f.write(record)
        f.close()
    
    #Update/create curves file P_crvs
    c_Message("Saving new P_CRVS in ALLcurves.TXT ")
    save_Pcrvs()
    P_crvs=[]           #reset

    #store in params xlsx
    mpath='databases/Params.xlsx'
    ws=Workbook()
    wb=load_workbook(mpath)
    if wb==None:
        c_Error(f'{mpath} not found in Indir - Ensure there is a Project Parameter Spreadsheet')
    else:
        #get active worksheet
        ws=wb.active
        column_a=ws['A']
        column_b=ws['B']
        row=0
     
        for cell in column_a:
            if cell.value=='TGRAD_Av':
                column_b[row].value=TGRAD_Av
                break
            row +=1

        #save update
        wb.save(mpath)

    #Restore working directory
    os.chdir(Curdir)
    if opt==1:  #update loaded data bases
        main_wells()
# ----------------------------------------------------------------------------------------------------------
def save_Pcrvs():
    '''
        Save the Indir Curve List
    '''
    global P_crvs

    curDir=os.getcwd()
    os.chdir(Indir)
    mpath='databases/ALLcurves.TXT'
    with open(mpath,'w') as f:
        for mline in P_crvs:
            record=''
            for it in mline: #Create a string
                record=record + it+ ','
            # write Frm data 
            record=record[:-1]+'\n'    
            f.write(record)
        f.close()
   
    os.chdir(curDir)
#------------------------------------------------------------------------------------
def save_MissCrvs():
    '''
        Save curves of well list with curves not in Alias file
    '''
    global mis_lst

    curDir=os.getcwd()
    os.chdir(Indir)
    mpath='databases/Misscurves.TXT'
    with open(mpath,'w') as f:
        for mline in mis_lst:
            record=''
            for it in mline: #Create a string
                record=record + it+ ','
            # write Frm data 
            record=record[:-1]+'\n'    
            f.write(record)
        f.close()
   
    os.chdir(curDir)