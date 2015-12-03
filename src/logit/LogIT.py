'''
###############################################################################
#    
# Name: LogIT (Logger for Isis and Tuflow) 
# Version: 0.2-Beta
# Author: Duncan Runnacles
# Copyright: (C) 2014 Duncan Runnacles
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
# Date:  16/11/2014
# Author:  Duncan Runnacles
# Version:  1.1
# 
# Summary:
#    Main file and GUI for the LogIT software. Deals with all interactions with
#    the user through the interface and updates the GUI.
#
# UPDATES:
#    DR - 19/11/2014:
#        Changed logging procedure so that it is now possible to log an ISIS
#        onlymodel without a Tuflow component.
#
# TODO:
#    It feels like there is a lot more code in this module than there should
#    be. Maybe look at how it could be thinned out a bit by making better use
#    of the controller.py module.
#    There is also an issue with how PyInstaller is dealing with icons at the
#    moment so they have been completely removed. Need to look into this and
#    fix at some point. At the moment only the Python/windows icon is used.
#
###############################################################################
'''

# Python standard modules
import os
import sys
import cPickle
import sqlite3
import logging
 
# Setup the logging protocols. Try and create a directory to put the logs into.
# If that fails we call the console only logger, if not detailed logs will be
# written to file.
# The settings are a dictConfig in the LogSettings.py module.
cur_location = os.getcwd()
log_path = os.path.join(cur_location, 'logs')
try:
    if not os.path.exists(log_path):
        os.mkdir(log_path)
      
    from LogSettings import LOG_SETTINGS
    logging.config.dictConfig(LOG_SETTINGS)
    logger = logging.getLogger(__name__)
    logger.info('Logs will be written to file at: %s' % (log_path))
    CONSOLE_ONLY_LOG = False
except:
    from LogSettings import LOG_SETTINGS_CONSOLE_ONLY
    logging.config.dictConfig(LOG_SETTINGS_CONSOLE_ONLY)
    logger = logging.getLogger(__name__)
    logger.warning('Unable to create log file directory')
    CONSOLE_ONLY_LOG = True


from _sqlite3 import Error

# Fetch the tmac_tools_lib library   
try:
    from tmac_tools_lib.utils.qtclasses import MyFileDialogs
except:
    logger.error('Cannot load tmac_tools_lib (Is it installed?)')
 
# Have to import PyQt4 like this or it won't compile into an .exe
try:
    from PyQt4 import QtCore, QtGui
except:
    logger.error('Cannot import PyQt4 is it installed?')
 
# LogIT specific modules.
from LogIT_UI import Ui_MainWindow
import LogBuilder
import DatabaseFunctions
import Exporters
import Controller


