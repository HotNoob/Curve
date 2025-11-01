
from dataclasses import dataclass
from classes.JsonObject import JsonObject

@dataclass
class DepthPlotProperties(JsonObject):
    '''fill, crv, constant,GT/LT, Col,alp'''
    Color : str
    LineStyle : str
    Ticks : list[float]
    Scale : str
    Marker : str
    Track : int
    Fill : str
    Crv : str
    Constant : str
    GTLT : str
    FillColor: str
    FillColorAlpha : str


@dataclass
class DepthPlotSettings(JsonObject):
    tracks : int
    zone : str
    properties : list[DepthPlotProperties]
