'''Las_Units'''

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import LASConverter

# ===========================================================================================
def las_units(self : 'LASConverter', las_dat):
    df = las_dat.df()
    
    for curve in range(1, len(las_dat.curves)):
        # Get units
        my_curve = las_dat.curves[curve].mnemonic
        my_unit = str(las_dat.curves[curve].unit).strip().upper()
        match my_unit:
            case 'V/V':
                my_P75 = df[my_curve].quantile(q=0.75)
                if my_P75 > 1:
                    # converst to fractions
                    df[my_curve] = df[my_curve]/100

            case 'PU' | '%' | 'PCNT':
                las_dat.curves[curve].unit = 'V/V'
                my_P75 = df[my_curve].quantile(q=0.75)
                if my_P75 > 1:
                    # converst to fractions
                    df[my_curve] = df[my_curve]/100

            case 'G/CM3':  #if unit error in LAS commonly DRHO
                las_dat.curves[curve].unit = 'G/CM3'
                test=df[my_curve].abs()
                my_P75 = test.quantile(q=0.75)
                if my_P75 > 10.0:          # conflict between units and values - correct
                    # convert by dividing by 1000
                    df[my_curve] = df[my_curve]/1000

            case 'K/M3' | 'KG/M3' | 'KGM3' | 'KM3':
                # Convert to Kg/m3 if not already done
                las_dat.curves[my_curve].unit = 'G/CM3'
                test=df[my_curve].abs()
                my_P75 = test.quantile(q=0.75)
                if my_P75 > 10.0:
                    # convert by dividing by 1000
                    df[my_curve] = df[my_curve]/1000
                    
            case 'US/F' | 'US/FT' | 'USFT' | 'USF':
                my_P75 = df[my_curve].quantile(q=0.75)
                if my_P75 < 90.0:
                    # converst to microseconds per meter
                    df[my_curve] = df[my_curve]*3.281
            
    # Finalize in LAS
    las_dat.set_data(df)