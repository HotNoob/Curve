''' adds json file saving and loading functions to a class'''
import json

def prepare_for_json(object):
    if isinstance(object, set):
        return list(object)
    elif hasattr(object, '__dict__'):
        return object.__dict__
    else:
        raise TypeError(f"Object of type {object.__class__.__name__} is not JSON serializable")


def toJson(self) -> str:
    return json.dumps(self, default=prepare_for_json)

    tmpDict : dict[str,str] = {}
    for key, value in self.__dict__.items():
        if(isinstance(value, dict)):
            value = json.dumps(value)
        elif isinstance(value, list):
            value = json.dumps(value)

        tmpDict[key] = value

        #invert_op = getattr(self, "invert_op", None)
        #if callable(invert_op):
    return json.dumps(tmpDict)

@classmethod
def LoadFromDictionary(cls, dictionary : dict ):
    new = cls() #may want to do this manually. for data validation?

    dictionary = dict((k.lower(), v) for k, v in dictionary.items()) #make all keys in dictionary lower case
    
    for attribute in new.__dict__.keys(): #loop through all keys of well class, and apply values if found
        lowercase = attribute.lower()
        if lowercase in dictionary:
            setattr(new, attribute, dictionary[lowercase])
    return new