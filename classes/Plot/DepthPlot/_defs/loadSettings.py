#pylint: disable=no-name-in-module
'''get_plt -- props needs to be rewritten to use a json object settings format'''
import os
from tkinter import filedialog
from typing import TYPE_CHECKING

from . import _enumerables

import defs.alert as alert
import global_vars

if TYPE_CHECKING:
    from .. import DepthPlot


#------------------------------------------------------------------------------------------------
def loadSettings(self : 'DepthPlot', plt_type : _enumerables.DepthPlotType):
    '''
    select and open plot file get settings and update plt_stgs
    '''
    curdir=os.getcwd()
    mpath=global_vars.project.inDir+'/databases/'
    message=f"{plt_type.value} files"
    try:
        Infile = filedialog.askopenfilename(
            #initialdir = inDir,
            title="Please, select an input file",
            filetype=((message, "*."+plt_type.value), ("all files", "*.*"))
        )
        with open(Infile, "r", encoding=global_vars.fileEncoding) as f:
            lines = f.readlines()
    except FileNotFoundError:
        alert.Error('File could not be found. Please, try again.')
    except ValueError:
        alert.Error('File could not be opened. Please, try again')
    if Infile=='':
        os.chdir(curdir)
        return

    if plt_type== _enumerables.DepthPlotType.DepthPlot:
        os.chdir(curdir)
        return lines

    plt_set= []

    for l in lines:
        a=l.split(" ")
        a[1]=a[1].replace('\n',"")
        plt_set.append(a)

    #check for missing curves
    '''
    miss_crvs(plt_set)
        if Well_List==[] or len(plt_set)<2: #If Well_list np.empty or no plot settings
        plt_set=''
    '''
    os.chdir(curdir)
    return plt_set