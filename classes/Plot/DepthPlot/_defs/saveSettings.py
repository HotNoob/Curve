'''save_dpt -- props needs to be rewritten to use a json object settings format'''
import os
from tkinter import filedialog
from typing import TYPE_CHECKING

import global_vars

if TYPE_CHECKING:
    from .. import DepthPlot

def saveSettings(self : 'DepthPlot', Old_dir,c_idx, no_trcks, zone, crvs,prps):
    #save settings  tr_box  zn_box mycrvs and mprops
    #save default Dpt plot file also update lines
    lines=[]
    mpath=global_vars.project.inDir+'/databases/'
    my_file=filedialog.asksaveasfilename(
            initialdir = mpath,
            title="Please, enter or select filename",
            filetype=(("depth plot files", "*.dpt"), ("all files", "*.*"))
            )

    if my_file=='':                     #Do not save
        os.chdir(Old_dir)
        return
    if my_file[-4:]!='.dpt':
        my_file=my_file+'.dpt'
    with open(my_file,'w', encoding=global_vars.fileEncoding) as f:
        record=str(no_trcks) + '\n'
        f.write(record)
        lines.append(record)
        record=zone + '\n'
        f.write(record)
        lines.append(record)
        for c_row in range(c_idx):                          #save only curves filled in
            record=crvs[c_row]+'\n'
            f.write(record)
        record='END_CRVS\n'
        f.write(record)
        lines.append(record)

        for c_row in range(c_idx):                          #  write properties for each curve filled in
            record=prps[c_row][0]+ ','+prps[c_row][1]+ ',' + prps[c_row][2]+ ',' + prps[c_row][3]+ ',' + prps[c_row][4]+ ',' + prps[c_row][5]+ ','+ prps[c_row][6]+ ','+ prps[c_row][7]+ ','+ prps[c_row][8]+ ','+ prps[c_row][9]+ ','+ prps[c_row][10]+ ','+ prps[c_row][11]+ ','
            record=record+'\n'
            f.write(record)