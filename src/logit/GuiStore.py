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
    '''Container class for a collection of QTableWidget objects.
    '''
    
    # Collection key
    VIEW_LOG = 0
    NEW_LOG = 1

    def __init__(self, type):
        self.tables = {}
        self.type = type
    
    
    def addTable(self, table_info_obj):
        '''Add a new table to the collection.
        '''
        self.tables[table_info_obj.key] = table_info_obj
    
    
    def _findTable(self, key=None, name=None):
        '''Find table key based on given parameter.
        Locates the correct table whether given the key to the table or the
        name of the QTableWidget object.
        @return key to table.
        '''
        if not key == None or (key == None and name == None):
            return key
        else:
            for t in self.tables.values():
                if t.name == name: return t.key
    
    
    def getNameFromKey(self, key):
        '''Return the table name when given the key.
        '''
        return self.tables[key].name
    
    
    def getKeyFromName(self, name):
        '''Return the table key when given the name.
        '''
        return self._findTable(name=name)
    
    
    def getTable(self, key=None, name=None):
        '''Return table referenced by either the key or the name.
        '''
        key = self._findTable(key, name)
        return self.tables[key]
    
    
    def clearAll(self):
        '''Clears the row data and completely resets the table.
        '''
        if self.type == TableHolder.NEW_LOG:         
            for table in self.tables.values():
                table.ref.clearContents()
                table.ref.setRowCount(1)
                
        elif self.type == TableHolder.VIEW_LOG:
            for table in self.tables.values():
                table.ref.setRowCount(0)


class TableWidget(object):
    '''Conveniance class for accessing regularly used attributes of the 
    QTableWidget object in the GUI.
    '''
    
    # Columns that are editable by the user
    EDITING_ALLOWED = ['COMMENTS', 'MODELLER', 'SETUP', 'DESCRIPTION',
                        'EVENT_NAME', 'EVENT_DURATION', 'ISIS_BUILD',
                        'TUFLOW_BUILD', 'AMENDMENTS']
    
    def __init__(self, key, name, table_ref):
        self.key = key
        self.name = name
        self.ref = table_ref
        
        
    def removeRow(self, row=None, row_no=0):
        '''Removes the row denoted by paramaters.
        
        If no arguments are given it will do nothing.
        @param row=None: The row object to delete.
        @param row_no=None: The index of the row to delete.
        
        '''
        if not row == None:
            self.ref.removeRow(row)
        else:
            self.ref.removeRow(self.ref.rowAt(row_no))
    
    
    def currentRow(self):
        '''Returns the currently selected row.
        '''
        return self.ref.currentItem().row()
        
    
    def getAllRows(self):
        '''Get a list containing dictionaries of all rows in this table.
        '''
        row_count = self.ref.rowCount()
        all_rows = []
        for i in range(1, row_count):
            all_rows.append(self.getValues(i, names='*')) 
        return all_rows


    def getValues(self, row_no=0, row=None, names=None):
        '''Get the item from the table where the header of the column in the
        table matches the given name.
        
        @param names: dictionary of names that are being looked for in the
               the table.
        @return: dictionary with the allowed items taken from the table.
        '''
        all_names = False
        if names == None:
            names = TableWidget.EDITING_ALLOWED
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
    
    
    def addRows(self, row_data, start_row):
        '''Adds the given rows to the table.
        
        @param row_data: list of row dictionaries containing the data for the
               table.
        @param start_row: the first row in the table to start entering data.
        '''
        for row in row_data:
            self.addRowValues(row, start_row)
            start_row += 1
            
    
    def addRowValues(self, row_dict, row_no=0):
        '''Put values in the given dictionary into the given table where the
        dictionary keys match the column headers of the table.
        
        @param row_dict: dictionary containing the values to put in the table.
        @param row_no=0: the row to add the values at.
        '''
        # Insert a new row first if needed
        row_count = self.ref.rowCount()
        if not row_count > row_no:
            self.ref.insertRow(row_count)
        
        row = self.ref.rowAt(row_no)
        headercount = self.ref.columnCount()
        for x in range(0,headercount,1):
            headertext = str(self.ref.horizontalHeaderItem(x).text())
            if headertext in row_dict:
                
                # If it's a loaded variable or db ID then we need to stop 
                # user for corrupting the data and/or database
                if not headertext in TableWidget.EDITING_ALLOWED:
                    self.ref.setItem(row_no, x, createQtTableItem(
                                        str(row_dict[headertext]), False))
                else:
                    self.ref.setItem(row_no, x, createQtTableItem(
                                        str(row_dict[headertext]), True))
    
    
    def setEditColors(self, row_no, is_editable=True):
        '''Sets the colour of the cells in a row according to whether the cell
        is editable or not.
        Cells that can be edited will be set to green.
        Cells that can't be edited will be set to red.
        If a model file has already been entered into the database the entire
        row will be set to red.
        
        @param row_no: the index of the row to change editing settings on.
        @param is_editable=True: Sets whether the entire row should be set to
               non-editable or not.
        '''
        if is_editable:
            my_color = QtGui.QColor(204, 255, 153) # Light green
        else:
            my_color = QtGui.QColor(255, 204, 204) # Light Red
        
        cols = self.ref.columnCount()
        for c in range(0, cols):
            if is_editable:
                # Only highlight it green if it's an editable entry
                headertext = str(self.ref.horizontalHeaderItem(c).text())
                if headertext in TableWidget.EDITING_ALLOWED:
                    self.ref.item(row_no, c).setBackground(my_color)
            else:
                self.ref.item(row_no, c).setBackground(my_color)

        
    
