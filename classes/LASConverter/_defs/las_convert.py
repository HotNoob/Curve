'''las_convert'''
import os
from tkinter import filedialog
import lasio
from defs import alert
from defs import prompt
import global_vars

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import LASConverter


def las_convert(self : 'LASConverter', files : list[str], TGRAD_Av, overwrite : bool = False):
    """ OPEN LAS FILE  AND SAVE NEW FILE
        skip resample depth if mstep not equal to 0.1 and startdepth NOT rounded to 0.1
    """

    filesLen = len(files)  #
    for index, filename in enumerate(files):
        # Report progress
        status = f"Converting File {index + 1} of {filesLen} : ({global_vars.project.IdentifyDir(filename)}) {os.path.basename(filename)} - "
        with self.__class__.workerLock: #thread safe, transfer to ui thread
            self.statusMessage = status + 'Loading LAS'


        # Open and read file with LASIO library as LS
        las_data = lasio.read(filename)
        # THE HARD WORK ==================================================
        # Update project database
        uwi = las_data.well.UWI.value

        newfile = global_vars.project.inDir + f"/{uwi}.las"
        if not overwrite and os.path.exists(newfile) and filesLen != 1: #if already exists, overwrite off, and not a single file, skip
            with self.__class__.workerLock: 
                self.statusMessage = status + ' Skip, Already Exists'
            continue

        with self.__class__.workerLock: #thread safe, transfer to ui thread
            self.statusMessage = status + 'PreConverting'

        # CHANGE THE LASS FILE
        mstep=las_data.well.STEP.value
        cstart=round(las_data.well.STRT.value,1)

        if mstep!=0.1 or cstart!=las_data.well.STRT.value:
            with self.__class__.workerLock:
                self.statusMessage = status + 'ReSampling'
            #resample.
            las_data= self.las_resample(las_data)
            #las_data= self.las_resample_optimize_test(las_data)
            
        # Convert ~Version SERV - default
        with self.__class__.workerLock:
            self.statusMessage = status + 'Las_SERV'
        self.convertService(las_data)

        if self.convertAll or self.convertDescriptions:
            with self.__class__.workerLock:
                self.statusMessage = status + 'Curve Descriptions'
            # Update curve descriptions
            self.las_crvdesc(las_data)

        if self.convertAll | self.convertNewCurves:
            with self.__class__.workerLock:
                self.statusMessage = status + 'New Curves'
        
            # Create new TEMP and BS-Bitsize curve
            self.Las_NewCrvs(las_data, TGRAD_Av)

        if self.convertAll | self.convertCurveUnits:
            with self.__class__.workerLock:
                self.statusMessage = status + 'Curve Units'
            # streamline curve data units
            self.las_units(las_data)
        '''
        # Update  ~ASCII with curve names STILL DOESN'T WORK
        las_data.ascii = 'A'
        for curve in las_data.curves:
            x = 6  # spaces between curve Mnem
            las_data.acii = las_data.ascii + " " * \
                (x-len(curve.mnemonic.strip(' ')))+curve.mnemonic.strip(' ')

        # finally save LAS Folder in Indir with concise file name
        #globals.rawDir
        #globals.inDir
        #globals.inFile
        '''

        newfile = global_vars.project.inDir + f"/{uwi}.las"

        if overwrite or not os.path.exists(newfile): #if file does not exist0
            '''
            Seems like lasio bugs out if STEP in original Newfile is not set to 0.1 
            prior to saving resampled curves?
            '''
            #las_data.well.STEP.value=0.1
            las_data.write(newfile, fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
            #global_vars.ui.Root.window.update_idletasks()
        elif filesLen == 1: #if only one file, prompt where to save file
            action = prompt.customButtonPrompt('File Already Exists in InDir', ['Overwrite', 'Save As', 'Discard'])
            if action == 'Save As':
                newFile = filedialog.asksaveasfilename(
                    initialdir=global_vars.project.inDir,
                    defaultextension="*.las",
                    confirmoverwrite=True,
                    filetypes=(("Log ASCII Standard File", "*.las"),(" text files", "*.txt")))
        
                if not newFile or not str(newFile).strip(): #empty file or cancel
                    action = 'Discard'
            
            if action != 'Discard': #write file
                las_data.write(newfile, fmt='%.2f', column_fmt={0:'%.4f'}, version=2.0)
                #global_vars.ui.Root.window.update_idletasks()
