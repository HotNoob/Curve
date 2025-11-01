from dataclasses import dataclass

@dataclass
class CurveParameter:
    curveName: str
    unit : str
    description: str
    scale : str