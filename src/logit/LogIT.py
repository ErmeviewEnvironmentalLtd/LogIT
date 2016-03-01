"""
##############################################################################
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
 
 
  Module:          logit.py
  Date:            16/11/2014
  Author:          Duncan Runnacles
  Since-Version:   0.1
  
  Summary:
     Main file and GUI for the LogIT software. Deals with all interactions with
     the user through the interface and updates the GUI.
 
  UPDATES:
     DR - 19/11/2014:
         Changed logging procedure so that it is now possible to log an ISIS
         only model without a Tuflow component.
     DR - 03/12/2015:
         Cleaned out a lot of non GUI related code from here and refeactored
         a lot of the methods. It's still quite big, but a lot neater and
         more focused on dealing with the UI.
     DR - 13/12/2015:
         Lots more refactoring. The MainGui now uses some new classes to better
         handle the data. These include TableHolder, ErrorHolder, and 
         AllLogs. 
         The last bits of direct DatabaseFunctions.py calls have been
         removed.
         There is no longer and updating of the UI tables. A call to reload
         the database is made instead. This simplifies, and in a lot cases,
         speeds up the refresh.
         The RUN page now has a "Delete associated Entries" menu item for 
         deleting all of the entires associated with that run.
    DR - 29/02/16:
         Added CopyLogsToClipboard to File menu. Allows for automatic zipping
         up of log files and copying to system clipboard.
         Added drag and drop extensions to files in multiple model file
         selection table.
         Added update multiple rows to view tables context menu.

  TODO:
     
############################################################################## 
"""

# Python standard modules
import os
from os.path import basename
import sys
import cPickle
import sqlite3
import logging
import zipfile
 
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
import GuiStore


