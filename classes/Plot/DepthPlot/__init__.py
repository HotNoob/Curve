import tkinter
from typing import TYPE_CHECKING

import global_vars
from classes.Plot import BasePlot

if TYPE_CHECKING:
    from classes.Project.WellList import WellList

from ._defs import _enumerables

Enumerables = _enumerables

class    DepthPlot(BasePlot):
    #alias' for easy access to enums
    Enumerables = _enumerables
    DepthPlotType = _enumerables.DepthPlotType

    def __init__(self, graphingWindow : tkinter.Toplevel = None,  wellList : 'WellList' = None):
        super().__init__()

        if wellList is None:
            self.wellList = global_vars.ui.Graphing.wellList
        else:
            self.wellList = wellList

        self.plotType : _enumerables.DepthPlotType = None #override base plot type
        self.graphingWindow : tkinter.Toplevel = graphingWindow
    
    #constructors
    from ._defs._constructors import newDepthPlot
    from ._defs.depthPlot import depthPlot
    from ._defs.getFills import getFills
    from ._defs.getTicks import getTicks
    from ._defs.loadSettings import loadSettings
    from ._defs.newSettingsMenu import newSettingsMenu
    from ._defs.saveSettings import saveSettings


