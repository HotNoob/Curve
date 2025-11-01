import threading
import time
import sys
import random
import webview

from tkinter import *

class Api:
    def __init__(self):
        self.window : webview.Window = None

    def version(self):
        return "2.0.1"

    def print(self, line):
        print(line)

def stopLoading(window : webview.Window):
    time.sleep(3)
    window.evaluate_js('window.fadeout(1777);')
    time.sleep(5)
    window.destroy()
    

if __name__ == '__main__':
    api = Api()
    api.window = webview.create_window('Curve 3.1 Loading', 'http://localhost:8080/curvewebserver/+curve/loading', width=400, height=400, frameless=True, transparent=True, js_api=api)
    
    webview.start(stopLoading, api.window)