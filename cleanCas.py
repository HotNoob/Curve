import io
import global_vars
import re


def cleanCAS(filename : str):
    lines : list = []
    removeCharacters : bool = False
    with open(filename, 'r', encoding=global_vars.fileEncoding) as fileHandle:
        for line in fileHandle:
            if(str.startswith(line, '~ASCII ')):
                removeCharacters = True   #read file until ASCII section

            if removeCharacters:
                line = re.sub("[a-zA-Z]", " ", line)
            lines.append(line)
        
    with open(filename + '.clean.cas', 'w', encoding=global_vars.fileEncoding) as newFileHandle:
        newFileHandle.writelines(lines)
    
cleanCAS("S:/User/Desktop/eucalyptus/Visual Studio Workspaces/LAS IN/100140103817W400.cas")