"""
###############################################################################
    
 Name: LogIT (Logger for Isis and Tuflow) 
 Author: Duncan Runnacles
 Copyright: (C) 2014 Duncan Runnacles
 email: duncan.runnacles@thomasmackay.co.uk
 License: GPL v2 - Available at: http://www.gnu.org/licenses/gpl-2.0.html

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


 Module:          ModelExtractor.py 
 Date:            04/03/2016
 Author:          Duncan Runnacles
 Since-Version:   0.4
 
 Summary:
    Copies the model at the path location stored in the log to a new directory.

 UPDATES:
    

 TODO:
    

###############################################################################
"""

import logging
logger = logging.getLogger(__name__)

from PyQt4 import QtCore, QtGui

from ship.utils.filetools import MyFileDialogs
    
import RunSummary_Widget as summarywidget
logger.debug('RunSummary_Widget import complete')
from app_metrics import utils as applog
import globalsettings as gs


class RunSummary_UI(QtGui.QWidget, summarywidget.Ui_RunSummaryWidget):
    

    def __init__(self, cwd, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QWidget.__init__(self, parent, f)
        
        self.tool_name = 'Run Summary'
        self.settings = ToolSettings()
        self.settings.cur_location = cwd
        
        self.setupUi(self)
        
        # Connect the slots
        
        
    def loadSettings(self, settings):
        """Load any pre-saved settings provided."""
        
        # Check that this version of the settings has all the necessary
        # attributes, and if not add the missing ones
        temp_set = ToolSettings()
        settings_attrs = [s for s in dir(temp_set) if not s.startswith('__')]
        for s in settings_attrs:
            if not hasattr(settings, s):
                setattr(settings, s, getattr(temp_set, s))
        
        self.settings = settings
    
    
    def saveSettings(self):
        """Return state of settings back to caller."""
        
        return self.settings
    

    def launchQtQBox(self, title, message):
        """Launch QtQMessageBox.
        """
        answer = QtGui.QMessageBox.question(self, title, message,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if answer == QtGui.QMessageBox.No:
            return False
        else:
            return answer


class ToolSettings(object):
    """Store the settings used by this class."""
    
    def __init__(self):
        
        self.tool_name = 'Run Summary'
        self.cur_display_path = ''
        


