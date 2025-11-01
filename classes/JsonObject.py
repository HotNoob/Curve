import json
import typing

class JsonObject:
    ''' object to handle json encoding / decoding, allows for recursive encoding / decoding '''

    __init__hints = None
    def __init__(self) -> None:
        self.__class__.set_init_hints() #initialize type hints, for LoadFromDictionary

    @classmethod
    def set_init_hints(cls):
        if cls.__init__hints is None:
            cls.__init__hints = typing.get_type_hints(cls)

    def toJson(self) -> str:
        ''' converts object into a json string '''
        def prepare_for_json(object):
            if isinstance(object, set):
                return list(object)
            elif hasattr(object, '__dict__'):
                return object.__dict__
            else:
                raise TypeError(f"Object of type {object.__class__.__name__} is not JSON serializable")
            
        return json.dumps(self, default=prepare_for_json)
    
    @classmethod
    def LoadFromDictionary(cls, dictionary : dict):
        dictionary = dict((k.lower(), v) for k, v in dictionary.items()) #make all keys in dictionary lower case
        cls.set_init_hints()
        newObj = cls()
        
        for attribute in newObj.__dict__.keys(): #loop through all keys of well class, and apply values if found
            lowercase = attribute.lower()
            if lowercase in dictionary:
                if lowercase in newObj.__class__.__init__hints: #check if has type hint
                    typeHint = newObj.__class__.__init__hints[lowercase]
                    if typeHint == set: #if typehint is a set, convert from list to set
                        setattr(newObj, attribute, set(dictionary[lowercase]))
                    elif(
                            type(dictionary[lowercase]) is dict #input is dict
                            and len(typeHint.__args__) == 2 #number of args in type hint
                            and typeHint.__args__[0] == str #type hint 1 is str
                            and hasattr(typeHint.__args__[1], 'LoadFromDictionary') #check if has function loadfromdict
                        ):
                        d = getattr(newObj, attribute)
                        for key, val in dictionary[lowercase].items():
                            d[key] = typeHint.__args__[1].LoadFromDictionary(val)
                    else:
                        setattr(newObj, attribute, dictionary[lowercase])

                else:
                    setattr(newObj, attribute, dictionary[lowercase])

        return newObj