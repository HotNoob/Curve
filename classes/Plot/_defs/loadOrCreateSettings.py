from typing import TYPE_CHECKING

import global_vars
import defs.prompt as prompt

if TYPE_CHECKING:
    from .. import Plot


def loadOrCreateSettings(self : 'Plot'):
    ''' prompts for default settings, if declined, opens new settings menu '''
    #Ask for default settings
    if not prompt.yesno('Use Default Plot Settings?'):
        # determine depth or stratigraphic interval
        if not self.newDepthSettingsMenu():
            self.graphingWindow.deiconify()
            return

        #create new plot settings
        self.newSettingsMenu()
    else:
        self.LoadDefaultSettings()
    
    self.findMissingCurves()

