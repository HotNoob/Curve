from typing import TYPE_CHECKING

from matplotlib import pyplot as pyplot
if TYPE_CHECKING:
    from .. import Plot

#draw a line on a cross plot
def drawLine(self : 'Plot',ax,fignum):
    xy=[]   
    #while len(xy)<2:
    xy = pyplot.ginput(2)
    x = [p[0] for p in xy]
    y = [p[1] for p in xy]

    if fignum in self.lines:
        self.lines[fignum][-1].remove()

    self.lines[fignum]=ax.plot(x,y,color='black')
    ax.figure.canvas.draw()
    return xy