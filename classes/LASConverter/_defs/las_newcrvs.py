'''Las_NewCrvs'''
import global_vars

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import LASConverter

def Las_NewCrvs(self : 'LASConverter', las_dat, TGRAD_Av):
    T_surf = 6.0   # mulitannual default surface temparture is 6 degrees celcius

    t_alias = global_vars.project.curveNameTranslator.GetAliases('TEMP')

    # Determine number of curves already in LAS file
    No_Curves = len(las_dat.curves)
    T_found=0
    for curve in las_dat.curves:
        if curve.mnemonic in t_alias:
            T_found=1
            break

    if T_found==0:  #If NO temp curve in las file
        try:
            if las_dat.params.TMAX.value ==0 or las_dat.params.TDD.value==0:
                # use default gradient  CONSIDER another method
                T_grad = TGRAD_Av #From Params.xlsx
            else:
                T_grad = (las_dat.params.TMAX.value - T_surf) / las_dat.params.TDD.value
        except Exception:
            # use default gradient
            T_grad = TGRAD_Av #From Params.xlsx

    df = las_dat.df()
    # Create Bitsize curve BIT
    df['BIT'] = las_dat.params.BS.value

    #if no temp curve create one
    # Create Temperature curve
    if T_found==0:  #If NO temp curve in las file
        mylist = []
        for dept in las_dat['DEPT']:
            mylist.append(T_surf+dept*T_grad)
        df['TEMP'] = mylist   # Copy list into PD array
   # Update las_dat
    las_dat.set_data(df)

    # update BIT and TEMP units and description
    las_dat.curves.BIT.unit = 'MM'
    x = int(No_Curves)+1
    
    las_dat.curves.BIT.descr = str(x) + ' BIT SIZE LOG'
    if T_found==0:  #If NO temp curve in las file
        x += 1
        las_dat.curves.TEMP.unit = 'C'
        las_dat.curves.TEMP.descr = str(x) + ' EUCALYPTUS BHT TEMPERATURE LOG'