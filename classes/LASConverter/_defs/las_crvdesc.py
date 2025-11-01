'''Las_CRVdescr'''
import global_vars

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import LASConverter

def las_crvdesc(self : 'LASConverter', las_dat):
    """ Update missing descriptions"""

    # Get LAS curve and description
    for curve in las_dat.curves:
        if curve.mnemonic in global_vars.project.curveParameters:
            description = str(curve.descr).strip()
            if len(description) < 2:
                curve.descr = description[0:2]+' ' + global_vars.project.curveParameters[curve.mnemonic].description