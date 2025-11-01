
import copy

import global_vars


class Settings:
    def __init__(self, file : str = ''):
        ''' file is the file name, self.file holds the last file that was opened / saved, object is locked to filename'''
        self.settings = {}
        self.unsavedSettings : bool = False
        self.__file = file
    
    @property
    def empty(self) -> bool:
        return self.settings == {}
    
    def Get(self, name : str) -> str:
        ''' a lazy way to access settings without uppercase letters and worry'''
        name = name.upper()

        if(name not in self.settings):
            return ''

        return self.settings[name]

    def Copy(self) -> 'Settings':
        return copy.deepcopy(self)

    def Set(self, name : str, val : str) -> None:
        ''' a lazy way to set settings without uppercase letters'''

        name = name.upper()
        if name in self.settings:
            if self.settings[name] != val: #value changed
                self.unsavedSettings = True
        else: #new setting
            self.unsavedSettings = True

        self.settings[name] = val
        

    def Load(self, delimiter : str = " ") -> bool:
        print('load settings: ' + self.__file)
        self.settings = {} #clear current settings

        #load lines from file
        with open(self.__file, "r", encoding=global_vars.fileEncoding) as fileHandler:
            for line in fileHandler:
                lineParts =line.split(delimiter, 1)
                if(len(lineParts) == 2):
                    self.settings[lineParts[0].upper()] = lineParts[1].strip() #strip is trim

        if(delimiter == "," and len(self.settings) == 0): #if failed to load with "," delimiter, try with " " for max compatability
            return self.Load(' ')

        self.unsavedSettings = False
        return not (len(self.settings) == 0) #if empty, return false

    def Save(self, delimiter : str = ' '  ):
        '''current uses old file definition'''
        print('save settings: ' + self.__file)

        if(self.__file == ''):
            raise Exception('file name can not be empty, object is locked to filename to avoid problems')

        if(delimiter == ''):
            raise Exception('delimiter is empty')

        with open(self.__file,'w', encoding=global_vars.fileEncoding) as f:
            for name, value in self.settings.items():
                f.write(str(name) +delimiter+str(value) + '\n')

        self.unsavedSettings = False
        return True

    def  SaveAs(self, file : str, delimiter : str = ' '):
        ''' a new file created as well as a new object. as to keep one object to one file'''
        newSave = Settings(file)
        newSave.settings = self.settings.copy() #create a new copy, not just reference
        newSave.Save(delimiter)
        return newSave

    def LoadFromArray(self, settings : list) -> 'Settings':
        '''loads from old 2d array [[name, val]]'''
        for x in settings:
            self.Set(x[0], x[1])
        
        self.unsavedSettings = False
        return self        