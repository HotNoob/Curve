# pylint: disable=not-callable
#alternative constructors
#from common import *
import tkinter
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from .. import Script

@classmethod
def newVClayGammaRayScript(cls : Type['Script'] ) -> 'Script':
    newScript = cls()
    newScript.VClayGammaRay()
    return newScript

@classmethod
def newVClayNeutronDensityScript(cls : Type['Script'] ) -> 'Script':
    newScript = cls()
    newScript.VClayNeutronDensity()
    return newScript

@classmethod
def newPorosityScript(cls : Type['Script'] ) -> 'Script':
    newScript = cls()
    newScript.Porosity()
    return newScript

@classmethod
def newWaterSaturationScript(cls : Type['Script'] ) -> 'Script':
    newScript = cls()
    newScript.WaterSaturation()
    return newScript

@classmethod
def newRITWaterSaturationScript(cls : Type['Script'] ) -> 'Script':
    newScript = cls()
    newScript.RITWaterSaturation()
    return newScript

@classmethod
def newPermeabilityScript(cls : Type['Script'] ) -> 'Script':
    newScript = cls()
    newScript.Permeability()
    return newScript

@classmethod
def newFaciesScript(cls : Type['Script'] ) -> 'Script':
    newScript = cls()
    newScript.Facies()
    return newScript