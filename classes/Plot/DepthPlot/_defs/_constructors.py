# pylint: disable=not-callable
import tkinter
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from .. import DepthPlot
    from classes.Project.WellList import WellList


@classmethod
def newDepthPlot(cls : Type['DepthPlot'], graphingWindow : tkinter.Toplevel, wellList : 'WellList' = None ) -> 'DepthPlot':
    '''creates a new depth plot, starting with the new settings menu'''
    newPlot = cls(graphingWindow, wellList)
    newPlot.newSettingsMenu()
    return newPlot