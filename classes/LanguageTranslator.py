import json
import os
import re
from enumerables import ErrorMessage, MenuMessage

class LanguageTranslator:
    def __init__(self, file : str):
        self.__file = os.path.abspath(file)
        self.messages = dict[str, str]
        self.Load()

    def Load(self):
        with open(self.__file, "r", encoding='utf-8') as fileHandler:
            self.messages = json.loads(fileHandler.read())

    def GetMessage(self, name : ErrorMessage | MenuMessage | str, parameters : list[str] | dict[str,str] | object = None ):
        if isinstance(name, ErrorMessage | MenuMessage):
            name = name.value

        name = name.upper().strip()
        
        msg = self.messages[name]

        if parameters is None:
            return msg
        
        match parameters:
            case list():
                parameterLen = len(parameters)
                #obj array matches
                matches = set(re.findall('\{(\d\.\w+)\}', msg))
                for match in matches:
                    parts = match.split('.', 2)
                    if len(parts) == 2:
                        attribute = parts[1]
                        index = int(parts[0])
                         
                        if index < parameterLen:
                            match parameters[index]:
                                case dict():
                                    if attribute in parameters[index]:
                                        msg = msg.replace('{'+str(index)+'.'+str(attribute)+'}', str(parameters[index][attribute]))
                                case _:
                                    if hasattr(parameters[index], attribute):
                                        msg = msg.replace('{'+str(index)+'.'+str(attribute)+'}', str(getattr(parameters[index], attribute)))

                matches = set(re.findall('\{(\d)\}', msg))
                if len(matches) == 0: #if no matches, try converting words to numbers for list
                    count = 0
                    for attribute in list(set(re.findall('\{(\w+)\}', msg))):
                        msg = msg.replace('{'+str(attribute)+'}', '{'+str(count)+'}')
                        count += 1
                    if count == 0:
                        return msg
                
                    matches = set(re.findall('\{(\d)\}', msg))

                for index in matches:
                    index = int(index)
                    if index < parameterLen:
                        msg = msg.replace('{'+str(index)+'}', str(parameters[index]))

            case dict():
                #obj dict matches
                matches = set(re.findall('\{(\w+\.\w+)\}', msg))
                for match in matches:
                    parts = match.split('.', 2)
                    if len(parts) == 2:
                        attribute = parts[1]
                        index = str(parts[0])
                         
                        if index in parameters:
                            match parameters[index]:
                                case dict():
                                    if attribute in parameters[index]:
                                        msg = msg.replace('{'+str(index)+'.'+str(attribute)+'}', str(parameters[index][attribute]))
                                case _:
                                    if hasattr(parameters[index], attribute):
                                        msg = msg.replace('{'+str(index)+'.'+str(attribute)+'}', str(getattr(parameters[index], attribute)))

                for attribute in set(re.findall('\{(\w+)\}', msg)):
                    if attribute in parameters:
                        msg = msg.replace('{'+str(attribute)+'}', str(parameters[attribute]))

            case _:
                #remove dict and list patterns because input is an object
                msg = re.sub('(\{)(\w+|\d)\.(\w+\})', '\\1\\3', msg)

                for attribute in set(re.findall('\{(\w+)\}', msg)):
                    if hasattr(parameters, attribute):
                        msg = msg.replace('{'+str(attribute)+'}', str(getattr(parameters, attribute)))


        return msg