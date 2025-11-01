#standardises curve names / alias' especially for programatic use
import os

import pandas as pd


class CurveNameTranslator:
    def __init__(self):
        self.data = None
        self.aliasFile = ''
        self.aliases : dict[str, list[str]] = {}
        self.aliasToName : dict[str, str] = {}
        #for now these will be in plot module, with the goal of moving to a curve name module



    def FindCurveAliasesInListByName(self, name : str, input : list[str]) -> bool:
        ''' if an alias of 'name' is in the input list, return True '''
        aliases = self.GetAliases(name)
        for curve in input:
            if curve in aliases:
                return True
        
        return False
            
    def GetCurveAliasesInListByName(self, name : str, input : list[str]) -> list[str]:
        ''' returns all alias of 'name' that are in the input list '''
        curves = []
        aliases = self.GetAliases(name)
        for curve in input:
            if curve in aliases:
                curves.append(curve)
        
        return curves
        

    def GetAliases(self, name : str) -> list[str]:
        ''' a lazy way to access results'''
        name = name.upper()

        if(name not in self.aliases):
            return []

        return self.aliases[name]

    def GetNames(self) -> list[str]:
        ''' returns all curve names (AKA) that have alias definitions, list is not a ref '''
        return list(self.aliases.keys())

    def GetName(self, alias : str) -> str:
        '''
            a lazy way to access results
            input alias is alias or name
        '''
        alias = alias.upper()

        if(alias not in self.aliasToName):
            return ''

        return self.aliasToName[alias]

    def Save(self, file : str = ''):
        if(file == ''):
            file = self.aliasFile

        df = pd.DataFrame(self.aliases.values())
        df.to_excel(file, header=None, index= False)

    def SaveLegacy(self, file : str = ''):
        if(file == ''):
            file = self.aliasFile + '.legacy.xlsx'

        legacy = []
        for k,v in self.aliases.items():
            legacy.append("1" + k)
            for alias in v :
                legacy.append("2" + alias)

        df = pd.DataFrame(legacy)
        df.to_excel(file, header=None, index= False)

    def LoadDefaultFile(self):
        return self.Load(os.path.dirname(os.path.realpath(__file__))+'/../'+'/config/CurveLogAliasFile.xlsx')

    # Load alias file and convert into a curve list for selection widgets
    def Load(self, file : str = ''):
        if(file != ''):
            self.aliasFile = os.path.abspath(file)

        self.aliases.clear()
        self.aliasToName.clear()
        aliasDf = pd.read_excel(self.aliasFile, header=None)

        if len(aliasDf.columns) < 5: #detect if file is in the old format
            a_column=aliasDf[aliasDf.columns[0]]
            alias_list=[]
            alias_arr=[]      #regular python array

            flag=0
            for ms in a_column:
                if '1' in ms[0]  :
                    if flag==0:       # if first list
                        alias_list.append(ms[1:])   # alias header column
                        flag=1
                    else:
                        #Reached end of list
                        alias_arr.append(alias_list)
                        alias_list=[]
                        alias_list.append(ms[1:])   # alias header column
                elif '2' in ms[0]  :
                    alias_list.append(ms[1:])  # add rows
            #add final list
            alias_arr.append(alias_list)

            #convert old list to dict
            for a in alias_arr:
                name = a[0]
                clean : list = list(set(a))
                clean.remove(name)
                clean.insert(0, name)
                self.aliases[name] = clean
        else: #load via new method
            rows = aliasDf.shape[0]
            for y in range(0,rows):
                row = aliasDf.loc[y, :].values.flatten().tolist()
                row = [item for item in row if not(pd.isnull(item)) == True] #remove nan / empty
                self.aliases[row[0]] = row

        for k,v in self.aliases.items():
            for alias in v:
                self.aliasToName[alias] = k