class MainGui(QtGui.QMainWindow):
    '''Main GUI application window for the PysisTools software.
    '''
     
    def __init__(self, cur_settings, cur_settings_path, parent = None):
        '''Constructor.
        @param parent: Reference to the calling class.
        '''        
        # Setup some variables
        if not cur_settings == False:
            self.settings = cur_settings
        else:
            self.settings = LogitSettings()
        
        self.settings.cur_settings_path = cur_settings_path
        
        self.model_log = None
        # Columns that are editable by the user
        self.editing_allowed = ['COMMENTS', 'MODELLER', 'SETUP', 'DESCRIPTION',
                                'EVENT_NAME', 'EVENT_DURATION', 'ISIS_BUILD',
                                'TUFLOW_BUILD', 'AMENDMENTS']
        
        # Database tables that should be exported to Excel
        self.export_tables = ['RUN', 'TCF', 'ECF', 'TGC', 'TBC', 'DAT', 'BC_DBASE']
            
        # Start the application and initialise the GUI
        self.app = QtGui.QApplication(sys.argv)
        
        #icon_path = os.path.join(cur_settings_path, 'Logit_Logo.ico')
        #self.app.setWindowIcon(QtGui.QIcon(':images/Logit_Logo.png'))
        self.app.aboutToQuit.connect(self._customClose)
        MainGui = QtGui.QMainWindow()
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(MainGui)
        
        # Connect the slots
        self.ui.loadModelButton.clicked.connect(self._loadFileActions)
        self.ui.addSingleLogEntryButton.clicked.connect(self._createLogEntry)
        self.ui.addMultiLogEntryButton.clicked.connect(self._createMultipleLogEntry)
        self.ui.addMultiModelButton.clicked.connect(self._updateMultipleLogSelection)
        self.ui.removeMultiModelButton.clicked.connect(self._updateMultipleLogSelection)
        self.ui.multiModelErrorClearButton.clicked.connect(self._clearMultiErrorText)
        self.ui.multiModelErrorCopyButton.clicked.connect(self._copyToClipboard)
        self.ui.actionLoad.triggered.connect(self.fileMenuActions)
        self.ui.actionExportToExcel.triggered.connect(self.fileMenuActions)
        self.ui.actionNewModelLog.triggered.connect(self.fileMenuActions)
        self.ui.actionExit.triggered.connect(self._customClose)
        self.ui.actionUpdateDatabaseSchema.triggered.connect(self._updateDatabaseVersion)
        self.ui.actionSaveSetupAs.triggered.connect(self._saveSetup)
        self.ui.actionLoadSetup.triggered.connect(self._loadSetup)
        self.ui.actionLogWarning.triggered.connect(self._updateLoggingLevel)
        self.ui.actionLogDebug.triggered.connect(self._updateLoggingLevel)
        self.ui.actionLogInfo.triggered.connect(self._updateLoggingLevel)
        self.ui.actionReloadDatabase.triggered.connect(self.loadModelLog)
        
        # A couple of keyboard shortcuts...because I'm lazy!
        # Launch the browse for model dialog
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+L"), self.ui.loadModelButton, 
                                lambda: self._loadFileActions(shortcut='loadmodel'))
        # Add log entry
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+A"), self.ui.addSingleLogEntryButton, 
                                                        self._createLogEntry)
        # Quit
        self.ui.actionExit.setToolTip('Exit Application')
        self.ui.actionExit.setShortcut("Ctrl+Q")
        # Create New database
        self.ui.actionNewModelLog.setToolTip('Create New Model Log Database')
        self.ui.actionNewModelLog.setShortcut("Ctrl+N")
        # Open existing database
        self.ui.actionLoad.setToolTip('Open Existing Model Log Database')
        self.ui.actionLoad.setShortcut("Ctrl+O")
        # Export to Excel
        self.ui.actionExportToExcel.setToolTip('Export Database to Excel Spreadsheet (*.xls)')
        self.ui.actionExportToExcel.setShortcut("Ctrl+E")
        
        # Set the context menu and connect the tables
        self.ui.runEntryViewTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.runEntryViewTable.customContextMenuRequested.connect(self._tablePopup)
        self.ui.tgcEntryViewTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tgcEntryViewTable.customContextMenuRequested.connect(self._tablePopup)
        self.ui.tbcEntryViewTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tbcEntryViewTable.customContextMenuRequested.connect(self._tablePopup)
        self.ui.datEntryViewTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.datEntryViewTable.customContextMenuRequested.connect(self._tablePopup)
        self.ui.bcEntryViewTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.bcEntryViewTable.customContextMenuRequested.connect(self._tablePopup)
        self.ui.ecfEntryViewTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.ecfEntryViewTable.customContextMenuRequested.connect(self._tablePopup)
        self.ui.tcfEntryViewTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tcfEntryViewTable.customContextMenuRequested.connect(self._tablePopup)
        
        # Custom quit function
        #self.app.aboutToQuit.connect(self._customClose)
        
        # Load the user settings from the last time the software was used 
        self._loadSettings()
        
        self.ui_container = {}
        self._setupUiContainer()
        
        # Use those settings to get the file path and try and load the last log
        # database that the user had open
        self.loadModelLog()
        self.log_pages = None
        
        self.setWindowIcon(QtGui.QIcon(':Logit_Logo2_25x25.png'))
        
        # Activate the GUI
        MainGui.show()
        sys.exit(self.app.exec_())
        
    
    def _setupUiContainer(self):
        '''Create a convenient holding object for the gui inputs.
        '''
        self.ui_container['New_log_entry'] = {}
        self.ui_container['New_log_entry']['runEntryTable'] = [self.ui.runEntryTable, 'RUN']
        self.ui_container['New_log_entry']['tcfEntryTable'] = [self.ui.tcfEntryTable, 'TCF']
        self.ui_container['New_log_entry']['ecfEntryTable'] = [self.ui.ecfEntryTable, 'ECF']
        self.ui_container['New_log_entry']['tgcEntryTable'] = [self.ui.tgcEntryTable, 'TGC']
        self.ui_container['New_log_entry']['tbcEntryTable'] = [self.ui.tbcEntryTable, 'TBC']
        self.ui_container['New_log_entry']['bcEntryTable'] = [self.ui.bcEntryTable, 'BC_DBASE']
        self.ui_container['New_log_entry']['datEntryTable'] = [self.ui.datEntryTable, 'DAT']
        #self.ui_container['New_log_entry']['inputVarGroup'] = [self.ui.inputVarGroup, 'inputs']
        
        self.ui_container['View_log'] = {}
        self.ui_container['View_log']['runEntryViewTable'] = [self.ui.runEntryViewTable, 'RUN']
        self.ui_container['View_log']['tcfEntryViewTable'] = [self.ui.tcfEntryViewTable, 'TCF']
        self.ui_container['View_log']['ecfEntryViewTable'] = [self.ui.ecfEntryViewTable, 'ECF']
        self.ui_container['View_log']['tgcEntryViewTable'] = [self.ui.tgcEntryViewTable, 'TGC']
        self.ui_container['View_log']['tbcEntryViewTable'] = [self.ui.tbcEntryViewTable, 'TBC']
        self.ui_container['View_log']['bcEntryViewTable'] = [self.ui.bcEntryViewTable, 'BC_DBASE']
        self.ui_container['View_log']['datEntryViewTable'] = [self.ui.datEntryViewTable, 'DAT'] 
    
    
    def _updateLoggingLevel(self):
        '''Alters to logging level based on the name of the calling action
        
        This is set by an action on the menu.
        '''
        caller = self.sender()
        call_name = caller.objectName()
        #logger.debug('Caller = ' + call_name)
        
        if call_name == 'actionLogWarning':
            
            self.ui.actionLogInfo.setChecked(False)
            self.ui.actionLogDebug.setChecked(False)
            self.ui.actionLogWarning.setChecked(True)

            logging.getLogger().setLevel(logging.WARNING)
            self.settings.logging_level = logging.WARNING
            logger.warning('Logging level set to: WARNING')
            logger.info('warning set check')
         
        elif call_name == 'actionLogInfo':
            logging.getLogger(__name__)
            self.ui.actionLogWarning.setChecked(False)
            self.ui.actionLogDebug.setChecked(False)
            self.ui.actionLogInfo.setChecked(True)

            logging.getLogger().setLevel(logging.INFO)
            self.settings.logging_level = logging.INFO
            logger.info('Logging level set to: INFO')
            logger.debug('info set check')

        elif call_name == 'actionLogDebug':
            self.ui.actionLogWarning.setChecked(False)
            self.ui.actionLogInfo.setChecked(False)
            self.ui.actionLogDebug.setChecked(True)
        
            logging.getLogger().setLevel(logging.DEBUG)
            self.settings.logging_level = logging.DEBUG
            logger.info('Logging level set to: DEBUG')
            logger.debug('Debug set test')
            
        
    def _clearMultiErrorText(self):
        '''Clears the error outputs in multi model load error textbox.
        '''
        self.ui.multiModelLoadErrorTextEdit.clear()
    
    
    def _copyToClipboard(self):
        '''Copies the contents of a textbox to clipboard.
        Textbox to copy is based on the calling action name.
        '''
        caller = self.sender()
        call_name = caller.objectName()
        
        if call_name == 'multiModelErrorCopyButton':
            text = self.ui.multiModelLoadErrorTextEdit.toPlainText()
        
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(text)
            event = QtCore.QEvent(QtCore.QEvent.Clipboard)
            self.app.sendEvent(clipboard, event)
        
    
    def _updateMultipleLogSelection(self):
        '''Updates the contents of the loadMultiModelListView.
        Called by both the add and remove buttons. It will open a multiple
        choice file dialog by the former or remove the selected items by the
        latter.
        '''
        caller = self.sender()
        call_name = caller.objectName()
        logger.debug('Caller = ' + call_name)
        
        # Add a new file
        if call_name == 'addMultiModelButton':
            open_paths = self._getModelFileDialog(multi_paths=True)
            if open_paths == False:
                return
            
            row_count = self.ui.loadMultiModelTable.rowCount()
            for p in open_paths:
                
                # Insert a new row first if needed
                self.ui.loadMultiModelTable.insertRow(row_count)
                
                # Get the filename
                d, fname = os.path.split(str(p))
                self.settings.last_model_directory = d
                
                # Create a couple of items and add to the table
                self.ui.loadMultiModelTable.setItem(row_count, 0, 
                                        Controller.createQtTableItem(fname))
                self.ui.loadMultiModelTable.setItem(row_count, 1, 
                                        Controller.createQtTableItem(p))
                
                # Set the sumbit button to enabled
                self.ui.submitMultiModelGroup.setEnabled(True)
            
        elif call_name == 'removeMultiModelButton':

            # Get the selected rows, reverse them and remove them
            rows = self.ui.loadMultiModelTable.selectionModel().selectedRows()
            rows = sorted(rows, reverse=True)
            for r in rows:
                self.ui.loadMultiModelTable.removeRow(r.row())
            
            # Deactivate the log button if there's no rows left
            if self.ui.loadMultiModelTable.rowCount() < 1:
                self.ui.submitMultiModelGroup.setEnabled(False)
        
        else:
            logger.info('Caller %s not recongnised' % call_name)
       
    
    def _tablePopup(self, pos):
        '''This is the action performed when the user opens the context menu
        with right click on on of the tables in the View Log tab.
        
        Finds out what the user selected from the menu and then performs the
        appropriate action.
        Actions:
            - Update Row: Updates the database with any changes made to the row
              in the View Log table tab. Calls the _saveViewChangesToDatabase()
              function.
            - Delete Row: Deletes the row selected in the table from both the
              database and the table widget. The removal is based on the 'ID'
              value in the row which is supposedly kept in sync with the
              database whenever any changes are made so should be safe?
        
        @param pos: the QPoint of the mouse cursor when clicked.
        '''
        menu = QtGui.QMenu()
        updateRowAction = menu.addAction("Update Row")
        deleteRowAction = menu.addAction("Delete Row")
    
        # Find who called us and get the object that the name refers to.
        sender = self.sender()
        sender = str(sender.objectName())
        
        # lookup the table and database table name
        try:
            table_obj = self.ui_container['View_log'][sender][0]
            table_name = self.ui_container['View_log'][sender][1]
        except KeyError:
            return
        
        # Get the action and do whatever it says
        action = menu.exec_(table_obj.viewport().mapToGlobal(pos))
        if action == updateRowAction:
            self._saveViewChangesToDatabase(table_obj, table_name)
        
        elif action == deleteRowAction:
            self._deleteRowFromDatabase(table_obj, table_name)
            
    
    def _deleteRowFromDatabase(self, table_widget, table_name):
        '''Deletes the row in the database based on the location that the mouse
        was last clicked.
        This is fine because this function is called from the context menu and
        therefore relies on the user right-clicking on the correct row.
        
        @param table_widget: the TableWidget item to get the row data from.
        @param table_name: the name of the database table to remove the row from.
        '''
        
        # Get the currently active row in the table and find it's ID value
        row = table_widget.currentItem().row()
        row_dict = self._getFromTableValues(table_widget, row=row, names=['ID'])
        
        # Just make sure we meant to do this
        message = "Are you sure you want to delete this row?\nTable = %s, Row ID = %s" % (table_name, row_dict['ID'])
        answer = self.launchQtQBox('Confirm Delete?', message)            
        if answer == False:
            return
        
        # Delete from database
        success = Controller.deleteDatabaseRow(self.settings.cur_log_path,
                                               table_name, row_dict['ID'])
        if success:
            # and then from the table
            table_widget.removeRow(row)
            logger.info('Row ID=%s deleted successfully' % (row_dict['ID']))
    
    
    def _saveViewChangesToDatabase(self, table_widget, table_name):
        '''Saves the edits made to the row in the View Log table to the database
        based on the id value in the row that was clicked to launch the context
        menu.
        
        @param table_widget: the table in the user form to takes  updates from.
        @param table_name: the name of the database table to update.
        '''
        row = table_widget.currentItem().row()
        
        # Search through the current row and get the values in the columns that
        # we are going to allow the user to update.
        save_dict = self._getFromTableValues(table_widget, row=row, names='*')
        id_key = save_dict['ID']
        
        # Add the updates to the database
        error = DatabaseFunctions.saveViewChangesToDatabase(table_name, 
                                save_dict, id_key, self.settings.cur_log_path)
        
        db_path = os.path.split(self.settings.cur_log_path)[0]
        if not error == False:
            logger.error('Row ID=%s failed to update' % (id_key))
            QtGui.QMessageBox.warning(self, "Log Entry Update Fail",
                        "Log (%s) entry for ID=%s has failed to update." % (
                                                            db_path, id_key))
        else:
            logger.info('Row ID=%s updated successfully' % (id_key))
            QtGui.QMessageBox.information(self, "Log Entry Updated",
                        "Log (%s) entry for ID=%s has been updated." % (
                                                        db_path, id_key))
                
        
    def loadModelLog(self):
        '''If there is a model log to load we do it.
        '''
        if not self.settings.cur_log_path == '' and not self.settings.cur_log_path == False:

            # Check that the database actually exists. If not get out of here.
            if not os.path.exists(self.settings.cur_log_path):
                logger.info('No existing log database to load')
                self.settings.cur_log_path = ''
                return
            
            title, error = Controller.checkDatabaseVersion(self.settings.cur_log_path)
            if not title == None:
                self.launchQMsgBox(title, error, 'warning')
                return
            
            self._clearTableWidget('view')
             
            # load each of the tables from the database
            for key, table in self.ui_container['View_log'].iteritems():
                t = table[0]
                name = table[1]
                has_vals, count, rows = Controller.fetchTableValues(
                                            self.settings.cur_log_path, name)
            
                # and display in the gui tables all those that loaded
                if has_vals:
                    t.setRowCount(count)
                    count = 0
                    for row in rows:
                        self._putInTableValues(row, t, count)
                        count += 1  
            

    def _fillEntryTables(self, log_pages):
        '''Add the log pages data to the log entry tables that will be
        displayed to the user for amending prior to updating the database.
        
        @param log_pages: the log pages dictionary loaded from the model.
        '''
        # Reset the tables first
        self._clearTableWidget('entry')
        
        self.log_pages = log_pages
        log_pages = self._getInputLogVariables(log_pages)
        
        # Create a list of all of the available tables and their names
        table_list = []
        for key, table in self.ui_container['New_log_entry'].iteritems():
            name = table[1]
            if name == 'RUN': continue
            table_list.append([name, key])
        
        # Update RUN seperately as it's treated in a different way to others
        self._putInTableValues(log_pages['RUN'], self.ui.runEntryTable)
        self._setRowIsEditable(self.ui.runEntryTable, 0)
        
        # check the new entries against the database and return them with
        # flags set for whether they are new entries or already exist
        entries = Controller.loadEntrysWithStatus(
                            self.settings.cur_log_path, log_pages, table_list)
        
        # Add the entries to the gui tables with editable status set
        for e in entries:
            self._putInTableValues(e[0], 
                    self.ui_container['New_log_entry'][e[1]][0], e[2])
            self._setRowIsEditable(
                self.ui_container['New_log_entry'][e[1]][0], e[2], e[3])
        
    
    def _setRowIsEditable(self, table_widget, row_no, is_editable=True):
        '''Sets the colour of the cells in a row according to whether the cell
        is editable or not.
        Cells that can be edited will be set to green.
        Cells that can't be edited will be set to red.
        If a model file has already been entered into the database the entire
        row will be set to red.
        
        @param table_widget: the table that will have cell editing settings
               changed.
        @param row_no: the index of the row to change editing settings on.
        @param is_editable=True: Sets whether the entire row should be set to
               non-editable or not.
        '''
        if is_editable:
            my_color = QtGui.QColor(204, 255, 153) # Light green
        else:
            my_color = QtGui.QColor(255, 204, 204) # Light Red
        
        cols = table_widget.columnCount()
        for c in range(0, cols):
            if is_editable:
                headertext = str(table_widget.horizontalHeaderItem(c).text())
                if headertext in self.editing_allowed:
                    table_widget.item(row_no, c).setBackground(my_color)
            else:
                table_widget.item(row_no, c).setBackground(my_color)
        
        
    def _getInputLogVariables(self, log_pages):
        '''Put the variables entered by the user in the Input log variables
        group into the log_pages dictionary.
        '''
        log_pages['RUN']['MODELLER'] = str(self.ui.modellerTextbox.text())
        log_pages['RUN']['TUFLOW_BUILD'] = str(self.ui.tuflowVersionTextbox.text())
        log_pages['RUN']['ISIS_BUILD'] = str(self.ui.isisVersionTextbox.text())
        log_pages['RUN']['EVENT_NAME'] = str(self.ui.eventNameTextbox.text())
        
        return log_pages
        
                
    def _putInTableValues(self, col_dict, table_obj, row_no=0):
        '''Put values in the given dictionary into the given table where the
        dictionary keys match the column headers of the table.
        
        @param col_dict: dictionary containing the values to put in the table.
        @param table_obj: the QTableWidget object to put the values in.
        '''
        # Insert a new row first if needed
        row_count = table_obj.rowCount()
        if not row_count > row_no:
            table_obj.insertRow(row_count)
        
        row = table_obj.rowAt(row_no)
        headercount = table_obj.columnCount()
        for x in range(0,headercount,1):
            headertext = str(table_obj.horizontalHeaderItem(x).text())
            if headertext in col_dict:
                
                # If it's a loaded variable or db ID then we need to stop 
                # user for corrupting the data and/or database
                if not headertext in self.editing_allowed:
                    table_obj.setItem(row_no, x, Controller.createQtTableItem(
                                        str(col_dict[headertext]), False))
                else:
                    table_obj.setItem(row_no, x, Controller.createQtTableItem(
                                        str(col_dict[headertext]), True))
                
    
    def _getFromTableValues(self, table_obj, row_no=0, row=None, names=None):
        '''Get the item from the table where the header of the column in the
        table matches the given name.
        
        @param table_obj: the QTableWidget object to retrieve the item from.
        @param names: dictionary of names that are being looked for in the
               the table.
        @return: dictionary with the allowed items taken from the table.
        '''
        all_names = False
        if names == None:
            names = self.editing_allowed
        elif names == '*':
            all_names = True
            
        keep_cells = {}
        if row == None:
            row = table_obj.rowAt(row_no)

        headercount = table_obj.columnCount()
        for x in range(0,headercount,1):
            
            headertext = str(table_obj.horizontalHeaderItem(x).text())
            if all_names:
                keep_cells[headertext] = str(table_obj.item(row, x).text())
            else:
                if headertext in names:
                    if not table_obj.item(row, x) == None:
                        keep_cells[headertext] = str(table_obj.item(row, x).text())
                    else:
                        keep_cells[headertext] = 'None'
                
        return keep_cells
        
        
    def _createLogEntry(self):
        '''Take the updated data in the provisional table and load it into the
        model log.
        '''
        # Check that we have a database
        if not self.checkDbLoaded(): return

        if not self.log_pages == None:
            
            self._updateWithUserInputs()
            
            error_details, self.log_pages, update_check = Controller.updateLog(
                                    self.settings.cur_log_path, self.log_pages)
            
            if error_details['Success'] == False:
                self.launchQMsgBox(error_details['Error'], 
                                            error_details['Message']) 
                return
            
            # Add the new entries to the view table as well
            self.updateLogTable(update_check)
            
            # Clear the entry rows and deactivate add new log button
            self._clearTableWidget('entry')
            self.ui.submitSingleModelGroup.setEnabled(False)
            
            # Update the status bar message
            self.ui.statusbar.showMessage("Log Database successfully updated")
            logger.info('Log Database successfully updated')
            
    
    def _createMultipleLogEntry(self):
        '''Takes all the files in the multiple model list, load them and add
        them to the database.        
        '''
        def checkErrorStatus(error_details, error_list):
            '''Look at outputs for errors and let caller know.
            '''
            error_found = False
            if error_details['Success'] == False:
                error_list.append(error_details)
                error_found = True
             
            return error_found, error_list
        

        def writeErrorLogs(load_errors):
            '''Write logs to GUI if any errors found
            '''
            if len(load_errors) < 1: 
                # Let the user know that all is good
                logger.info('Log Database updated successfully')
                self.ui.statusbar.showMessage("Log Database successfully updated")
            
            else:
                # Collect all of the errors and show to user
                logger.warning('One or more models could not be loaded')
                error_files = []
                for e in load_errors:
                    error_files.append(e['Message'])
                error_files.insert(0, 
                        'Models not logged:\n')
                errors = '\n\n'.join(error_files)
                
                self.ui.multiModelLoadErrorTextEdit.setText(errors)
                
                # Reset the progress stuff
                prog_mon.reset('Complete')
                    
                QtGui.QMessageBox.warning(self, 'Logging Error:',
                            'See Error Logs window for details')
            
            
        # Check that we have a database
        if not self.checkDbLoaded(): return
        
        # Get all of the file paths from the list
        model_paths = []
        allRows = self.ui.loadMultiModelTable.rowCount()
        for row in xrange(0,allRows):
            model_paths.append(str(self.ui.loadMultiModelTable.item(row,1).text()))
        
        # Get the type of log to build
        log_type = self.ui.loadMultiModelComboBox.currentIndex()
        
        # Load all of the models into a list
        model_logs = []
        load_errors = []
        
        # Setup the progress monitor. It updates prgress bars etc
        total = len(model_paths)
        prog_mon = ProgressMonitor(self.ui.multiLoadProgressBar, 
                                   self.ui.multiLoadProgressLabel)
        prog_mon.setRanges(total*2, 1, total, 'Loading Model %d or %d')
        
        # Loop through all of the file paths given
        for path in model_paths:
            error_found = False
            
            prog_mon.update()
            
            error_details, log_pages = Controller.fetchAndCheckModel(
                self.settings.cur_log_path, path, log_type, launch_error=False)
            
            # Go to next if we find an error
            error_found, load_errors = checkErrorStatus(error_details, load_errors)
            if error_found: continue
            
            prog_mon.update(bar_only=True)
            
            # Get the global user supplied log variables
            log_pages = self._getInputLogVariables(log_pages)

            # Update the log entries
            error_details, self.log_pages, update_check = Controller.updateLog(
                                self.settings.cur_log_path, log_pages, 
                                check_new_entries=True)
            
            error_found, load_errors = checkErrorStatus(error_details, load_errors)
            if error_found: continue
            
            # Add the new entries to the view table as well
            self.updateLogTable(update_check)
            
        # Clear the list entries
        self.ui.loadMultiModelTable.setRowCount(0)
        writeErrorLogs(load_errors)
        prog_mon.reset('Complete')
        
    
    def _updateWithUserInputs(self):
        '''Get the variables that we want to allow the user to be able to update.
        '''
        # Fetch the values that have editing allowed from the form tables
        # These only have single entries
        updates = {}
        updates['RUN'] = self._getFromTableValues(self.ui.runEntryTable)
        updates['DAT'] = self._getFromTableValues(self.ui.datEntryTable)
        
        # The others can have multiple entries
        for key, table in self.ui_container['New_log_entry'].iteritems():
            t = table[0]
            name = table[1]
            if name == 'RUN' or name == 'DAT': continue
            
            updates[name] = []
            if not self.log_pages[name] == None:
                for i, entry in enumerate(self.log_pages[name], 0):
                    updates[name].append(self._getFromTableValues(t, row_no=i))
        
        # Loop through the updates entries and amend any corresponding log_pages
        for key, val in updates.iteritems():
            if key == 'TGC' or key == 'TBC' or key == 'ECF' or \
                                    key == 'BC_DBASE' or key == 'TCF':
                
                # In this case val is a list
                for i, input_dict in enumerate(val, 0):
                    for item in input_dict:
                        if not self.log_pages[key] == None and \
                            not self.log_pages[key][i] == None and \
                                item in self.log_pages[key][i]:
                            self.log_pages[key][i][item] = val[i][item]
            else:
                for v in val:
                    if not self.log_pages[key] == None and v in self.log_pages[key]:
                        self.log_pages[key][v] = val[v]
            
    
    def updateLogTable(self, update_check):
        '''Updates the log tables on the log view tab.
        '''
        update_check['RUN'] = True
        table_dict = {'RUN': self.ui.runEntryViewTable, 'TGC': self.ui.tgcEntryViewTable,
                      'TBC': self.ui.tbcEntryViewTable, 'DAT': self.ui.datEntryViewTable,
                      'ECF': self.ui.ecfEntryViewTable, 'TCF': self.ui.tcfEntryViewTable,
                      'BC_DBASE': self.ui.bcEntryViewTable}
        
        for t in table_dict:
            
            # Make sure that we have something to update
            if not update_check[t] == False:
                last_row = table_dict[t].rowCount()
                
                # Need to loop through possible multiple rows in these
                if t == 'TGC' or t == 'TBC' or t == 'ECF' or t == 'BC_DBASE' or t == 'TCF':
                    tab_length = len(self.log_pages[t])
                    for i in range(0, tab_length):
                        table_dict[t].setRowCount((last_row + 1))
                        self._putInTableValues(self.log_pages[t][i], table_dict[t], 
                                                                        last_row)
                        last_row += 1
                else:
                    table_dict[t].setRowCount(last_row + 1)
                    self._putInTableValues(self.log_pages[t], table_dict[t], last_row)
                    
    
    def _clearTableWidget(self, table_type):
        '''Clears the row data and completely resets the table at the 
        given type.
        
        @param table_type: the type of table to reset
        '''
        entries = {'RUN': [self.ui.runEntryTable, self.ui.runEntryViewTable], 
                   'TGC': [self.ui.tgcEntryTable, self.ui.tgcEntryViewTable],
                   'TBC': [self.ui.tbcEntryTable, self.ui.tbcEntryViewTable], 
                   'DAT': [self.ui.datEntryTable, self.ui.datEntryViewTable],
                   'BC_DBASE': [self.ui.bcEntryTable, self.ui.bcEntryViewTable],
                   'ECF': [self.ui.ecfEntryTable, self.ui.ecfEntryViewTable],
                   'TCF': [self.ui.tcfEntryTable, self.ui.tcfEntryViewTable]}
        
        if table_type == 'entry' or table_type == 'all':
                        
            for val in entries.itervalues():
                val[0].clearContents()
                val[0].setRowCount(1)
            
        if table_type == 'view' or table_type == 'all':
            for val in entries.itervalues():
                val[1].setRowCount(0)
            
            
    def _loadSettings(self):
        '''Get the settings loaded from file if they exist.
        '''
        try:
            self.ui.statusbar.showMessage("Current log: " + str(self.settings.cur_log_path))
            self.ui.modellerTextbox.setText(self.settings.modeller)
            self.ui.tuflowVersionTextbox.setText(self.settings.tuflow_version)
            self.ui.isisVersionTextbox.setText(self.settings.isis_version)
            self.ui.eventNameTextbox.setText(self.settings.event_name)
            self.ui.loadModelComboBox.setCurrentIndex(int(self.settings.cur_model_type))
            
            if self.settings.logging_level == logging.WARNING:
                self.ui.actionLogWarning.setChecked(True)
            elif self.settings.logging_level == logging.INFO:
                self.ui.actionLogInfo.setChecked(True)
            elif self.settings.logging_level == logging.DEBUG:
                self.ui.actionLogDebug.setChecked(True)                
            
            logging.getLogger().setLevel(self.settings.logging_level)
            
            if self.settings.last_model_directory == '' or self.settings.last_model_directory == False:
                if self.settings.cur_log_path == '' or self.settings.cur_log_path == False:
                    self.settings.last_model_directory = os.path.split(self.settings.cur_settings_path)[0]
                else:
                    self.settings.last_model_directory = os.path.split(self.settings.cur_log_path)[0]
       
            self.ui.loadModelTextbox.setText(self.settings.last_model_directory)
        
        except:
            logger.warning('Was unable to retrieve previous settings - Has LogIT been updated?')
        
    
    def _writeSettings(self, save_path):
        '''Need a custom close event so that we can save the user settings.
        '''            
        logger.info('Closing program')
        logger.info('Saving user settings to: ' + save_path)
        self.settings.modeller = str(self.ui.modellerTextbox.text())
        self.settings.tuflow_version = str(self.ui.tuflowVersionTextbox.text())
        self.settings.isis_version = str(self.ui.isisVersionTextbox.text())
        self.settings.event_name = str(self.ui.eventNameTextbox.text())
        self.settings.cur_model_type = str(self.ui.loadModelComboBox.currentIndex())
        try:
            # Load the UnitCollection from file and convert it back to the
            # dictionary format being used.
            with open(save_path, "wb") as p:
                cPickle.dump(self.settings, p)
        except:
            logger.info('Unable to save user defined settings')
    
    
    def _saveSetup(self):
        '''Write the current LogIT setup to file.
        '''
        d = MyFileDialogs()
        save_path = d.saveFileDialog(path=os.path.split(
                            self.settings.cur_log_path)[0], 
                            file_types='Log Settings (*.logset)')
        
        if save_path == False:
            return
        self._writeSettings(str(save_path))
        
    
    def _loadSetup(self):
        '''Load LogIT setup from file.
        '''
        settings, err_title, err_msg = Controller.loadSetup(
                self.settings.cur_settings_path, self.settings.cur_log_path)
         
        if settings == False:
            if not err_title == None:
                QtGui.QMessageBox.warning(self, err_title, err_msg)
            return
        else:
            self.settings = settings
            self._loadSettings()
        
    
    def _customClose(self):
        '''Do the things that need doing before closing window.
        '''
        save_path = self.settings.cur_settings_path
        self._writeSettings(save_path)
        # We need sys.exit because otherwise this function will be called twice.
        #self.app.quit()
        sys.exit()            

 
    def _updateDatabaseVersion(self): 
        '''Checks if the databse at the given path is compatible with the
        latest version of LogIT.
        '''
        errors = Controller.updateDatabaseVersion()
        if errors == None:
            return
        elif errors['Success'] == False:
            msg = "Failed to update database scheme: See log for details"
            self.launchQMsgBox('Database Update Failed', message)
        else:
        
            msg = "Update Successfull\nWould you like to load updated database?"
            reply = self.launchQtQBox('Update Successful', msg)
            if not reply == False:
                temp = self.settings.cur_log_path = open_path
                try:
                    self.loadModelLog()
                    self.ui.statusbar.showMessage("Current log: " + open_path)
                except:
                    logger.error('Cannot load database: see log for details')
                    msg = "Failed to open database: See log for details"
                    self.launchQMsgBox('Database Update Failed', message)
                    self.settings.cur_log_path = temp
    
    
    def _createNewLogDatabase(self):
        '''Create a new model log database.
        '''
        d = MyFileDialogs()
        save_path = d.saveFileDialog(path=os.path.split(
                                    self.settings.cur_settings_path)[0], 
                                     file_types='LogIT database(*.logdb)')
        
        if not save_path == False:
            self.settings.cur_log_path = str(save_path)
            self._clearTableWidget('all')
            self.ui.statusbar.showMessage('Building new log database...')
            self.ui.centralwidget.setEnabled(False)
            DatabaseFunctions.createNewLogDatabase(str(save_path))
            self.ui.centralwidget.setEnabled(True)
            self.ui.statusbar.showMessage("Current log: " + save_path)
    
    
    def _loadDatabaseFromUser(self):
        '''Load database chosen by user in dialog.
        '''
        d = MyFileDialogs()
        if not self.checkDbLoaded():
            open_path = str(d.openFileDialog(path=self.settings.cur_log_path, 
                                        file_types='LogIT database(*.logdb)'))
        else:
            open_path = str(d.openFileDialog(path=self.settings.cur_settings_path, 
                                        file_types='LogIT database(*.logdb)'))
        
        if open_path == False:
            return
        
        if self.settings == False:
            self.settings = LogitSettings()
        
        self.settings.cur_log_path = open_path
        
        try:
            self.loadModelLog()
            self.ui.statusbar.showMessage("Current log: " + open_path)
        except:
            logger.error('Cannot load database: see log for details')
    
    
    def _exportDatabase(self, call_name):
        '''Exports the database based on calling action.
        '''
        if self.checkDbLoaded():
            err_details = Controller.exportToExcel(
                        self.settings.cur_log_path, self.export_tables)
            
            if err_details['Success'] == False:
                self.launchQMsgBox(err_details['Error'], err_details['Message'])
                self.ui.statusbar.showMessage(err_details['Status_bar'])
            else:
                self.launchQMsgBox(err_details['Error'], 
                                   err_details['Message'], 'info')
                self.ui.statusbar.showMessage(err_details['Status_bar'])
        else:
            logger.warning('Cannot export log - no database loaded')
            QtGui.QMessageBox.warning(self, "Cannot Export Log",
                                      "There is no log database loaded")
        

    def fileMenuActions(self):
        '''Respond to actions that occur on the file menu
        '''
        caller = self.sender()
        call_name = caller.objectName()
        logger.debug('Caller = ' + call_name)
        
        if call_name == 'actionNewModelLog':
            self._createNewLogDatabase()
        
        elif call_name == 'actionLoad':
            self._loadDatabaseFromUser()
                                    
        elif call_name == 'actionExportToExcel':
            self._exportDatabase(call_name)
            
            
    def _getModelFileDialog(self, multi_paths=False):
        '''Launches an open file dialog to get .ief or .tcf files.
        
        @param multi_paths=False: if set to True it will return a list of all
               the user selected paths, otherwise a single string path.
        @return: The chosen file path, a list of paths or false if the user 
                 cancelled.
        '''

        # Check that we have a database
        if not self.checkDbLoaded():
            QtGui.QMessageBox.warning(self, "No Database Loaded",
                "No log database active. Please load or create one from" +
                                                    " the file menu.")
            logger.error('No log database found. Load or create one from File menu')
            return            

        open_path = Controller.getModelFileLocation(multi_paths,
            self.settings.last_model_directory, self.settings.cur_log_path,
                self.settings.cur_settings_path)
        
        return open_path
    
          
    def _loadFileActions(self, shortcut=None):
        '''Respond to the user clicking a button that loads a file.
        '''
        caller = self.sender()
        call_name = caller.objectName()
        logger.debug('Caller = ' + call_name)
        
        # Trying to load a model to add to the log
        if call_name == 'loadModelButton' or shortcut == 'loadmodel':
                
            # Launch dialog and get a file
            open_path = self._getModelFileDialog()
            
            # If the user doesn't cancel
            if not open_path == False:
                open_path = str(open_path)
                self.ui.loadModelTextbox.setText(open_path)
                self.settings.last_model_directory = os.path.split(str(open_path))[0]
                
                # Get the log type index
                log_type = self.ui.loadModelComboBox.currentIndex()
                
                result, log_pages = Controller.fetchAndCheckModel(
                    self.settings.cur_log_path, open_path, log_type)
    
                if result['Success'] == False:
                    QtGui.QMessageBox.warning(self, result['Error'],
                    result['Message'])
                    self.ui.statusbar.showMessage(result['Status_bar'])
                else:
                    self.ui.statusbar.showMessage(result['Status_bar'])
                    self._fillEntryTables(log_pages)
                    self.ui.submitSingleModelGroup.setEnabled(True) 


    def launchQtQBox(self, title, message):
        '''Launch QtQMessageBox.
        '''
        answer = QtGui.QMessageBox.question(self, title, message,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if answer == QtGui.QMessageBox.No:
            return False
        else:
            return answer
    
    
    def launchQMsgBox(self, title, message, type='warning'):
        '''Launch a QMessageBox
        '''
        if type == 'warning':
            QtGui.QMessageBox.warning(self, title, message)
        
        elif type == 'info':
            QtGui.QMessageBox.information(self, title, message)
    
    
    def checkDbLoaded(self):
        '''Check if there's a database filepath set.
        '''
        if self.settings.cur_log_path == '' or self.settings.cur_log_path == False:
            QtGui.QMessageBox.warning(self, "No Database Loaded",
                    "No log database active. Please load or create one from the file menu.")
            logger.error('No log database found. Load or create one from File menu')
            return False
        return True
        

class ProgressMonitor(object):
    '''Convenience class for updating progress bars and text.
    
    This stays in this module becuase it sort of breaks the encapsulation of
    the MainGui class by updating its progress bar and text label. It's better
    than having to little progress update code all over the place though.
    '''
     
    def __init__(self, progbar_ui, text_ui=None):
        self.progbar_ui = progbar_ui
        self.text_ui = text_ui
        self.prog_cur = 0
        self.text_cur = 0
    
    def setRanges(self, prog_up, text_down=None, text_up=None, textform='%d of %d'): 
        '''Set the range to operate on.
        @param prog_up: max progress bar value.
        @param text_down=None: lowest text counter value.
        @param text_up=None: max text counter value.
        @param textform=None: format to dislplay text counter in.
        '''
        self.prog_up = prog_up
        self.text_up = text_up
        self.text_current = self.text_down = text_down
        self.textform = textform
        self.progbar_ui.setRange(0, prog_up)
        self.setToStart()
    
    def setToStart(self):
        '''Set progress counters to start point.
        '''
        self.progbar_ui.setValue(0)
        if not self.text_ui == None:
            text_out = self.textform % (self.text_cur, self.text_up)
            self.text_ui.setText(text_out)
    
    def reset(self, text=None):
        '''Reset the progress bar to normal state.
        @param text=None: text to display in text label.
        '''
        self.setToStart()
        if text == None: text = ''
        self.text_ui.setText(text)
    
    def update(self, bar_only=False, text_only=False):
        '''Update progress.
        @param bar_only=False: don't update the progress bar.
        @param text_only=False: don't update the text counter.
        '''
        if not text_only:
            self.updateBarProgress()
        if not bar_only:
            self.updateTextProgress()
        QtGui.QApplication.processEvents()
    
    def updateBarProgress(self):
        '''Iterate and update progress bar
        '''
        self.prog_cur += 1
        self.progbar_ui.setValue(self.prog_cur)
    
    def updateTextProgress(self):
        '''Iterate and update text counter label.
        '''
        if self.text_ui == None:
            return
        else:
            self.text_cur += 1
            text_out = self.textform % (self.text_cur, self.text_up)
            self.text_ui.setText(text_out)


class LogitSettings(object):
    '''Storage class for holding all of the settings that the current user has
    stored.
    '''
    
    def __init__(self):
        '''Constructor.
        '''
        self.cur_log_path = ''
        self.cur_settings_path = ''
        self.last_model_directory = ''
        self.modeller = ''
        self.tuflow_version = ''
        self.isis_version = ''
        self.event_name = ''
        self.log_path = ''
        self.log_export_path = ''
        self.cur_model_type = 0
        self.logging_level = 0
        
        
def main():
    # Set up the logging module with software specific settings.
    #import logging.config
    #import logging
     
    # Need to do this so that the icons show up properly
    import ctypes
    myappid = 'logit.0-3-Beta'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    QPlugin = QtCore.QPluginLoader("qico4.dll")
     
    cur_location = os.getcwd()
    settings_path = os.path.join(cur_location, 'settings.logset')
 
    try:
        # Load the settings dictionary
        cur_settings = cPickle.load(open(settings_path, "rb"))
        cur_settings.cur_settings_path = settings_path 
    except:
        cur_settings = False
        #logging.info('Unable to load user defined settings')
        print 'Unable to load user defined settings'
         
    # Launch the user interface.
    MainGui(cur_settings, settings_path)
 
 
if __name__ == '__main__': main()