class MainGui(QtGui.QMainWindow):
    """Main GUI application window for the PysisTools software.
    """
     
    def __init__(self, cur_settings, cur_settings_path, parent = None):
        """Constructor.
        :param parent: Reference to the calling class.
        """        
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
                                'TUFLOW_BUILD', 'AMENDMENTS', 'RUN_OPTIONS']
        
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

        # Setup a custom QTableWidget for multiple model choice table so that
        # It can be drag and dropped into order
        self.ui.horizontalLayout_5.removeItem(self.ui.verticalLayout_21)
        self.ui.loadMultiModelTable = GuiStore.TableWidgetDragRows(0, 2, self)
        self.ui.loadMultiModelTable.setHorizontalHeaderLabels(['File name', 'Abs Path'])
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.ui.loadMultiModelTable.setHorizontalHeaderItem(0, item)
        item.setText("TCF / IEF File Name")
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.ui.loadMultiModelTable.setHorizontalHeaderItem(1, item)
        item.setText("Absolute Path")
        self.ui.loadMultiModelTable.horizontalHeader().setDefaultSectionSize(350)
        self.ui.loadMultiModelTable.horizontalHeader().setMinimumSectionSize(350)
        self.ui.loadMultiModelTable.horizontalHeader().setStretchLastSection(True)
        self.ui.loadMultiModelTable.setStyleSheet('QTableWidget {background-color: rgb(255, 255, 255);}')
        self.ui.loadMultiModelTable.setSortingEnabled(True)
        self.ui.horizontalLayout_5.addWidget(self.ui.loadMultiModelTable)
        self.ui.horizontalLayout_5.addItem(self.ui.verticalLayout_21)

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
        self.ui.actionCopyLogsToClipboard.triggered.connect(self._copyLogs)
        
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
        self.ui.runEntryViewTable.cellChanged.connect(self._highlightEditRow)
        self.ui.tgcEntryViewTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tgcEntryViewTable.customContextMenuRequested.connect(self._tablePopup)
        self.ui.tgcEntryViewTable.itemChanged.connect(self._highlightEditRow)
        self.ui.tbcEntryViewTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tbcEntryViewTable.customContextMenuRequested.connect(self._tablePopup)
        self.ui.tbcEntryViewTable.itemChanged.connect(self._highlightEditRow)
        self.ui.datEntryViewTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.datEntryViewTable.customContextMenuRequested.connect(self._tablePopup)
        self.ui.datEntryViewTable.itemChanged.connect(self._highlightEditRow)
        self.ui.bcEntryViewTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.bcEntryViewTable.customContextMenuRequested.connect(self._tablePopup)
        self.ui.bcEntryViewTable.itemChanged.connect(self._highlightEditRow)
        self.ui.ecfEntryViewTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.ecfEntryViewTable.customContextMenuRequested.connect(self._tablePopup)
        self.ui.ecfEntryViewTable.itemChanged.connect(self._highlightEditRow)
        self.ui.tcfEntryViewTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tcfEntryViewTable.customContextMenuRequested.connect(self._tablePopup)
        self.ui.tcfEntryViewTable.itemChanged.connect(self._highlightEditRow)
        
        # Custom quit function
        #self.app.aboutToQuit.connect(self._customClose)
        
        # Load the user settings from the last time the software was used 
        self._loadSettings()
        
        self._setupUiContainer()
        
        # Use those settings to get the file path and try and load the last log
        # database that the user had open
        self.loadModelLog()
        self.all_logs = None
        
        self.setWindowIcon(QtGui.QIcon(':Logit_Logo2_25x25.png'))
        
        # Activate the GUI
        MainGui.show()
        sys.exit(self.app.exec_())
        
    
    def _setupUiContainer(self):
        """Create a convenient holding object for the gui inputs.
        """
        
        self.new_entry_tables = GuiStore.TableHolder(GuiStore.TableHolder.NEW_LOG)
        self.new_entry_tables.addTable(GuiStore.TableWidget('RUN', 
                                    'runEntryTable', self.ui.runEntryTable))
        self.new_entry_tables.addTable(GuiStore.TableWidget('TCF', 
                                    'tcfEntryTable', self.ui.tcfEntryTable))
        self.new_entry_tables.addTable(GuiStore.TableWidget('ECF', 
                                    'ecfEntryTable', self.ui.ecfEntryTable))
        self.new_entry_tables.addTable(GuiStore.TableWidget('TGC', 
                                    'tgcEntryTable', self.ui.tgcEntryTable))
        self.new_entry_tables.addTable(GuiStore.TableWidget('TBC', 
                                    'tbcEntryTable', self.ui.tbcEntryTable))
        self.new_entry_tables.addTable(GuiStore.TableWidget('BC_DBASE', 
                                    'bcEntryTable', self.ui.bcEntryTable))
        self.new_entry_tables.addTable(GuiStore.TableWidget('DAT', 
                                    'datEntryTable', self.ui.datEntryTable))
        
        self.view_tables = GuiStore.TableHolder(GuiStore.TableHolder.VIEW_LOG)
        self.view_tables.addTable(GuiStore.TableWidget('RUN', 
                            'runEntryViewTable', self.ui.runEntryViewTable))
        self.view_tables.addTable(GuiStore.TableWidget('TCF', 
                            'tcfEntryViewTable', self.ui.tcfEntryViewTable))
        self.view_tables.addTable(GuiStore.TableWidget('ECF', 
                            'ecfEntryViewTable', self.ui.ecfEntryViewTable))
        self.view_tables.addTable(GuiStore.TableWidget('TGC', 
                            'tgcEntryViewTable', self.ui.tgcEntryViewTable))
        self.view_tables.addTable(GuiStore.TableWidget('TBC', 
                            'tbcEntryViewTable', self.ui.tbcEntryViewTable))
        self.view_tables.addTable(GuiStore.TableWidget('BC_DBASE', 
                            'bcEntryViewTable', self.ui.bcEntryViewTable))
        self.view_tables.addTable(GuiStore.TableWidget('DAT', 
                            'datEntryViewTable', self.ui.datEntryViewTable))
    
    
    def _highlightEditRow(self):
        """
        """
        sender = self.sender()
        s_name = str(sender.objectName())
        item = sender.currentItem()
        if not item is None:
            item.setBackgroundColor(QtGui.QColor(178, 255, 102)) # Light Green
        
     
    
    def _updateLoggingLevel(self):
        """Alters to logging level based on the name of the calling action
        
        This is set by an action on the menu.
        """
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
        """Clears the error outputs in multi model load error textbox.
        """
        self.ui.multiModelLoadErrorTextEdit.clear()
    
    
    def _copyToClipboard(self):
        """Copies the contents of a textbox to clipboard.
        Textbox to copy is based on the calling action name.
        """
        caller = self.sender()
        call_name = caller.objectName()
        
        if call_name == 'multiModelErrorCopyButton':
            text = self.ui.multiModelLoadErrorTextEdit.toPlainText()
        
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(text)
            event = QtCore.QEvent(QtCore.QEvent.Clipboard)
            self.app.sendEvent(clipboard, event)
        
    
    def _updateMultipleLogSelection(self):
        """Updates the contents of the loadMultiModelListView.
        Called by both the add and remove buttons. It will open a multiple
        choice file dialog by the former or remove the selected items by the
        latter.
        """
        caller = self.sender()
        call_name = caller.objectName()
        logger.debug('Caller = ' + call_name)
        
        # Add a new file
        if call_name == 'addMultiModelButton':
            open_paths = self._getModelFileDialog(multi_paths=True)
            if open_paths == False:
                return
            
