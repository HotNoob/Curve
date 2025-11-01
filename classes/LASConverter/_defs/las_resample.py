'''las_resample'''

import pandas as pd
import global_vars

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import LASConverter

# --------------------------------------------------------------------------------------
def las_resample(self : 'LASConverter', las_data):
    '''
    Eucalyptus default depth increment is 0.1m
    also round start depth to 1 place behind desmo point
    All converted las files are using this step
    '''

    global_vars.perfTest.Start('las_resample')

    df=las_data.df()                                #old data frame
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

    # Optimized code
    #reindex dataframe / resample
    df = df.reindex(mdpt, method='bfill').astype('object') #interpolate()
    df.index.name = 'DEPT'

    las_df = df

    #global_vars.perfTest.Stop('las_resample optimized fill df')  RESAMPLE STOP

    #update las_data for las_df
    mynull=round(las_data.well.NULL.value,2)
    las_df.fillna(mynull)
    las_data.set_data(las_df)
    #Update lasdata for new step
    las_data.well.STEP.value=round(cstep,1)

    #global_vars.perfTest.Stop('las_resample')

    return las_data                 #NOT global