import global_vars
import matplotlib.pyplot as plt  


class LineBuilder:
    def __init__(self, line, curvs, lines, my_ann, my_col, my_mark):
            
        self.line = line
        self.curvs = curvs
        self.lines = lines
        self.xs = list(line.get_xdata())
        self.ys = list(line.get_ydata())
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self)
        self.my_ann = my_ann
        self.my_col=my_col
        self.my_mark = my_mark
        self.tline=''


    def __call__(self, event):
        
        if event.dblclick:
            plt.close()
            return

        elif event.inaxes!=self.line.axes: return

        
        if self.tline!='':
            self.tline.remove()          #remove previous shifted CPOR
            self.tline=''
        if self.ys==[]:                    # ready for new shift
            self.ys.append(event.ydata)
            self.xs.append(event.xdata)

            mytxt='select second shift point in GR track'
            self.my_ann.set_text(mytxt)
            self.my_ann.figure.canvas.draw()
            return

        elif self.ys[-1]==0:                # reset list to first pick or select second point  Pressed escape?
            self.ys[0]=event.ydata
            self.xs[0]=event.xdata
            if global_vars.cr_shft:         #First reset to old depth
                idx=0
                for c in self.curvs:
                    #found core curves
                    if idx!=4:
                        self.lines[idx].set_data(c,c.index)
                    idx +=1
                self.xs = list()
                self.ys = list()
                mytxt='select first shift point in GR track./nTo Abort Double Klick'
                self.my_ann.set_text(mytxt)
                self.my_ann.figure.canvas.draw()
                del global_vars.cr_shft[-1]     # reset curve_shift
                return
            else:
                mytxt='select second shift point in GR track'
                self.my_ann.set_text(mytxt)
                self.my_ann.figure.canvas.draw()
                return 


        self.xs.append(event.xdata)
        self.ys.append(event.ydata)
        
        
        #shift core curves and display
        if len(self.ys)==2:     #ready to shift
            global_vars.tmp[0]=1
            global_vars.cr_shft.append(0)
            global_vars.cr_shft[0]=(self.ys[-1]-self.ys[-2])
            cshift=round(round(global_vars.cr_shft[-1]/0.1,0)*0.1,1)

            for c in self.curvs:
                #found core curves
                if c.name == 'MAVCL':  #['MAVCL', 'MAPHIT', 'CPOR', 'DHRO']:  
                    c_index=c.index+cshift
                    self.lines[1].set_ydata(c_index)
                elif c.name == 'MAPHIT':  #['MAVCL', 'MAPHIT', 'CPOR', 'DHRO']:
                    c_index=c.index+cshift
                    self.lines[3].set_ydata(c_index)

                elif c.name == 'CPOR':  #['MAVCL', 'MAPHIT', 'CPOR', 'DHRO']:
                    my_ax=self.lines[4].axes
                    #self.lines[4].remove()
                    #c.index=c.index+cshift
                    self.tline=my_ax.scatter(c, c.index+cshift)
                '''                    
                    y=c_index
                    self.lines[4].set_array(y)
                    self.lines[4].figure.canvas.draw()
                '''
   
            mytxt=f'Core shift: {cshift}m.\nTo change shift: left click on GR track \nWhen done press X'
            self.my_ann.set_text(mytxt) 
            #reset shift line
            self.xs.clear()
            self.xs.append(0)
            self.ys.clear()
            self.ys.append(0)
        self.line.set_data(self.xs, self.ys)
        self.line.figure.canvas.draw()
