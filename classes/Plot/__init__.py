# pylint: disable = import-outside-toplevel
import tkinter
from typing import TYPE_CHECKING

import cython
import pandas as pd

import global_vars
from classes.Settings import Settings
from structs import ZoneDepths

if TYPE_CHECKING:
    import matplotlib.axes
    import matplotlib.collections
    import matplotlib.figure
    import matplotlib.text
    from matplotlib.widgets import RectangleSelector

    from classes.Project.WellList import WellList
    from classes.SelectFromCollection import SelectFromCollection


class BasePlot(object):
    def __init__(self):
        self.plotType = None
        self.settings : Settings = None
        self.figures : list[matplotlib.figure.Figure] = []
        self.axes : list[matplotlib.axes.Axes] = []

        self.wellList : 'WellList' = None

        if cython.compiled:
            print("Yep, I'm compiled.")
        else:
            print("Just a lowly interpreted script...")

    #event handlers
    from ._defs.pickettPlotOnClick import pickettPlotOnClick
    from ._defs.plotOnBaseKey import plotOnBaseKey
    from ._defs.plotOnClick import plotOnClick
    from ._defs.plotOnKey import plotOnKey

class Plot(BasePlot):
    def __init__(self, graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None):

        self.rect_selectors : dict[int, RectangleSelector] = {}
        ''' index is int, which is the figure number -  #dict of rectangle selectors '''

        self.selectors : dict[int, SelectFromCollection] = {}
        ''' index is int, which is the figure number - #dict of polygon selectors '''

        self.points : dict[int, matplotlib.collections.PathCollection] = {}
        ''' index is int, which is the figure number '''
        
        self.lines : dict[int, object] = {}
        ''' index is int, which is the figure number '''

        self.annotations : dict[int, matplotlib.text.Annotation] = {}
        ''' index is int, which is the figure number '''


        self.resetDataFrames : dict[int, list[pd.DataFrame]] = {}
        ''' index is int, which is the figure number '''

        self.mlti_f : bool = False
        ''' toggle for plotOnKey'''

        self.graphingWindow : tkinter.Toplevel = graphingWindow
        self.zoneDepths : ZoneDepths = None

        super().__init__()
        if wellList is None:
            self.wellList = global_vars.ui.Graphing.wellList
        else:
            self.wellList = wellList

    # Imported methods
    # static methods need to be set
    #from ._staticMethodExample import StaticMethodExample
    #StaticMethodExample = staticmethod(StaticMethodExample)
    from ._defs._constructors import (newMultipleWellCrossPlot,
                                      newMultipleWellHistograms,
                                      newMultipleWellThreeDPlot,
                                      newMultipleWellZPlots,
                                      newMultiWellCrossPlot,
                                      newMultiWellHistogram,
                                      newMultiWellThreeDPlot,
                                      newMultiWellZplot, 
                                      newPickettPlot,
                                      newSingleWellCrossPlot,
                                      newSingleWellHistogram,
                                      newSingleWellThreeDPlot,
                                      newSingleWellZPlot)
    from ._defs.discrim_curv import discrim_crv
    from ._defs.drawLine import drawLine
    from ._defs.findMissingCurves import findMissingCurves
    from ._defs.get_discriminator import get_discriminator
    from ._defs.loadOrCreateSettings import loadOrCreateSettings
    from ._defs.mlt_well_df import mlt_well_df
    from ._defs.mtp_well_df import mtp_well_df
    from ._defs.multipleWellCrossPlot import multipleWellCrossPlot
    from ._defs.multipleWellHistograms import multipleWellHistograms
    from ._defs.multipleWellThreeDPlot import multipleWellThreeDPlot
    from ._defs.multipleWellZPlots import multipleWellZPlots
    from ._defs.multiWellCrossPlot import multiWellCrossPlot
    from ._defs.multiWellHistogram import multiWellHistogram
    from ._defs.multiWellThreeDPlot import multiWellThreeDPlot
    from ._defs.multiWellZplot import multiWellZplot
    from ._defs.newDepthSettingsMenu import newDepthSettingsMenu
    from ._defs.newSettingsMenu import newSettingsMenu
    from ._defs.pickettPlot import pickettPlot
    from ._defs.plotScales import plotScales
    from ._defs.singleWellCrossPlot import singleWellCrossPlot
    from ._defs.singleWellHistogram import singleWellHistogramPlot
    from ._defs.singleWellThreeDPlot import singleWellThreeDPlot
    from ._defs.singleWellZPlot import singleWellZPlot

    def LoadDefaultSettings(self : 'Plot'):
        self.LoadSettings(global_vars.project.inDir+'/databases/default.'+ self.plotType.value)

    def LoadSettings(self : 'Plot', file : str):
        self.settings = Settings(file)
        self.settings.Load()
        #todo, validate settings. see def find_missing_curves(plt_settings):

    def SaveDefaultSettings(self):
        self.settings.SaveAs(global_vars.project.inDir+'/databases/default.'+ self.plotType.value)
