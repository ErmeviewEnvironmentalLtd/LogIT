'''
###############################################################################
#    
# Name: LogIT (Logger for Isis and Tuflow) 
# Version: 0.4-Beta
# Author: Duncan Runnacles
# Copyright: (C) 2015 Duncan Runnacles
# email: duncan.runnacles@thomasmackay.co.uk
# License: GPL v2 - Available at: http://www.gnu.org/licenses/gpl-2.0.html
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#
# Module:  logit.py
# Date:  05/12/2015
# Author:  Duncan Runnacles
# Version:  1.0
# 
# Summary:
#    Convenience classes for use with the UI. Nothing kept here will be of
#    use to anything other than the GUI. It's a collection of classes for 
#    helping the GUI manage code bloat.
#
# UPDATES:
#   
#
# TODO:
#    
#
###############################################################################
'''

from PyQt4 import QtCore, QtGui

from tmac_tools_lib.utils.qtclasses import MyFileDialogs

import logging
logger = logging.getLogger(__name__)


class TableHolder(object):
    
    #VIEW_LOG = 0
    #NEW_LOG = 1

    def __init__(self, type=None):
        self.tables = {}
    
    
    def addTable(self, table_info_obj):
        self.tables[table_info_obj.key] = table_info_obj
    
    def _findTable(self, key=None, name=None):
        '''
        '''
        if not key == None or (key == None and name == None):
            return self.tables[key]
        else:
            for t in self.tables.values():
                if t.name == name: return t.key
    
    def getNameFromKey(self, key):
        return self.tables[key].name
    
    def getKeyName(self, name):
        return self._findTable(name=name)
    
    def getTable(self, key=None, name=None):
        key = self._findTable(key, name)
        return self.tables[key]


class TableWidget(object):
    
    # Columns that are editable by the user
    EDITING_ALLOWED = ['COMMENTS', 'MODELLER', 'SETUP', 'DESCRIPTION',
                        'EVENT_NAME', 'EVENT_DURATION', 'ISIS_BUILD',
                        'TUFLOW_BUILD', 'AMENDMENTS']
    
    def __init__(self, key, name, table_ref):
        self.key = key
        self.name = name
        self.ref = table_ref
        
    def removeRow(self, row=None, row_no=0):
        '''
        '''
        if not row == None:
            self.ref.removeRow(row)
        else:
            self.ref.removeRow(self.ref.rowAt(row_no))
    
    def currentRow(self):
        return self.ref.currentItem().row()
        
    
    def getValues(self, row_no=0, row=None, names=None):
        '''Get the item from the table where the header of the column in the
        table matches the given name.
        
        @param names: dictionary of names that are being looked for in the
               the table.
        @return: dictionary with the allowed items taken from the table.
        '''
        all_names = False
        if names == None:
            names = EDITING_ALLOWED
        elif names == '*':
            all_names = True
            
        keep_cells = {}
        if row == None:
            row = self.ref.rowAt(row_no)

        headercount = self.ref.columnCount()
        for x in range(0,headercount,1):
            
            headertext = str(self.ref.horizontalHeaderItem(x).text())
            if all_names:
                keep_cells[headertext] = str(self.ref.item(row, x).text())
            else:
                if headertext in names:
                    if not self.ref.item(row, x) == None:
                        keep_cells[headertext] = str(self.ref.item(row, x).text())
                    else:
                        keep_cells[headertext] = 'None'
                
        return keep_cells
        


    
            
        
    
def createQtTableItem(is_editable):
    '''Create a QTableWidgetItem and return
    @param is_editable=False: Set editable flag.
    @return: QTableWidgetItem
    '''
    item = QtGui.QTableWidgetItem(str(name))
    
    if is_editable:
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
    else:
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        
    return item

# class MessageBox(QtGui.QWidget):
#      def __init__(self, parent=None):
#          QtGui.QWidget.__init__(self, parent)
# 
#          self.setGeometry(300, 300, 250, 150)
#          self.setWindowTitle('message box')
# 
# 
#      def closeEvent(self, event):
#          reply = QtGui.QMessageBox.question(self, 'Message',
#              "Are you sure to quit?", QtGui.QMessageBox.Yes, 
#              QtGui.QMessageBox.No)
# 
#          if reply == QtGui.QMessageBox.Yes:
#              event.accept()
#          else:
#              event.ignore()

    
    