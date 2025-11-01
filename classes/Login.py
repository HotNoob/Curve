import threading
import time
import sys
import random
import webview

from tkinter import *

import global_vars
import ctypes

from classes.APIClient import APIClient
from tkinter import Toplevel

import os


class Login:
    window : webview.Window
    apiClient : APIClient = None
    loggedIn : bool = True #skip login
    background_thread : threading.Thread = None

    def __init__(self):
        self.loggedIn = True
        return #skip login
        if self.is_debugging(): #if debugging, attempt to login via saved session.
            self.apiClient = APIClient()
            if self.apiClient.load_session():
                if self.check_session():
                    self.loggedIn = True
                    if global_vars.ui != None:
                        self.show_curve()

            if not self.loggedIn:
                self.login_window()
        else:
            self.login_window()

        self.background_thread = threading.Thread(target=self.check_session_worker)
        self.background_thread.daemon = True #background
        self.background_thread.start()

    def check_session(self) -> bool:
        return True
        
        result = self.apiClient.request('check_session')
        return result and (self.apiClient.username) and (result['user'] == self.apiClient.username)
    
    def check_session_worker(self):

        while self.loggedIn!=True:
            for i in range(0, 60*2): #sleep 60 seconds
                if not global_vars.running:
                    return
            
                time.sleep(0.5)

            if self.check_session():
                self.loggedIn = False


    def is_debugging(self):
        """Check if the script is running from VSCode with debugger attached."""
        vscode_env_vars = ["VSCODE_PID", "VSCODE_IPC_HOOK_CLI", "VSCODE_DEBUGGER"]
        debugging = any(var in os.environ for var in vscode_env_vars)
        if not debugging:
            return sys.gettrace() is not None
    
    def login_window(self):

        if global_vars.ui != None:
            self.hide_curve()

        self.window = webview.create_window('Curve 3.1 Loading', 'https://euky.ca/+curve/login', width=800, height=450, frameless=True, transparent=False, js_api=self)
        self.apiClient = APIClient()
 
        webview.start(self.stopLoading, self.window)

        while global_vars.running and not self.loggedIn:
            time.sleep(0.1)  # Sleep for a short time

            
    def version(self):
        return global_vars.SoftwareVersion

    def print(self, line):
        print(line)

    def hide_curve(self):
        global_vars.ui.Root.window.iconify()  # Hide the main window
        for win in  global_vars.ui.Root.window.winfo_children():
            if isinstance(win, Toplevel):
                win.iconify()  # Hide the Toplevel windows

    def show_curve(self):
         global_vars.ui.Root.window.deiconify()

    def login(self, username, password):

        if self.apiClient.login(username, password):
            result = self.apiClient.request('check_session')
            if not self.apiClient.username or result['user'] != self.apiClient.username:
                print("session failed")
                self.window.evaluate_js("login_failed();")
            else:
                self.window.evaluate_js("login_successful();")
                self.loggedIn = True
                if self.is_debugging(): #save session if debugging
                    self.apiClient.save_session()
        else:
            print('failed to login')
            self.window.evaluate_js("login_failed();")
        


    def resize(self):
        self.adjust_height(self.window)

    def close(self):
        print("closing")
        #work around to avoid error within webview
        threading.Timer(0.7, self.window.destroy).start()
        if not self.loggedIn:
            global_vars.running = False
            if global_vars.ui != None:
                global_vars.ui.Root.window.quit()
            sys.exit()
        elif global_vars.ui != None:
                self.show_curve()


    def get_dpi_scaling(self):
        user32 = ctypes.windll.user32
        
        # Get the DPI of the primary monitor
        dpi = user32.GetDpiForSystem()
        
        # Calculate the scaling factor (1.25 for 125% DPI scaling)
        scaling_factor = dpi / 96
        
        return scaling_factor

    def stopLoading(self, window : webview.Window):
        self.adjust_height(window)

    def adjust_height(self, window : webview.Window):
        # Execute JavaScript in the webview to get the height of the content
        content_height = window.evaluate_js("$(document).height()")
        content_height = content_height * self.get_dpi_scaling()
        content_height = int(content_height)
        
        # Set the height of the webview to match the content height
        window.resize(window.initial_width, content_height)
