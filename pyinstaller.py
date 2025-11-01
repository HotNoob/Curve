import subprocess
import glob

files : list[str] = [] 

for f in glob.glob('classes/**/*.pyd', recursive=True):
    files.append(" --add-binary=\""+f+";lib\" ")
    print(f)



subprocess.call("python --version & conda activate py10 & python --version & pyinstaller --noconfirm " 
                    + "--onefile --nowindow" 
                    + ' '.join(files) 
                    + "--exclude-module PyQt5 "
                    + "Curve.py"
                , shell=True)

#manually run this
#trouble running in conda? 
# pyinstaller --onefile --nowindow Curve.Spec
