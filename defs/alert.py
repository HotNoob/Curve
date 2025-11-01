from tkinter import messagebox
import traceback
from enumerables import ErrorMessage
import global_vars

def Error(error : str | ErrorMessage, parameters : list | object | None = None) -> bool:
    '''
     Report an error, always returns False for convenience
     '''

    if isinstance(error, ErrorMessage):
        error = global_vars.languageTranslator.GetMessage(error, parameters)
    
    print("Error: " + error)
    print("--------------------")
    print(traceback.format_exc(limit=7))
    print("--------------------")
    traceback.print_stack(limit=10)
    print("--------------------")
    messagebox.showerror('Error Message', message=error)
    return False

def RaiseException(error : str | ErrorMessage, parameters : list | object | None = None):
    Error(error, parameters)
    
    raise Exception(error)

def Message(my_Txt : str):
    '''
     Show message
     '''
    messagebox.showinfo('Information', message=my_Txt)
