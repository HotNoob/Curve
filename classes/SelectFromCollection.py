import warnings

import numpy as np
from matplotlib.path import Path
from matplotlib.widgets import PolygonSelector

import defs.alert as alert


class SelectFromCollection:
    """
    Select indices from a matplotlib collection using `PolygonSelector`.

    Selected indices are saved in the `ind` attribute. This tool fades out the
    points that are not part of the selection (i.e., reduces their alpha
    values). If your collection has alpha < 1, this tool will permanently
    alter the alpha values.

    Note that this tool selects collection objects based on their *origins*
    (i.e., `offsets`).

    Parameters
    ----------
    ax : `~matplotlib.axes.Axes`
        Axes to interact with.
    collection : `matplotlib.collections.Collection` subclass
        Collection you want to select from.
    alpha_other : 0 <= float <= 1
        To highlight a selection, this tool sets all selected points to an
        alpha value of 1 and non-selected points to *alpha_other*.
    """
    # ax=ax array, collection = data points, t_line is trendline,
    # dpt_line is empty dataline on dpt plot ax[1], tl_deg is order of trendanalysis,
    # my_ann = annotations
    def __init__(self, ax, collection, t_line, c1, dpt_line ,tl_deg, my_ann, mcol, alpha_other=0.3):
        self.ax = ax
        self.canvas = ax[0].figure.canvas
        if len(ax)>1:       #if not a multiwell plot
            self.canvas1 = ax[1].figure.canvas
        else:
            self.canvas1 = ax[0].figure.canvas #not to be used. Just a placeholder
        self.collection = collection
        self.alpha_other = alpha_other
        self.lbl = ax[0].get_xlabel()
        self.t_line = t_line
        self.c1 = c1
        self.dpt_line = dpt_line
        self.tl_deg = tl_deg
        self.my_ann = my_ann
        self.mcol = mcol                #reset col for selected data points

        self.xys = collection.get_offsets()
        self.Npts = len(self.xys)

        # Ensure that we have separate colors for each object
        self.fc = collection.get_facecolors()
        if len(self.fc) == 0:
            raise ValueError('Collection must have a facecolor')
        elif len(self.fc) == 1:
            self.fc = np.tile(self.fc, (self.Npts, 1))

        self.poly = PolygonSelector(ax[0], self.onselect)
        self.ind = []

    def onselect(self, verts):

        path = Path(verts)
        self.ind = np.nonzero(path.contains_points(self.xys))[0]
        self.fc[:, -1] = self.alpha_other
        self.fc[self.ind, -1] = 1

        #if trendline selected
        if self.tl_deg:
            #update trendline
            #convert list of tupples into two data lists
            v=[]
            w=[]
            for dat in self.xys[self.ind]:
                v.append(dat[0])
                w.append(dat[1])

            x=np.array(v)
            y=np.array(w)

            #obtain m (slope) and b(intercept) of linear regression line
            with warnings.catch_warnings():
                warnings.filterwarnings('error')
                try:
                    if self.tl_deg==1 and x.any():
                        #linear regression
                        slop, interc = np.polyfit(x, y, self.tl_deg)
                        x1=np.min(x)
                        x2=np.max(x)
                        y1=slop*x1+interc
                        y2=slop*x2+interc
                        self.t_line.set_data([x1,x2],[y1,y2])
                        slope=round(slop,3)
                        intercept=round(interc,3)
                        mytxt=f"{self.lbl}x{slope:.3f} + {intercept:.2f}"
                    elif self.tl_deg==2 and x.any():              #Squared regression
                        p = np.polyfit(x, y, self.tl_deg)
                        predict = np.poly1d(p)
                        myx=[]
                        myy=[]
                        myx.append(np.min(x))
                        myy.append(np.max(x))
                        mystep=(myy[0]-myx[0])/10
                        myy[0]=predict(myx[0])
                        for id in range(1,11):
                            myx.append(myx[id-1]+mystep)
                            myy.append(predict(myx[id]))
                        self.t_line.set_data(myx,myy)
                        #y=ax**2+bx+c
                        mytxt=f"{p[0]:.1f}x{self.lbl}^2 + {p[1]:.1f}x{self.lbl} + {p[2]:.1f}"
                    elif self.tl_deg==3 and x.any():              #Cubic regression
                        p = np.polyfit(x, y, self.tl_deg)
                        predict = np.poly1d(p)
                        myx=[]
                        myy=[]
                        myx.append(np.min(x))
                        myy.append(np.max(x))
                        mystep=(myy[0]-myx[0])/10
                        myy[0]=predict(myx[0])
                        for id in range(1,11):
                            myx.append(myx[id-1]+mystep)
                            myy.append(predict(myx[id]))
                            self.t_line.set_data(myx,myy)
                        #y=ax**3+bx**2+cx+d
                        mytxt=f"{p[0]:.1f}x{self.lbl}^3 + {p[1]:.1f}x{self.lbl}^2 + {p[2]:.1f}x{self.lbl}+{p[2]:.1f}"

                    self.my_ann.set_text(mytxt)

                except np.RankWarning:
                    alert.Error("lower polyfit degree")
                except Exception:
                    alert.Error("polyfit problem - try lower degree")

            self.collection.set_facecolors(self.fc)
            self.canvas.draw_idle()
        if len(self.ax)!=1:       #if not a multiwell plot
            old_col = self.dpt_line.get_color() #reset to original line or market color
            self.dpt_line.set_color(self.mcol)
            # Update depth plot for selected points
            self.c1['HI']=self.c1.iloc[self.ind][self.lbl]
            self.dpt_line.set_data(self.c1['HI'],self.c1.index)
            self.dpt_line.set_color(old_col)
            self.canvas1.draw_idle()
        self.canvas.draw_idle()

    def disconnect(self):
        self.poly.disconnect_events()
        self.fc[:, -1] = 1
        self.collection.set_facecolors(self.fc)

    '''
    def connect(self):
        plt.figure(fignum)              #set to active figure
        self.poly.set_active=True
        self.fc[:, -1] = 1
        self.collection.set_facecolors(self.fc)
    '''
