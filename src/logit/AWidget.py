"""
###############################################################################
    
 Name: LogIT (Logger for Isis and Tuflow) 
 Author: Duncan Runnacles
 Copyright: (C) 2016 Duncan Runnacles
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


 Module:          AWidget.py 
 Date:            26/04/2016
 Author:          Duncan Runnacles
 Since-Version:   0.7
 
 Summary:
     Abstract class that provides an interface for all widgets used by LogIt.
     These will be called by the MainGui class at startup and added to the
     main QTabWidget.
     This class provides a range of convenience methods for launching 
     QMessagebox's, loading and saving data to the cache etc.
     There are also some methods such a load/save settings and loadto/savefrom
     cache that need to be implemented for the main gui to function properly.
     All widgets MUST implement this interface, but the settings and cache
     methods can be overridden is required.

 UPDATES:    

 TODO:
    

###############################################################################
"""

import logging
logger = logging.getLogger(__name__)

import uuid
import cPickle
import os

from PyQt4 import QtCore, QtGui

import ATool

class AWidget(QtGui.QWidget, ATool.ATool):
    
    def __init__(self, tool_name, cwd, parent=None, f=QtCore.Qt.WindowFlags(),
                 create_data_dir=True):
        ATool.ATool.__init__(self, tool_name, cwd, create_data_dir)
        QtGui.QWidget.__init__(self, parent, f)
        self._TEST_MODE = False # Used by some widgets in unittests
        
    
    def launchQMsgBox(self, title, message, type='warning'):
        """Launch a QMessageBox
        """
        if type == 'warning':
            QtGui.QMessageBox.warning(self, title, message)
        elif type == 'critical':
            QtGui.QMessageBox.critical(self, title, message)
        elif type == 'info':
            QtGui.QMessageBox.information(self, title, message)
            
            
    def launchQtQBox(self, title, message):
        """Launch QtQMessageBox.
        """
        answer = QtGui.QMessageBox.question(self, title, message,
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No) 
        if answer == QtGui.QMessageBox.No:
            return False
        else:
            return answer
    
    
    def launchQtQInput(self, title, message):
        """Launch a QtQInputDialog.
        
        Returns False if user cancels or the input text otherwise.
        """
        input, status = QtGui.QInputDialog.getText(self, title, message)
        if status:
            return input
        else:
            return False
    
    
    def _copyToClipboard(self, text_widget):
        """Copies the contents of a textbox to clipboard.
        Textbox to copy is based on the calling action name.
        """
        text = text_widget.toPlainText()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(text)
        event = QtCore.QEvent(QtCore.QEvent.Clipboard)
        QtGui.QApplication.sendEvent(clipboard, event)
    

    