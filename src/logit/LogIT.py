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
import win32clipboard
 
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
    #from LogSettings import LOG_SETTINGS_WARNING
    #logging.config.dictConfig(LOG_SETTINGS_WARNING)
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
        
        # Use those settings to get the file path and try and load the last log
        # database that the user had open
        self.loadModelLog()
        self.log_pages = None
        
        self.setWindowIcon(QtGui.QIcon(':Logit_Logo2_25x25.png'))
        
        # Activate the GUI
        MainGui.show()
        sys.exit(self.app.exec_())
        
    
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
        '''
        '''
        self.ui.multiModelLoadErrorTextEdit.clear()
    
    def _copyToClipboard(self):
        '''
        '''
        caller = self.sender()
        call_name = caller.objectName()
        
        if call_name == 'multiModelErrorCopyButton':
            text = self.ui.multiModelLoadErrorTextEdit.toPlainText()
        
#         try:
#             win32clipboard.OpenClipboard()
#             win32clipboard.EmptyClipboard()
#             win32clipboard.SetClipboardText(s)
#             win32clipboard.CloseClipboard()
#         except:
#             logger.warning('Could not copy clipboard data.')
            
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
                itemf = QtGui.QTableWidgetItem(str(fname))
                itemf.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                itemp = QtGui.QTableWidgetItem(str(p))
                itemp.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ui.loadMultiModelTable.setItem(row_count, 0, itemf)
                self.ui.loadMultiModelTable.setItem(row_count, 1, itemp)
                
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
        sender = sender.objectName()
        
        # Table objects
        if sender == 'runEntryViewTable':
            table_obj = self.ui.runEntryViewTable
            table_name = 'RUN'
        elif sender == 'tgcEntryViewTable':
            table_obj = self.ui.tgcEntryViewTable
            table_name= 'TGC'
        elif sender == 'tbcEntryViewTable':
            table_obj = self.ui.tbcEntryViewTable
            table_name = 'TBC'
        elif sender == 'datEntryViewTable':
            table_obj = self.ui.datEntryViewTable
            table_name = 'DAT'
        elif sender == 'bcEntryViewTable':
            table_obj = self.ui.bcEntryViewTable
            table_name = 'BC_DBASE'
        elif sender == 'ecfEntryViewTable':
            table_obj = self.ui.ecfEntryViewTable
            table_name = 'ECF'
        elif sender == 'tcfEntryViewTable':
            table_obj = self.ui.tcfEntryViewTable
            table_name = 'TCF'
        else:
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
        answer = QtGui.QMessageBox.question(self, "Confirm Delete",
            "Are you sure you want to delete this row?\n" +
            "Table = %s, Row ID = %s" % (table_name, row_dict['ID']),
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if answer == QtGui.QMessageBox.No:
            return
        
        conn = None
        try:
            # Delete the row from the database
            conn = DatabaseFunctions.loadLogDatabase(self.settings.cur_log_path)
            DatabaseFunctions.deleteRowFromTable(conn, table_name, row_dict['ID'])
            
            # and then from the table
            table_widget.removeRow(row)
            logger.info('Row ID=%s deleted successfully' % (row_dict['ID']))
            
        except IOError:
            logger.error('Unable to access database - see log for details')
        except Exception:
            logger.error('Unable to access database - see log for details')
        finally:
            if not conn == None:
                conn.close()
    
    
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
        conn = False
        if not self.settings.cur_log_path == '' and not self.settings.cur_log_path == False:

            # Check that the database actually exists. If not get out of here.
            if not os.path.exists(self.settings.cur_log_path):
                logger.info('No existing log database to load')
                self.settings.cur_log_path = ''
                return
            try:
                # Need to check that the database is aligned with the current version
                version_check = DatabaseFunctions.checkDatabaseVersion(self.settings.cur_log_path)
                if version_check == DatabaseFunctions.DATABASE_VERSION_LOW:
                    logger.error('Database version is old - please update database')
                    QtGui.QMessageBox.warning(self, "Load Error",
                        "Unable to load model log from file at: " + self.settings.cur_log_path +
                        "\nDatabase needs updating to latest" +
                        " version.\nUse Settings > Tools > Update Database Schema." +
                        " See Help for details." )
                    return
                    
                elif version_check == DatabaseFunctions.DATABASE_VERSION_HIGH:
                    logger.error('Database version in new - please update LogIT')
                    QtGui.QMessageBox.warning(self, "Load Error",
                        "Unable to load model log from file at: " + self.settings.cur_log_path +
                        "\nDatabase was produced with newer version of LogIT.\n" +
                        "Update to latest version of LogIT to use database.") 
                    return
                
                conn = DatabaseFunctions.loadLogDatabase(self.settings.cur_log_path)
                cur = conn.cursor()
                cur.execute("select * from RUN")
            except:
                conn = False
                QtGui.QMessageBox.warning(self, "Load Error",
                    "Unable to load model log from file at: %s." % self.settings.cur_log_path)
                logger.error('Unable to load model log from file at: \n' + self.settings.cur_log_path)
                return
        
        if not conn == False:
            
            self._clearTableWidget('view')
             
            # Fetch data from the RUN table
            conn.row_factory = sqlite3.Row
            
            # Get the tables and update
            run_table = self.ui.runEntryViewTable
            self._fetchAndShowTable(conn, run_table, 'RUN')
            tgc_table = self.ui.tgcEntryViewTable
            self._fetchAndShowTable(conn, tgc_table, 'TGC')
            tbc_table = self.ui.tbcEntryViewTable
            self._fetchAndShowTable(conn, tbc_table, 'TBC')
            dat_table = self.ui.datEntryViewTable
            self._fetchAndShowTable(conn, dat_table, 'DAT')
            bc_table = self.ui.bcEntryViewTable
            self._fetchAndShowTable(conn, bc_table, 'BC_DBASE') 
            ecf_table = self.ui.ecfEntryViewTable
            self._fetchAndShowTable(conn, ecf_table, 'ECF')
            tcf_table = self.ui.tcfEntryViewTable
            self._fetchAndShowTable(conn, tcf_table, 'TCF')
                
            conn.close()
            
    
    def _fetchAndShowTable(self, conn, table_widget, table_name):
        '''Get the table from the database and show it on the gui.
        
        @param cursor: the cursor from the open database connection.
        @param table_widget: the TableWidget on the form to display the data in.
        @param db_table_name: the name of the database table to load data from.
        '''
        results = DatabaseFunctions.findInDatabase(table_name, db_path=False, conn=conn, 
                                                            return_rows=True)
        if not results[0] == False:
            count = results[1]
            table_widget.setRowCount(count)
            count = 0
            for row in results[2]:
                self._putInTableValues(row, table_widget, count)
                count += 1        
        

    def _findNewLogEntries(self, conn, log_pages, log_name, entry_table=None, 
                                                        multiple_files=True):
        '''Checks the log entries to see if they already exist, adds them to
        their respective tables and highlights the cells.
        '''
        
        logger.debug('Find Entry: log_name=%s, entry_table=%s' % (log_name, entry_table))
        
        # Most files are multiple but the DAT file entry isn't so has to be 
        # dealt with seperately as it doesn't need looping through
        if multiple_files:
            if not log_pages[log_name] == None:
                mod_length = len(log_pages[log_name])
                
                # We have to loop backwards here because we might delete entries
                for i in range(mod_length-1, -1, -1):
                    
                    if log_pages[log_name][i][log_name] == 'None':
                        log_pages[log_name][i] = None
                    else:
                    
                        is_new_entry = DatabaseFunctions.findNewEntries(
                                            conn, log_name, log_pages[log_name][i])
        
                        # If we're adding them to the editable tables we do it
                        # Otherwise just get rid of those we don't want
                        if not entry_table == None:
                            self._putInTableValues(log_pages[log_name][i], entry_table, i)
                            
                            # If it'a already in the database then we remove it from the log
                            # dictionary to avoid entering it again.
                            if not is_new_entry:
                                self._setRowIsEditable(entry_table, i, False)
                                del log_pages[log_name][i]
                            else:
                                self._setRowIsEditable(entry_table, i)
                        else:
                            if not is_new_entry:
                                del log_pages[log_name][i]
        else:
            if not entry_table == None:
                self._putInTableValues(log_pages[log_name], entry_table)
                if not DatabaseFunctions.findNewEntries(conn, log_name, log_pages[log_name]):
                    self._setRowIsEditable(entry_table, 0, False)
                    log_pages[log_name] = None
                else:
                    self._setRowIsEditable(entry_table, 0)
            else:
                log_pages[log_name] = None
        
        return log_pages


    def _fillEntryTables(self, log_pages):
        '''Add the log pages data to the log entry tables that will be
        displayed to the user for amending prior to updating the database.
        
        @param log_pages: the log pages dictionary loaded from the model.
        '''
        # Reset the tables first
        self._clearTableWidget('entry')
        
        self.log_pages = log_pages
        log_pages = self._getInputLogVariables(log_pages)
        
        # Update RUN
        self._putInTableValues(log_pages['RUN'], self.ui.runEntryTable)
        self._setRowIsEditable(self.ui.runEntryTable, 0)
        
        # We need to find if the TGC and TBC files have been registered with the
        # database before. If they have then we don't need to register them 
        # again.
        conn = False
        try:
            conn = DatabaseFunctions.loadLogDatabase(self.settings.cur_log_path)
            
            # Find log entries and populate tables for the model files
            log_pages = self._findNewLogEntries(conn, log_pages, 'TGC', 
                                                    self.ui.tgcEntryTable)
            log_pages = self._findNewLogEntries(conn, log_pages, 'TBC', 
                                                    self.ui.tbcEntryTable)
            log_pages = self._findNewLogEntries(conn, log_pages, 'ECF', 
                                                    self.ui.ecfEntryTable)
            log_pages = self._findNewLogEntries(conn, log_pages, 'TCF', 
                                                    self.ui.tcfEntryTable)
            log_pages = self._findNewLogEntries(conn, log_pages, 'BC_DBASE', 
                                                    self.ui.bcEntryTable)
            
            # DAT files get dealt with separately as there can only be one.
            if log_pages['DAT']['DAT'] == 'None': 
                log_pages['DAT'] = None
            else:
                log_pages = self._findNewLogEntries(conn, log_pages, 'DAT', 
                                        self.ui.datEntryTable, False)
                
        except IOError:
            logger.error('IOError - Unable to access database')
        except Error:
            logger.error('SQLError - Could not query database')
        finally:
            if not conn == False:
                conn.close()
        
    
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
        
#         return str(self.ui.modellerTextbox.text()), \
#                 str(self.ui.tuflowVersionTextbox.text()), \
#                 str(self.ui.isisVersionTextbox.text()), \
#                 str(self.ui.eventNameTextbox.text())

                
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
                item = QtGui.QTableWidgetItem(str(col_dict[headertext]))
                
                # If it is the ID column we have to ensure that no one can mess
                # with it, otherwise we could accidentally corrupt the underlying
                # database. With the other
                if not headertext in self.editing_allowed:
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
                
                table_obj.setItem(row_no, x, item)
                
                if not headertext in self.editing_allowed:
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                
    
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
        if self.settings.cur_log_path == '' or self.settings.cur_log_path == False:
            QtGui.QMessageBox.warning(self, "No Database Loaded",
                    "No log database active. Please load or create one from the file menu.")
            logger.error('No log database found. Load or create one from File menu')
            return

        if not self.log_pages == None:
            
            self._updateWithUserInputs()
            
            # Connect to the database and then update the log entries
            conn = False
            error_found = False
            try:
                conn = DatabaseFunctions.loadLogDatabase(
                                            self.settings.cur_log_path)
                self.log_pages, update_check = Controller.logEntryUpdates(
                                                        conn, self.log_pages)
            except IOError:
                logger.error('Unable to access database')
                error_found = True
            except Error:
                logger.error('Error updating database -  See log for details')
                error_found = True
            finally:
                if not conn == False:
                    conn.close()
            
            if error_found:
                QtGui.QMessageBox.warning(self, 'Unable to Update Database',
                    'Problem updating database: see log for details')
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
        TODO:
            Currently a copy of the method above. Need to implement properly.
        '''
        
        def _updateProgressBar(prog_val, label_text=None):
            '''Updates the progress bar on the multiple model load tab.
            '''
            self.ui.multiLoadProgressBar.setValue(prog_val)
            if not label_text == None:
                self.ui.multiLoadProgressLabel.setText(label_text)
            QtGui.QApplication.processEvents()
            return prog_val + 1

        
        # Check that we have a database
        if self.settings.cur_log_path == '' or self.settings.cur_log_path == False:
            QtGui.QMessageBox.warning(self, "No Database Loaded",
                    "No log database active. Please load or create one from the file menu.")
            logger.error('No log database found. Load or create one from File menu')
            return
        
        # Get all of the file paths from the list
        model_paths = []
        allRows = self.ui.loadMultiModelTable.rowCount()
        for row in xrange(0,allRows):
            #rows.append(index.row()) 
            model_paths.append(str(self.ui.loadMultiModelTable.item(row,1).text()))
        
        # Get the type of log to build
        log_type = self.ui.loadMultiModelComboBox.currentIndex()
        
        # Load all of the models into a list
        model_logs = []
        load_errors = []
        total = len(model_paths)
        current = 1
        load_progress = 0
        total_progress = total*2
        self.ui.multiLoadProgressBar.setRange(0, total_progress)
        
        # Loop through all of the file paths given
        for path in model_paths:
            error_found = False
            
            try:
                load_progress = _updateProgressBar(load_progress, 
                                   'Loading Model %d of %d' % (current, total))
                
                log_pages, result = self._fetchAndCheckModel(path, log_type, launch_error=False)
                
                if result['Success'] == False:
                    load_errors.append(result)
                    error_found = True
                    continue
                
            except IOError:
                load_errors.append({'Success': False, 
                    'Status_bar': "Unable to update Database with model: %s" % path,
                     'Error': 'IO Error', 
                    'Message': "Unable to load model from file at: %s" % path})
                error_found = True
            except:
                load_errors.append({'Success': False, 
                    'Status_bar': "Unable to update Database with model: %s" % path,
                     'Error': 'IO Error', 
                    'Message': "Unable to load model from file at: %s" % path})
                error_found = True
            
            if not error_found:
                # Setup progress bar stuff
                load_progress = _updateProgressBar(load_progress)
                
                # Get the global user supplied log variables
                log_pages = self._getInputLogVariables(log_pages)
    
                # Connect to the database and then update the log entries
                conn = False
                error_found = False
                try:
                    conn = DatabaseFunctions.loadLogDatabase(
                                                self.settings.cur_log_path)
                    
                    self.log_pages, update_check = Controller.logEntryUpdates(
                                        conn, log_pages, check_new_entries=True)
                except IOError:
                    logger.error('Unable to access database')
                    error_found = True
                except Error:
                    logger.error('Error updating database -  See log for details')
                finally:
                    if not conn == False:
                        conn.close()
            
            # Log any errors to show later
            if error_found:
                load_errors.append({'Success': False, 
                    'Status_bar': "Unable to update Database with model: %s" % path,
                     'Error': 'Database Error', 
                    'Message': "Unable to update Database with model: %s" % path})
                continue
            
            # Add the new entries to the view table as well
            self.updateLogTable(update_check)
            current += 1
        
        load_progress = _updateProgressBar(0, 'Complete')
            
        # Clear the list entries
        self.ui.loadMultiModelTable.setRowCount(0)
        
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
            _updateProgressBar(0, 'Complete')
                
            QtGui.QMessageBox.warning(self, 'Logging Error:',
                        'See Error Logs window for details')
            
    
    def _updateWithUserInputs(self):
        '''Get the variables that we want to allow the user to be able to update.
        '''
        # Fetch the values that have editing allowed from the form tables
        updates = {}
        updates['RUN'] = self._getFromTableValues(self.ui.runEntryTable)
        
        # For tgc, tbc, ecf and bc_dbase this most be done for multiple files
        updates['TGC'] = []
        if not self.log_pages['TGC'] == None:
            for i, entry in enumerate(self.log_pages['TGC'], 0):
                updates['TGC'].append(self._getFromTableValues(self.ui.tgcEntryTable, row_no=i))
        
        if not self.log_pages['TBC'] == None:
            updates['TBC'] = []
            for i, entry in enumerate(self.log_pages['TBC'], 0):
                updates['TBC'].append(self._getFromTableValues(self.ui.tbcEntryTable, row_no=i))
        
        if not self.log_pages['ECF'] == None:
            updates['ECF'] = []
            for i, entry in enumerate(self.log_pages['ECF'], 0):
                updates['ECF'].append(self._getFromTableValues(self.ui.ecfEntryTable, row_no=i))
        
        if not self.log_pages['TCF'] == None:
            updates['TCF'] = []
            for i, entry in enumerate(self.log_pages['TCF'], 0):
                updates['TCF'].append(self._getFromTableValues(self.ui.tcfEntryTable, row_no=i))
                
        if not self.log_pages['BC_DBASE'] == None:
            updates['BC_DBASE'] = []
            for i, entry in enumerate(self.log_pages['BC_DBASE'], 0):
                updates['BC_DBASE'].append(self._getFromTableValues(self.ui.bcEntryTable, row_no=i))
            
        updates['DAT'] = self._getFromTableValues(self.ui.datEntryTable)
        
        # Loop through the updates entries and amend any corresponding log_pages
        for key, val in updates.iteritems():
            if key == 'TGC' or key == 'TBC' or key == 'ECF' or \
                                    key == 'BC_DBASE' or key == 'TCF':
                
                # In this case val is a list
                for i, input_dict in enumerate(val, 0):
                    for item in input_dict:
                        if not self.log_pages[key] == None and not self.log_pages[key][i] == None and item in self.log_pages[key][i]:
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
        d = MyFileDialogs()
        open_path = d.openFileDialog(path=os.path.split(
                            self.settings.cur_log_path)[0], 
                            file_types='Log Settings (*.logset)')
        
        if open_path == False:
            return
        try:
            # Load the settings dictionary
            open_path = str(open_path)
            cur_settings = cPickle.load(open(open_path, "rb"))
            cur_settings.cur_settings_path = self.settings.cur_settings_path
            self.settings = cur_settings 
        except:
            logging.info("Unable to load user settings from: %s" % (open_path))
            logger.error('Could not load settings file')
            QtGui.QMessageBox.warning(self, "Load Failed",
                    "Unable to load user settings from: %s" % (open_path))
            return
        
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
         
        @param db_path: path to the database to check.
        '''
        d = MyFileDialogs()
        if not self.settings.cur_log_path == '' and not self.settings.cur_log_path == False:
            open_path = str(d.openFileDialog(path=self.settings.cur_log_path, file_types='LogIT database(*.logdb)'))
        else:
            open_path = str(d.openFileDialog(path=self.settings.cur_settings_path, file_types='LogIT database(*.logdb)'))
         
        if not open_path == False:
            try:
                DatabaseFunctions.updateDatabaseVersion(open_path)
                
            except:
                logger.error('Failed to update database scheme: See log for details')
                QtGui.QMessageBox.warning(self, "Database Update Failed",
                        "Failed to update database scheme: See log for details") 
                return
            
            msg = "Update Successfull\nWould you like to load updated database?"
            reply = QtGui.QMessageBox.question(self, 'Update Successfull', 
                        msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.settings.cur_log_path = open_path
                try:
                    self.loadModelLog()
                    self.ui.statusbar.showMessage("Current log: " + open_path)
                except:
                    logger.error('Cannot load database: see log for details')
                    QtGui.QMessageBox.warning(self, "Database Open Failed",
                        "Failed to open database: See log for details") 
                    
            
        

    def fileMenuActions(self):
        '''Respond to actions that occur on the file menu
        '''
        caller = self.sender()
        call_name = caller.objectName()
        logger.debug('Caller = ' + call_name)
        
        if call_name == 'actionNewModelLog':
            d = MyFileDialogs()
            save_path = d.saveFileDialog(path=os.path.split(
                                        self.settings.cur_settings_path)[0], 
                                         file_types='LogIT database(*.logdb)')
            
            if not save_path == False:
                
                # Check if we are about to write over an existing database
                create_db = True
                
                # Removed because the system already checks this.
#                 if os.path.exists(save_path):
#                     button = QtGui.QMessageBox.question(self, "Confirm Remove",
#                         "Existing database will be reset to new. Continue?\nDatabase = %s" % save_path,
#                         QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
#                     if button == QtGui.QMessageBox.No:
#                         create_db = False
                
                if create_db:
                    self.settings.cur_log_path = str(save_path)
                    self._clearTableWidget('all')
                    self.ui.statusbar.showMessage('Building new log database...')
                    self.ui.centralwidget.setEnabled(False)
                    DatabaseFunctions.createNewLogDatabase(str(save_path))
                    self.ui.centralwidget.setEnabled(True)
                    self.ui.statusbar.showMessage("Current log: " + save_path)
        
        elif call_name == 'actionLoad':
            d = MyFileDialogs()
            if not self.settings.cur_log_path == '' and not self.settings.cur_log_path == False:
                open_path = str(d.openFileDialog(path=self.settings.cur_log_path, file_types='LogIT database(*.logdb)'))
            else:
                open_path = str(d.openFileDialog(path=self.settings.cur_settings_path, file_types='LogIT database(*.logdb)'))
            if self.settings == False:
                self.settings = LogitSettings()
            
            if not open_path == False:
                self.settings.cur_log_path = open_path
                
                try:
                    self.loadModelLog()
                    self.ui.statusbar.showMessage("Current log: " + open_path)
                except:
                    logger.error('Cannot load database: see log for details')
                                    
        elif call_name == 'actionExportToExcel':
            if not self.settings.cur_log_path == '' and not self.settings.cur_log_path == False:
                d = MyFileDialogs()
                save_path = d.saveFileDialog(path=os.path.split(
                                            self.settings.cur_log_path)[0], 
                                             file_types='Excel File (*.xls)')
                save_path = str(save_path)
                
                if not save_path == False:
                    try:
                        Exporters.exportToExcel(self.settings.cur_log_path, 
                                                self.export_tables, save_path)
                    except:
                        logger.error('Could not export log to Excel')
                        QtGui.QMessageBox.warning(self, "Export Failed",
                                            "Unable to export database to Excel - Is the file open?")
                        return
                   
                    logger.info('Database exported to Excel at:\n%s' % (save_path))
                    QtGui.QMessageBox.information(self, "Export Complete",
                    "Database exported to Excel at: %s." % save_path)
            else:
                logger.warning('Cannot export log - no database loaded')
                QtGui.QMessageBox.warning(self, "Cannot Export Log",
                                          "There is no log database loaded")
            
            
    def _getModelFileDialog(self, multi_paths=False):
        '''Launches an open file dialog to get .ief or .tcf files.
        
        @param multi_paths=False: if set to True it will return a list of all
               the user selected paths, otherwise a single string path.
        @return: The chosen file path, a list of paths or false if the user 
                 cancelled.
        '''

        # Check that we have a database
        if self.settings.cur_log_path == '' or self.settings.cur_log_path == False:
            QtGui.QMessageBox.warning(self, "No Database Loaded",
                "No log database active. Please load or create one from" +
                                                    " the file menu.")
            logger.error('No log database found. Load or create one from File menu')
            return            

        # Create a file dialog with an initial path based on the availability
        # of path variables.
        d = MyFileDialogs()
        if not self.settings.last_model_directory == '' and not self.settings.last_model_directory == False:
            chosen_path = self.settings.last_model_directory
        elif not self.settings.cur_log_path == ''  and not self.settings.cur_log_path == False:
            chosen_path = self.settings.cur_log_path
        else:
            chosen_path = self.settings.cur_settings_path
            
        if multi_paths:
            open_path = d.openFileDialog(path=chosen_path, 
                    file_types='ISIS/TUFLOW (*.ief *.IEF *.tcf *.TCF)',
                    multi_file=True)
        else:
            open_path = d.openFileDialog(path=chosen_path, 
                    file_types='ISIS/TUFLOW (*.ief *.IEF *.tcf *.TCF)')
            
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
                
                log_pages, result = self._fetchAndCheckModel(open_path, log_type)
    
                if result['Success'] == False:
                    QtGui.QMessageBox.warning(self, result['Error'],
                    result['Message'])
                    self.ui.statusbar.showMessage(result['Status_bar'])
                else:
                    self.ui.statusbar.showMessage(result['Status_bar'])
                    self._fillEntryTables(log_pages)
                    self.ui.submitSingleModelGroup.setEnabled(True) 


    def _fetchAndCheckModel(self, open_path, log_type, launch_error=True):
        '''Loads a model and makes a few conditional checks on it.
        Loads model from the given .tcf/.ief file and checks that the .ief, 
        .tcf and ISIS results don't already exist in the DB and then returns
        a success or fail status.
        
        @param open_path: the .ief or .tcf file path.
        @param log_type: the model type to load (tuflow or ISIS only).
        @param lauch_error=True: whether to launch message boxes if an error is
               found or not. We don't want to if we're loading multiple files.
        @return: tuple containing log_pages (which could be the loaded log
                 pages or False if the load failed and a dictionary containing
                 the load status and messages for status bars and errors.
        '''
                
        # Load the model at the chosen path.
        log_pages = LogBuilder.loadModel(open_path, log_type)
        if log_pages == False:
            if launch_error:
                QtGui.QMessageBox.warning(self, "Load Error",
                "Unable to load model from file at: %s." % open_path)
                self.ui.statusbar.showMessage("Unable to load model at: " + open_path)
            else:
                return log_pages, {'Success': False, 
                        'Status_bar': "Unable to load model at: %s" % open_path,
                         'Error': 'LoadError', 
                        'Message': 'Selected file could not be loaded - file: %s.' % found_path}
        else:
            # Make sure that this ief or tcf do not already exist in the
            # database. You need new ones for each run so this isn't
            # allowed.
            main_ief = log_pages['RUN']['IEF']
            main_tcf = log_pages['RUN']['TCF']
            tcf_results = log_pages['RUN']['RESULTS_LOCATION_2D']
            indb = (False,)
            found_path = ''
            
            # If we have an ief get the ief name to see if we already
            # recorded a run using that model
            if not main_ief == 'None':
                indb = DatabaseFunctions.findInDatabase(
                         'RUN', db_path=self.settings.cur_log_path, 
                         db_entry=main_ief, col_name='IEF', 
                         only_col_name=True)
                
                # Then check if we've already used the results locations
                # location for a previous run and see if the user wants
                # to continue if we have.
                if indb[0]:
                    exists = DatabaseFunctions.findInDatabase(
                             'RUN', db_path=self.settings.cur_log_path, 
                             db_entry=tcf_results, col_name='RESULTS_LOCATION_1D', 
                             only_col_name=True)
                    
                    if exists[0]:
                        button = QtGui.QMessageBox.question(self, 
                                "ISIS/FMP Results Folder Already Exists",
                                "Results folder location found in previous " +
                                "entry\nDo you want to Continue?",
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                        
                        if button == QtGui.QMessageBox.No:
                            return
                    
                found_path = main_ief
            
            # Do the whole lot again for the tuflow run
            if not main_tcf == 'None':
                if not indb[0]:
                    indb = DatabaseFunctions.findInDatabase(
                             'RUN', db_path=self.settings.cur_log_path, 
                             db_entry=main_tcf, col_name='TCF', 
                             only_col_name=True)
                    found_path = main_tcf
                        
            if indb[0]:
                return log_pages, {'Success': False, 
                        'Status_bar': "Unable to load model at: %s" % open_path,
                         'Error': 'LoadError', 
                        'Message': 'Selected file already exists in database - file: %s.' % found_path}
            else:
                return log_pages, {'Success': True, 
                        'Status_bar': "Loaded model at: %s" % open_path,
                         'Error': None, 
                        'Message': None}



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

