'''getparm'''
import tkinter.ttk as ttk
from tkinter import (BOTH, END, LEFT, RIGHT, VERTICAL, Button, Canvas, E,
                     Entry, Frame, Label, Y)
from typing import TYPE_CHECKING

import defs.common as common
import defs.excel as excel
import global_vars

if TYPE_CHECKING:
    from ...MultiMineral import MultiMineral
# -------------------------------------------------------------------------------
def getParameter(self : 'MultiMineral', crv,extens):
    '''
    get a curve's multimineral parameter (CRV1 through 5)
    '''

    curnam=crv.name
    if '_NRM' in curnam:
        parnam=curnam[:-4]
    else :
        parnam = curnam

    match curnam:
        case 'RHOB':
            parnam = 'RHOM'
        case 'NPSS':        #convert crv to LS scale?
            parnam = 'NPHI'

    parnam = parnam + extens    # construct parameter name
    #look up in X_DF
    
    parval = self.parameters.loc[parnam,'VAL']
    return parval