class Script(object):
    def __init__(self):
        self.wells : list[str]
        self.VCL_Fn : str = None      #Final Vclay
        self.SW_Fn : str = None            #Final SW
        self.Phi_Fn : str = None          #Final Porosity
        self.Phie_Fn : str = None         #Final Effective Porosity
        self.K_Fn : str = None

    from ._defs.VClayGammaRay import VClayGammaRay
    from ._defs.VClayNeutronDensity import VClayNeutronDensity
    from ._defs.Porosity import Porosity
    from ._defs.WaterSaturation import WaterSaturation
    from ._defs.RITWaterSaturation import RITWaterSaturation
    from ._defs.Permeability import Permeability
    from ._defs.Facies import Facies
    from ._defs.selectFinalCurvePrompt import selectFinalCurve
    from ._defs._constructors import newVClayGammaRayScript
    from ._defs._constructors import newVClayNeutronDensityScript
    from ._defs._constructors import newPorosityScript
    from ._defs._constructors import newWaterSaturationScript
    from ._defs._constructors import newRITWaterSaturationScript
    from ._defs._constructors import newPermeabilityScript
    from ._defs._constructors import newFaciesScript