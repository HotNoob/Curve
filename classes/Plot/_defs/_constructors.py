# pylint: disable=not-callable
#alternative constructors
#from common import *
import tkinter
from typing import TYPE_CHECKING, Type


if TYPE_CHECKING:
    from .. import Plot
    from classes.Project.WellList import WellList

@classmethod
def newSingleWellHistogram(cls : Type['Plot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'Plot':
    newPlot = cls(graphingWindow, wellList)
    newPlot.singleWellHistogramPlot()
    return newPlot

@classmethod
def newMultipleWellHistograms(cls : Type['Plot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'Plot':

    newPlot = cls(graphingWindow, wellList)
    newPlot.multipleWellHistograms()
    return newPlot

@classmethod
def newMultiWellHistogram(cls : Type['Plot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'Plot':

    newPlot = cls(graphingWindow, wellList)
    newPlot.multiWellHistogram()
    return newPlot

@classmethod
def newSingleWellCrossPlot(cls : Type['Plot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'Plot':

    newPlot = cls(graphingWindow, wellList)
    newPlot.singleWellCrossPlot()
    return newPlot

@classmethod
def newMultipleWellCrossPlot(cls : Type['Plot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'Plot':

    newPlot = cls(graphingWindow, wellList)
    newPlot.multipleWellCrossPlot()
    return newPlot

@classmethod
def newMultiWellCrossPlot(cls : Type['Plot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'Plot':

    newPlot = cls(graphingWindow, wellList)
    newPlot.multiWellCrossPlot()
    return newPlot

@classmethod
def newSingleWellZPlot(cls : Type['Plot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'Plot':

    newPlot = cls(graphingWindow, wellList)
    newPlot.singleWellZPlot()
    return newPlot

@classmethod
def newMultipleWellZPlots(cls : Type['Plot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'Plot':

    newPlot = cls(graphingWindow, wellList)
    newPlot.multipleWellZPlots()
    return newPlot

@classmethod
def newMultiWellZplot(cls : Type['Plot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'Plot':

    newPlot = cls(graphingWindow, wellList)
    newPlot.multiWellZplot()
    return newPlot

@classmethod
def newSingleWellThreeDPlot(cls : Type['Plot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'Plot':

    newPlot = cls(graphingWindow, wellList)
    newPlot.singleWellThreeDPlot()
    return newPlot

@classmethod
def newMultipleWellThreeDPlot(cls : Type['Plot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'Plot':

    newPlot = cls(graphingWindow, wellList)
    newPlot.multipleWellThreeDPlot()
    return newPlot

@classmethod
def newMultiWellThreeDPlot(cls : Type['Plot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'Plot':

    newPlot = cls(graphingWindow, wellList)
    newPlot.multiWellThreeDPlot()
    return newPlot

@classmethod
def newPickettPlot(cls : Type['Plot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'Plot':
    newPlot = cls(graphingWindow, wellList)
    newPlot.pickettPlot()
    return newPlot