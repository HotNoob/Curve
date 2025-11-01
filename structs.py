from dataclasses import dataclass

from enumerables import Dir

@dataclass
class CurveSource:
    source : Dir
    name : str

@dataclass
class ZoneDepths:
    top : float
    base : float
    name : str

@dataclass
class FormationZone:
    Name : str
    TopFormation : str
    BaseFormation : str
    TopOffset : float
    BaseOffset : float
    Type : int


