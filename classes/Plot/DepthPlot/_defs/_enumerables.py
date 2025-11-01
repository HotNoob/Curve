from enum import Enum


class DepthPlotType(Enum):
    DepthPlot = 'dpt'
    DepthShift = 'dptsft'
    MutlipleDepthPlot = 'mltdpt'
    def FromString(self, value : str) -> 'DepthPlotType':
        if(isinstance(value, DepthPlotType)): #check if is already PlotType
            return value

        match value:
            case str(self.DepthPlot):
                return self.DepthPlot
            case str(self.DepthShift):
                return self.DepthShift
            case str(self.MutlipleDepthPlot):
                return self.MutlipleDepthPlot