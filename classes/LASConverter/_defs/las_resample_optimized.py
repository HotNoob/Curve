'''las_resample'''

import numpy as np
import pandas as pd
import global_vars

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import LASConverter

# --------------------------------------------------------------------------------------
def las_resample_optimize_test(self : 'LASConverter', las_data):
    '''
    Eucalyptus default depth increment is 0.1m
    also round start depth to 1 place behind desmo point
    All converted las files are using this step
    '''

    global_vars.perfTest.Start('las_resample')

    df : pd.DataFrame =las_data.df()                                #old data frame
    cstart=round(las_data.well.STRT.value,1)
    cstop=round(las_data.well.STOP.value,1)
    cstep=0.1
    #Update lasdata for new step

    #create new dept index
    dpt=cstart
    mdpt=[]                     #Create empty new depth curve
    while dpt <= cstop:
        mdpt.append(dpt)
        dpt +=cstep
        dpt=round(dpt,1)

    global_vars.perfTest.Start('las_resample optimized fill df')

    checkEquals = False
    if checkEquals:
        # Optimized code
        #create new dataframe
        las_df_opt=pd.DataFrame(index=mdpt,columns=df.columns)
        las_df_opt.index.name='DEPT'


        # fill in new data frame with updated curvedata
        indexLen = len(df.index)
        o_idx=0
        o_dpt=df.index[o_idx]
        for dpt in las_df_opt.index:
            if dpt<= o_dpt:
                las_df_opt.loc[dpt,:] = df.loc[o_dpt,:]
            else:
                while o_dpt<=dpt:
                    if o_idx < indexLen-1:
                        o_idx +=1
                        o_dpt=df.index[o_idx]
                        las_df_opt.loc[dpt,:]=df.loc[o_dpt,:]
                    else:
                        o_dpt=df.index[o_idx]+cstep  #end of df

    global_vars.perfTest.Stop('las_resample optimized fill df')
    global_vars.perfTest.Start('las_resample fill df')

    #create new dataframe
    #optimize 2
    #df.index = np.round(df.index, 1)
    #df.index.drop_duplicates(keep="first")
    #df = df.interpolate(method='ffill')

    #optimize 3 -- almost identical
    df = df.reindex(mdpt, method='bfill').astype('object') #interpolate()
    df.index.name = 'DEPT'

    global_vars.perfTest.Stop('las_resample fill df')
    #test results
    if checkEquals:
        optimized = df.equals(las_df_opt)
        print(optimized)

    las_df = df

    #update las_data for las_df
    mynull=round(las_data.well.NULL.value,2)
    las_df.fillna(mynull)
    las_data.set_data(las_df)
    #Update lasdata for new step
    las_data.well.STEP.value=round(cstep,1)

    global_vars.perfTest.Stop('las_resample')

    return las_data                 #NOT global