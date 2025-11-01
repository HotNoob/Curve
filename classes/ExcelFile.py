import pandas as pd
import os
import defs.alert as alert

class ExcelFile:
    def __init__(self, file : str):
        self.file = os.path.abspath(file)
        self.dataFrame : pd.DataFrame  = None

    def Load(self) -> bool:
        self.dataFrame = pd.DataFrame(None) #create or clear df

        try:
            self.dataFrame = pd.read_excel(self.file)
        except FileNotFoundError:
            return alert.Error(f'{self.file} not found. Please, try again.')
        except ValueError:
            return alert.Error('File could not be opened. Please, try again')
        except PermissionError:
            return alert.Error('File already opened by another program. Please, try again')

        return True

    def Save(self, dataframe : pd.DataFrame = None, index : bool = False) -> bool:
        '''saves self.DataFrame, if dataframe is provided, overrides self.DataFrame with it'''
        if dataframe is not None:
            self.dataFrame = dataframe

        try:
            self.dataFrame.to_excel(self.file, index=index)
        except FileNotFoundError:
            return alert.Error('File could not be found. Please, try again.')
        except ValueError:
            return alert.Error('File could not be opened. Please, try again')
        except PermissionError:
            return alert.Error('File already opened by another program. Please, try again')

        return True

    def SaveAs(self, file : str, index : bool = False) -> bool:
        excelFile = ExcelFile(file)
        excelFile.dataFrame = self.dataFrame.copy()
        return excelFile.Save(index=index)