#             paths = [str(x) for x in open_paths]
#             paths.reverse()
            
            row_count = self.ui.loadMultiModelTable.rowCount()
            for p in open_paths:
                
                # Insert a new row first if needed
                self.ui.loadMultiModelTable.insertRow(row_count)
                
                # Get the filename
                d, fname = os.path.split(str(p))
                self.settings.last_model_directory = d
                
                # Create a couple of items and add to the table
                self.ui.loadMultiModelTable.setItem(row_count, 0, 
                                        Controller.createQtTableItem(fname, drag_enabled=True))
                self.ui.loadMultiModelTable.setItem(row_count, 1, 
                                        Controller.createQtTableItem(p, drag_enabled=True))
                
            # Set the sumbit button to enabled
            self.ui.submitMultiModelGroup.setEnabled(True)
            self.ui.loadMultiModelTable.sortItems(0,  QtCore.Qt.AscendingOrder)
            self.ui.loadMultiModelTable.setSortingEnabled(False)
                
            
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
        """This is the action performed when the user opens the context menu
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
        
        :param pos: the QPoint of the mouse cursor when clicked.
        """
        menu = QtGui.QMenu()
        updateRowAction = menu.addAction("Update Row")
        updateMultipleRowAction = menu.addAction("Update Multiple Rows")
        deleteRowAction = menu.addAction("Delete Row")
        
        # Find who called us and get the object that the name refers to.
        sender = self.sender()
        sender = str(sender.objectName())
        has_delall = False
        if sender == self.view_tables.tables['RUN'].name:
            deleteAllRowAction = menu.addAction("Delete Associated Entries")
            has_delall = True
        
        # lookup the table and database table name
        table_obj = self.view_tables.getTable(name=sender)
        
        # Get the action and do whatever it says
        action = menu.exec_(table_obj.ref.viewport().mapToGlobal(pos))
        if action == updateRowAction:
            self._saveViewChangesToDatabase(table_obj)
            self.loadModelLog()               
            
        if action == updateMultipleRowAction:
            
            # Get a list of selected ranges and loop from top row to bottom
            sel_range = table_obj.ref.selectedRanges()
            for sel in sel_range:
                top_row = sel.topRow()
                bottom_row = sel.bottomRow()
                
                # Save row contents to database
                for row in range(top_row, bottom_row+1):
                    self._saveViewChangesToDatabase(table_obj, row)
                    logger.info('Updating row no: ' + str(row+1))
            self.loadModelLog()               
        
        elif action == deleteRowAction:
            self._deleteRowFromDatabase(table_obj, False)
        
        elif has_delall and action == deleteAllRowAction:
            self._deleteRowFromDatabase(table_obj, True)
            
    
    def _deleteRowFromDatabase(self, table, all_entry):
        """Deletes the row in the database based on the location that the mouse
        was last clicked.
        This is fine because this function is called from the context menu and
        therefore relies on the user right-clicking on the correct row.
        
        :param table: the TableWidget item to get the row data from.
        """
        
        # Get the currently active row in the table and find it's ID value
        row = table.currentRow()
        row_dict = table.getValues(row=row, names=['ID'])
        
        # Just make sure we meant to do this
        if not all_entry:
            message = "Delete this row?\nTable = %s, Row ID = %s" % (table.name, row_dict['ID'])
        else:
            message = "Delete this row AND all assocated rows?\nTable = %s, Row ID = %s" % (table.name, row_dict['ID'])
        answer = self.launchQtQBox('Confirm Delete?', message)            
        if answer == False:
            return
        
        # Delete from database
        errors = GuiStore.ErrorHolder()
        errors = Controller.deleteDatabaseRow(self.settings.cur_log_path,
                                table.key, row_dict['ID'], errors, all_entry)
        # and then from the table
        if errors.has_errors:
            self.launchQMsgBox(errors.msgbox_error.title, 
                               errors.msgbox_error.message)
            logger.error('Failed to delete row(s)')
        else:
            self.loadModelLog()
            logger.info('Row ID=%s deleted successfully' % (row_dict['ID']))
    
    
    def _saveViewChangesToDatabase(self, table, row=None):
        """Saves the edits made to the row in the View Log table to the database
        based on the id value in the row that was clicked to launch the context
        menu.
        
        :param table: the table in the user form to takes  updates from.
        """
        if row is None:
            row = table.currentRow()
        
        # Search through the current row and get the values in the columns that
        # we are going to allow the user to update.
        save_dict = table.getValues(row=row, names='*')
        id_key = save_dict['ID']
        
        # Add the updates to the database
        errors = GuiStore.ErrorHolder()
        errors = Controller.editDatabaseRow(self.settings.cur_log_path, 
                                        table.key, id_key, save_dict, errors)
        
        db_path = os.path.split(self.settings.cur_log_path)[0]
        if errors.has_errors:
            logger.error('Row ID=%s failed to update' % (id_key))
            self.launchQMsgBox(errors.msgbox_error.title, 
                               errors.msgbox_error.message)
        else:
            logger.info('Row ID=%s updated successfully' % (id_key))
            self.ui.statusbar.showMessage(
                                "Log entry (Table=%s : ID=%s) has been"
                                " updated" % (table.key, id_key))
                
        
    def loadModelLog(self):
        """If there is a model log to load we do it.
        """
        if self.checkDbLoaded(False):
            errors = GuiStore.ErrorHolder()
            # Check that the database actually exists. If not get out of here.
            if not os.path.exists(self.settings.cur_log_path):
                logger.info('No existing log database to load')
                self.settings.cur_log_path = ''
                return
            
            errors = Controller.checkDatabaseVersion(
                                        self.settings.cur_log_path, errors)
            if errors.has_errors:
                self.launchQMsgBox(errors.msgbox_error.title,
                                                errors.msgbox_error.message)
                return
            
            self.view_tables.clearAll()
             
            # load each of the tables from the database
            table_list = []
            for table in self.view_tables.tables.values():
                table_list.append([table.key, table.name])
            
            entries, errors = Controller.fetchTableValues(
                            self.settings.cur_log_path, table_list, errors)
            
            if errors.has_errors:
                self.launchQMsgBox(errors.msgbox_error.title,
                                                errors.msgbox_error.msg) 
                return
             
            # Add the results to the database tables
            for entry in entries:
                if entry[2]:
                    table = self.view_tables.getTable(name=entry[1])
                    table.ref.setRowCount(entry[3])
                    table.addRows(entry[4], 0)
            

    def _fillEntryTables(self, all_logs):
        """Add the log pages data to the log entry tables that will be
        displayed to the user for amending prior to updating the database.
        
        :param log_pages: the log pages dictionary loaded from the model.
        """
        # Reset the tables first
        self.new_entry_tables.clearAll()
        
        self.all_logs = self._getInputLogVariables(all_logs)
        
        # Create a list of all of the available tables and their names
        table_list = []
        for table in self.new_entry_tables.tables.values():
            if table.key == 'RUN': continue
            table_list.append([table.key, table.name])
        
        # Update RUN seperately as it's treated in a different way to others
        self.new_entry_tables.tables['RUN'].addRowValues(
                                            all_logs.getLogEntryContents('RUN', 0)) 
        self.new_entry_tables.tables['RUN'].setEditColors(0)
        
        # check the new entries against the database and return them with
        # flags set for whether they are new entries or already exist
        errors = GuiStore.ErrorHolder()
        entries, errors = Controller.loadEntrysWithStatus(
                self.settings.cur_log_path, self.all_logs, table_list, errors)
        
        # Add the entries to the gui tables with editable status set
        for entry in entries:
            table = self.new_entry_tables.getTable(name=entry[1])
            table.addRowValues(entry[0], entry[2])
            table.setEditColors(entry[2], entry[3])

    
    def _getInputLogVariables(self, all_logs):
        """Put the variables entered by the user in the Input log variables
        group into the all_logs object.
        """
        run = all_logs.getLogEntryContents('RUN', 0)
        run['MODELLER'] = str(self.ui.modellerTextbox.text())
        run['TUFLOW_BUILD'] = str(self.ui.tuflowVersionTextbox.text())
        run['ISIS_BUILD'] = str(self.ui.isisVersionTextbox.text())
        run['EVENT_NAME'] = str(self.ui.eventNameTextbox.text())
        
        return all_logs
        
        
    def _createLogEntry(self):
        """Take the updated data in the provisional table and load it into the
        model log.
        """
        # Check that we have a database
        if not self.checkDbLoaded(): return

        if not self.all_logs == None:
            
            self._updateWithUserInputs()
            
            errors = GuiStore.ErrorHolder()
            errors, self.all_logs = Controller.updateLog(
                        self.settings.cur_log_path, self.all_logs, errors) # DEBUG , check_new_entries=True
            
            if errors.has_errors:
                self.launchQMsgBox(errors.msgbox_error.title, 
                                        errors.msgbox_error.message)
                del errors
                return
            
            # Add the new entries to the view table as well
            self.loadModelLog()
            
            # Clear the entry rows and deactivate add new log button
            self.new_entry_tables.clearAll()
            self.ui.submitSingleModelGroup.setEnabled(False)
            
            # Update the status bar message
            self.ui.statusbar.showMessage("Log Database successfully updated")
            logger.info('Log Database successfully updated')
            del errors
            
    
    def _createMultipleLogEntry(self):
        """Takes all the files in the multiple model list, load them and add
        them to the database.        
        """
            
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
        errors = GuiStore.ErrorHolder()
        
        # Setup the progress monitor. It updates prgress bars etc
        total = len(model_paths)
        prog_mon = ProgressMonitor(self.ui.multiLoadProgressBar, 
                                   self.ui.multiLoadProgressLabel)
        prog_mon.setRanges(total*2, 1, total, 'Loading Model %d or %d')
        
        # Loop through all of the file paths given
        for path in model_paths:
            error_found = False
            
            prog_mon.update()
            
            errors, all_logs = Controller.fetchAndCheckModel(
                       self.settings.cur_log_path, path, log_type, 
                            errors)
            
            # Go to next if we find an error
            if errors.has_local_errors:
                continue
            
            prog_mon.update(bar_only=True)
            
            # Get the global user supplied log variables
            all_logs = self._getInputLogVariables(all_logs)

            # Update the log entries
            errors, self.all_logs = Controller.updateLog(
                                self.settings.cur_log_path, all_logs, 
                                errors, check_new_entries=True)
            
            if errors.has_local_errors:
                errors.has_local_errors = False
                continue
            
        self.loadModelLog()

        # Clear the list entries
        self.ui.loadMultiModelTable.setRowCount(0)
        if errors.has_errors:
            prog_mon.reset('Complete')
            text = errors.formatErrors('Some models could not be logged:')
            self.ui.multiModelLoadErrorTextEdit.setText(text)
            QtGui.QMessageBox.warning(self, 'Logging Error:',
                            'See Error Logs window for details')
        else:
            logger.info('Log Database updated successfully')
            self.ui.statusbar.showMessage("Log Database successfully updated")
            prog_mon.reset('Complete')
        
    
    def _updateWithUserInputs(self):
        """Get the variables that we want to allow the user to be able to update.
        """
        for log in self.all_logs.log_pages.values():
            if not log.has_contents: 
                continue
            
            for i, row in enumerate(log.contents, 1):
                table_row = self.new_entry_tables.tables[log.name].getValues(i)

                for key, entry in table_row.iteritems():
                    row[key] = entry
        

    def _loadSettings(self):
        """Get the settings loaded from file if they exist.
        """
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
        """Need a custom close event so that we can save the user settings.
        """            
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
        """Write the current LogIT setup to file.
        """
        d = MyFileDialogs()
        save_path = d.saveFileDialog(path=os.path.split(
                            self.settings.cur_log_path)[0], 
                            file_types='Log Settings (*.logset)')
        
        if save_path == False:
            return
        self._writeSettings(str(save_path))
        
    
    def _loadSetup(self):
        """Load LogIT setup from file.
        """
        errors = GuiStore.ErrorHolder()
        settings, errors = Controller.loadSetup(
                                        self.settings.cur_settings_path, 
                                        self.settings.cur_log_path,
                                        errors)
         
        if settings == None:
            if errors.has_errors:
                QtGui.QMessageBox.warning(self, errors.msgbox_error.title, 
                                                error.msgbox_error.message)
            return
        else:
            self.settings = settings
            self._loadSettings()
        
    
    def _customClose(self):
        """Do the things that need doing before closing window.
        """
        save_path = self.settings.cur_settings_path
        self._writeSettings(save_path)
        # We need sys.exit because otherwise this function will be called twice.
        #self.app.quit()
        sys.exit()            

 
    def _updateDatabaseVersion(self): 
        """Checks if the databse at the given path is compatible with the
        latest version of LogIT.
        """
        d = MyFileDialogs()
        if not self.checkDbLoaded():
            open_path = str(d.openFileDialog(path=self.settings.cur_log_path, 
                                        file_types='LogIT database(*.logdb)'))
        else:
            open_path = str(d.openFileDialog(path=self.settings.cur_settings_path, 
                                        file_types='LogIT database(*.logdb)'))
        # User cancel return
        if open_path == False:
            return None
        errors = GuiStore.ErrorHolder()
        errors = Controller.updateDatabaseVersion(open_path, errors)
        if errors.has_errors:
            self.launchQMsgBox(errors.msgbox_error.title, 
                                            errors.msgbox_error.message)
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
                    self.launchQMsgBox(errors.types[errors.DB_UPDATE].title, 
                                       errors.types[errors.DB_UPDATE].message)
                    self.settings.cur_log_path = temp
    
    
    def _createNewLogDatabase(self):
        """Create a new model log database.
        """
        d = MyFileDialogs()
        save_path = d.saveFileDialog(path=os.path.split(
                                    self.settings.cur_settings_path)[0], 
                                     file_types='LogIT database(*.logdb)')
        
        if not save_path == False:
            self.settings.cur_log_path = str(save_path)
            self.new_entry_tables.clearAll()
            self.view_tables.clearAll()
            self.ui.statusbar.showMessage('Building new log database...')
            self.ui.centralwidget.setEnabled(False)
            DatabaseFunctions.createNewLogDatabase(str(save_path))
            self.ui.centralwidget.setEnabled(True)
            self.ui.statusbar.showMessage("Current log: " + save_path)
    
    
    def _loadDatabaseFromUser(self):
        """Load database chosen by user in dialog.
        """
        d = MyFileDialogs()
        if not self.checkDbLoaded(False):
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
        """Exports the database based on calling action.
        """
        if self.checkDbLoaded():
            d = MyFileDialogs()
            save_path = d.saveFileDialog(path=os.path.split(
                                        self.settings.cur_log_path)[0], 
                                        file_types='Excel File (*.xls)')
            if save_path == False:
                return

            save_path = str(save_path)
            errors = GuiStore.ErrorHolder()
            errors = Controller.exportToExcel(self.settings.cur_log_path, 
                                              self.export_tables, save_path,
                                                                    errors)
            
            if errors.has_errors:
                self.launchQMsgBox(errors.msgbox_error.title, 
                                   errors.msgbox_error.message)
                self.ui.statusbar.showMessage(errors.msgbox_error.status_bar)
            else:
                self.launchQMsgBox('Export Complete', 
                    'Database exported to Excel (.xls) at:\n%s' % (save_path), 
                                                                    'info')
                self.ui.statusbar.showMessage('Database exported to Excel')
                
        else:
            logger.warning('Cannot export log - no database loaded')
            QtGui.QMessageBox.warning(self, "Cannot Export Log",
                                      "There is no log database loaded")
        

    def fileMenuActions(self):
        """Respond to actions that occur on the file menu
        """
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
        """Launches an open file dialog to get .ief or .tcf files.
        
        :param multi_paths=False: if set to True it will return a list of all
               the user selected paths, otherwise a single string path.
        :return: The chosen file path, a list of paths or false if the user 
                 cancelled.
        """

        # Check that we have a database
        if not self.checkDbLoaded():
            QtGui.QMessageBox.warning(self, "No Database Loaded",
                "No log database active. Please load or create one from" +
                                                    " the file menu.")
            logger.error('No log database found. Load or create one from File menu')
            return            

        open_path = GuiStore.getModelFileLocation(multi_paths,
            self.settings.last_model_directory, self.settings.cur_log_path,
                self.settings.cur_settings_path)
        
        return open_path
    
          
    def _loadFileActions(self, shortcut=None):
        """Respond to the user clicking a button that loads a file.
        """
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
                
                errors = GuiStore.ErrorHolder()
                errors, all_logs = Controller.fetchAndCheckModel(self.settings.cur_log_path, open_path, log_type, errors)
    
                if errors.has_errors:
                    self.launchQMsgBox(errors.msgbox_error.title, 
                                       errors.msgbox_error.message)
                    self.ui.statusbar.showMessage(errors.msgbox_error.status_bar)
                else:
                    self.ui.statusbar.showMessage('Loaded model at: %s' % open_path)
                    self._fillEntryTables(all_logs)
                    self.ui.submitSingleModelGroup.setEnabled(True) 


    def launchQtQBox(self, title, message):
        """Launch QtQMessageBox.
        """
        answer = QtGui.QMessageBox.question(self, title, message,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if answer == QtGui.QMessageBox.No:
            return False
        else:
            return answer
    
    
    def launchQMsgBox(self, title, message, type='warning'):
        """Launch a QMessageBox
        """
        if type == 'warning':
            QtGui.QMessageBox.warning(self, title, message)
        
        elif type == 'info':
            QtGui.QMessageBox.information(self, title, message)
    
    
    def checkDbLoaded(self, show_dialog=True):
        """Check if there's a database filepath set.
        """
        if self.settings.cur_log_path == '' or self.settings.cur_log_path == False:
            if show_dialog:
                QtGui.QMessageBox.warning(self, "No Database Loaded",
                        "No log database active. Please load or create one from the file menu.")
            logger.error('No log database found. Load or create one from File menu')
            return False
        return True
    
    
    def _copyLogs(self):
        """Zip up all of the log file and copy them to the system clipbaord.
        """
        zip_log = os.path.join(log_path, '..', 'logs.zip')
        
        # Remove any existing zip file
        if os.path.exists(zip_log):
            try:
                os.remove(zip_log)
            except:
                logger.warning('Unable to delete existing log zip file')
        
        # Create a zipfile handler
        zipper = zipfile.ZipFile(zip_log, 'w', zipfile.ZIP_DEFLATED)
        
        # Grab all of the log files into it
        for roots, dir, files in os.walk(log_path):
            for f in files:
                write_path = os.path.join(log_path, f)
                zipper.write(write_path, basename(write_path))
        zipper.close()
        
        # Copy the logs zip file to clipboard
        data = QtCore.QMimeData()
        url = QtCore.QUrl.fromLocalFile(zip_log)
        data.setUrls([url])
        self.app.clipboard().setMimeData(data)
        

class ProgressMonitor(object):
    """Convenience class for updating progress bars and text.
    
    This stays in this module becuase it sort of breaks the encapsulation of
    the MainGui class by updating its progress bar and text label. It's better
    than having to little progress update code all over the place though.
    """
     
    def __init__(self, progbar_ui, text_ui=None):
        self.progbar_ui = progbar_ui
        self.text_ui = text_ui
        self.prog_cur = 0
        self.text_cur = 0
    
    def setRanges(self, prog_up, text_down=None, text_up=None, textform='%d of %d'): 
        """Set the range to operate on.
        :param prog_up: max progress bar value.
        :param text_down=None: lowest text counter value.
        :param text_up=None: max text counter value.
        :param textform=None: format to dislplay text counter in.
        """
        self.prog_up = prog_up
        self.text_up = text_up
        self.text_current = self.text_down = text_down
        self.textform = textform
        self.progbar_ui.setRange(0, prog_up)
        self.setToStart()
    
    def setToStart(self):
        """Set progress counters to start point.
        """
        self.progbar_ui.setValue(0)
        if not self.text_ui == None:
            text_out = self.textform % (self.text_cur, self.text_up)
            self.text_ui.setText(text_out)
    
    def reset(self, text=None):
        """Reset the progress bar to normal state.
        :param text=None: text to display in text label.
        """
        self.setToStart()
        if text == None: text = ''
        self.text_ui.setText(text)
    
    def update(self, bar_only=False, text_only=False):
        """Update progress.
        :param bar_only=False: don't update the progress bar.
        :param text_only=False: don't update the text counter.
        """
        if not text_only:
            self.updateBarProgress()
        if not bar_only:
            self.updateTextProgress()
        QtGui.QApplication.processEvents()
    
    def updateBarProgress(self):
        """Iterate and update progress bar
        """
        self.prog_cur += 1
        self.progbar_ui.setValue(self.prog_cur)
    
    def updateTextProgress(self):
        """Iterate and update text counter label.
        """
        if self.text_ui == None:
            return
        else:
            self.text_cur += 1
            text_out = self.textform % (self.text_cur, self.text_up)
            self.text_ui.setText(text_out)


class LogitSettings(object):
    """Storage class for holding all of the settings that the current user has
    stored.
    """
    
    def __init__(self):
        """Constructor.
        """
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
    myappid = 'logit.0-4-Beta'
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