def createQtTableItem(name, is_editable):
    '''Create a QTableWidgetItem and return
    @param name: value to put into the item text.
    @param is_editable=False: Set editable flag.
    @return: QTableWidgetItem
    '''
    item = QtGui.QTableWidgetItem(str(name))
    
    if is_editable:
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
    else:
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        
    return item


def getModelFileLocation(multi_paths, last_model_directory,
                                        cur_log_path, cur_settings_path):
    '''Launch dialog for user to choose model to load.
    @param param: 
    '''
    # Create a file dialog with an initial path based on the availability
    # of path variables.
    d = MyFileDialogs()
    if not last_model_directory == '' and \
                    not last_model_directory == False:
        chosen_path = last_model_directory
    elif not cur_log_path == ''  and not self.settings.cur_log_path == False:
        chosen_path = cur_log_path
    else:
        chosen_path = cur_settings_path
          
    if multi_paths:
        open_path = d.openFileDialog(path=chosen_path, 
                file_types='ISIS/TUFLOW (*.ief *.IEF *.tcf *.TCF)',
                multi_file=True)
    else:
        open_path = d.openFileDialog(path=chosen_path, 
                file_types='ISIS/TUFLOW (*.ief *.IEF *.tcf *.TCF)')
    
    return open_path


class ErrorHolder(object):
    '''Container for errors logged for later use.
    '''
    
    def __init__(self):
        self.reset()
        
    
    def addError(self, key, msg_add='', change_status=False,
                                                msgbox_error=False):
        '''Adds a new error to the log list.
        @param key: the key to the error. If this doesn't exist it will raise a 
               KeyError. If you want to create a new type of error either add 
               it to the _initErrorTypes function or call addErrorType with an 
               ErrorType object if you only want it at run time.
        @param message_additional='': Any additional text to add to the error.
        @param change_status=False: If set to True the message_additional text
               will be added to the status text as well.
        '''
        if not key in self.types:
            raise KeyError
        title = self.types[key].title+''
        msg = self.types[key].message + msg_add
        status_bar = msg
        if change_status:
            status_bar = self.types[key].status_bar + msg_add
        error = ErrorType(title, status_bar, msg)
        error.error_found = True
        self.log.append(error)
        self.has_errors = True
        self.has_local_errors = True
        if msgbox_error:
            self.msgbox_error = error
    
    
    def formatErrors(self, prologue=''):
        '''Return the message from the error logs formatted as text.
        Takes the message from each of the ErrorType objects stored in the
        self.log and combines them into a single formatted text string.
        @param prologue: string containing any text that should be prepended
               to the output text.
        @return: string of formatted log messages.
        '''
        if len(self.log) < 1:
            return ''
        else:
            out_err = []
            for l in self.log:
                out_err.append(l.message)
            out_err = '\n\n'.join(out_err)
            return out_err
        
    
    def addErrorType(self, error_type, key):
        '''Adds a new ErrorType to the self.types dictionary.
        @param error_type: The ErrorType object to add.
        @param key: the key to use to access the error_type.
        '''
        self.types[key] = error_type
        
    
    def reset(self):
        self.log = []
        self.msgbox_error = None
        self.types = self._initErrorTypes()
        self.has_errors = False
        self.has_local_errors = False
    
    
    def _initErrorTypes(self):
        '''Initialise all of the available error types.
        '''
        errors = {}
        self.DB_UPDATE = 'Database Update Error'
        self.DB_EDIT = 'Database Edit Error'
        self.DB_OLD = 'Database Old Error'
        self.DB_NEW = 'Database New Error'
        self.DB_ACCESS = 'Database Access Error'
        self.DB_SCHEMA = 'Database Schema Error'
        self.MODEL_LOAD = 'Model Load Error'
        self.RESULTS_EXIST = 'Results Already Exist Error'
        self.LOG_EXISTS = 'Log Entry Exists Error'
        self.IO_ERROR = 'IO Error'
        self.SETTINGS_LOAD = 'Load Settings Error' 
        self.EXPORT_EXCEL = 'Export to Excel Error'
            
        #
        title = self.DB_UPDATE
        status_bar = 'Unable to update Database with model '
        message = status_bar
        errors[title] = ErrorType(title, status_bar, message)
        
        #
        title = self.DB_EDIT
        status_bar = 'Unable to edit log database'
        message = status_bar
        errors[title] = ErrorType(title, status_bar, message)

        #
        title = self.DB_OLD
        status_bar = 'Unable to load database '
        message = ('Database needs updating to latest version.'
                   '\nUse Settings > Tools > Update Database Schema. '
                   'See Help for details.')
        errors[title] = ErrorType(title, status_bar, message)
        
        #
        title = self.DB_NEW
        status_bar = 'Unable to load database '
        message = ('Database was produced with newer version of LogIT.\n'
                   'Update to latest version of LogIT to use database.')
        errors[title] = ErrorType(title, status_bar, message)
        
        #
        title = self.DB_ACCESS
        status_bar = 'Unable to access database '
        message = status_bar
        errors[title] = ErrorType(title, status_bar, message)
        
         #
        title = self.MODEL_LOAD
        status_bar = 'Unable to load model log from file '
        message = status_bar
        errors[title] = ErrorType(title, status_bar, message)
        
        #
        title = self.RESULTS_EXIST
        status_bar = 'ISIS/FMP results file already exist '
        message = status_bar
        errors[title] = ErrorType(title, status_bar, message)
        
        #
        title = self.LOG_EXISTS
        status_bar = 'Selected file already exists in database '
        message = status_bar
        errors[title] = ErrorType(title, status_bar, message)
        
        #
        title = self.IO_ERROR
        status_bar = 'Unable to access file '
        message = status_bar
        errors[title] = ErrorType(title, status_bar, message)
        
        #
        title = self.DB_SCHEMA
        status_bar = 'Failed to update database schema: See log for details '
        message = status_bar
        errors[title] = ErrorType(title, status_bar, message)
        
        #
        title = self.SETTINGS_LOAD
        status_bar = 'Unable to load user settings '
        message = status_bar
        errors[title] = ErrorType(title, status_bar, message)
        
        #
        title = self.EXPORT_EXCEL
        status_bar = 'Export to Excel Failed '
        message = 'Unable to export database to Excel - Is the file open? '
        errors[title] = ErrorType(title, status_bar, message)
        
        return errors


class ErrorType(object):
    '''Holds details of error types for use in ErrorHolder.
    '''
    
    def __init__(self, title, status_bar, message=None):        
        self.error_found = False
        self.title = title
        self.status_bar = status_bar
        if message == None:
            self.message = status_bar
        else:
            self.message = message
    
    