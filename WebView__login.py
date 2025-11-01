import threading
import time
import sys
import random
import webview

from tkinter import *

import ctypes

def get_dpi_scaling():
    user32 = ctypes.windll.user32
    
    # Get the DPI of the primary monitor
    dpi = user32.GetDpiForSystem()
    
    # Calculate the scaling factor (1.25 for 125% DPI scaling)
    scaling_factor = dpi / 96
    
    return scaling_factor

class Api:
    def __init__(self):
        self.window : webview.Window = None

    def version(self):
        return "2.0.1"

    def print(self, line):
        print(line)

    def login(self, username, password):
        print(username)
        print(password)

        from classes.APIClient import APIClient

        apiClient : APIClient = APIClient()
        if apiClient.login(username, password):
            result = apiClient.request('check_session')
            print(result)
            self.window.evaluate_js("login_successful();")
        else:
            print('failed to login')
            self.window.evaluate_js("login_failed();")


    def resize(self):
        adjust_height(self.window)

    def close(self):
        print("closing")
        #work around to avoid error within webview
        threading.Timer(0.1, self.window.destroy).start()

def stopLoading(window : webview.Window):
    adjust_height(window)

def adjust_height(window : webview.Window):
    # Execute JavaScript in the webview to get the height of the content
    content_height = window.evaluate_js("$(document).height()")
    content_height = content_height * get_dpi_scaling()
    content_height = int(content_height)
    
    # Set the height of the webview to match the content height
    window.resize(window.initial_width, content_height)

if __name__ == '__main__':
    api = Api()
    api.window = webview.create_window('Curve 3.1 Loading', 'http://localhost:8080/curvewebserver/+curve/login', width=800, height=450, frameless=True, transparent=False, js_api=api)

    webview.start(stopLoading, api.window)