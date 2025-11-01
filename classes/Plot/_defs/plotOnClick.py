from typing import TYPE_CHECKING

import matplotlib.pyplot as pyplot

import global_vars

if TYPE_CHECKING:
    from .. import Plot


def plotOnClick(self : 'Plot', e):
    '''
    On mouse click close all graphs
    '''
    if e.button==1:                  #'<MouseButton.LEFT: 1>'
        return
    
    pyplot.close('all')