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
         Added ModelExtractor widget and module code.
         Added progress bar to status bar and removed from multiple load.
         Added load/save widget (tools) functionality.
    DR - 09/03/2016:
         Added app_metrics module to track tool usage.
         Added update check menu item and autoinstall.
    DR - 13/03/2016:
         Updated version checker to use globalsettings version variables.
    DR - 05/04/2016:
         Removed log_type and selection combo box from interface. This is no
         longer needed because the loader accepts any type of model file.
    DR - 14/04/2016:
         Moved the new entry tab into a separate widget.
    DR - 28/04/2016:
         Changed the way settings work to now use a combination of the 
         LogitSettings class some global path variables (stored in 
         globalsettings.py) and dictionaries for the other tools rather than
         ToolSettings.
         Updated Keyboard shortcuts and fixed a few.
         Added Run Summary widget, cleaned up the class and moved most of the
         zip up and copy logs stuff into Controller.py.
         Added LOG_DIR, RUN_STATUS and MB to run table and added update Run
         Status to context and settings menu. Also added Add to Run Summary
         option to context menu.

  TODO:
     
############################################################################## 
"""

# Python standard modules
import os
import sys
import cPickle
import logging

# Stupid imports to make pyinstaller work with pyqtgraph
import six
import packaging
import packaging.version
import packaging.specifiers
import packaging.requirements
 
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
logger.debug('SQLite3 import complete')

# Fetch the ship library   
try:
    from ship.utils.qtclasses import MyFileDialogs
except:
    logger.error('Cannot load ship (Is it installed?)')
 
# Have to import PyQt4 like this or it won't compile into an .exe
try:
    from PyQt4 import QtCore, QtGui
except:
    logger.error('Cannot import PyQt4 is it installed?')
 
# LogIT specific modules.
logger.debug('Start of Logit imports')
from LogIT_UI import Ui_MainWindow
logger.debug('Main Window import complete')
import LogBuilder
logger.debug('LogBuilder import complete')
import DatabaseFunctions
logger.debug('Database functions import complete')
import Exporters
logger.debug('Exporters import complete')
import Controller
logger.debug('Controller import complete')
import GuiStore
logger.debug('GuiStore import complete')
import IefResolver
logger.debug('Ief Resolver import complete')
import globalsettings as gs
logger.debug('Global Settings import complete')
from newentry import NewEntry
logger.debug('New Entry import complete')
from extractmodel import ModelExtractor
logger.debug('Extract Model import complete')
from runsummary import RunSummary
logger.debug('Run Summary import complete')
logger.debug('Import modules complete')


class MainGui(QtGui.QMainWindow):
    """Main GUI application window for the PysisTools software.
    """
     
    def __init__(self, cur_settings, parent=None):
        """Constructor.
        :param parent: Reference to the calling class.
        """        
        # Setup some variables
        self._TEST_MODE = False
        self.settings = cur_settings
        self.model_log = None
        
        # Database tables that should be exported to Excel
        self.export_tables = ['RUN', 'TCF', 'ECF', 'TGC', 'TBC', 'DAT', 'BC_DBASE']
            
        icon_path = os.path.join(self.settings.cur_settings_path, 'Logit_Logo.ico')
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow() # ~
        self.ui.setupUi(self)
        logger.debug('Setup UI complete')
        
        # Add a progress bar to the status bar
        self.progress_bar = QtGui.QProgressBar(self.ui.statusbar)
        self.progress_bar.setMaximumSize(200, 20)
        self.ui.statusbar.addPermanentWidget(self.progress_bar)
        self.progress_bar.setValue(0)

        # Connect the slots
        self.ui.actionLoad.triggered.connect(self.fileMenuActions)
        self.ui.actionExportToExcel.triggered.connect(self.fileMenuActions)
        self.ui.actionNewModelLog.triggered.connect(self.fileMenuActions)
        self.ui.actionUpdateDatabaseSchema.triggered.connect(self._updateDatabaseVersion)
        self.ui.actionSaveSetupAs.triggered.connect(self._saveSetup)
        self.ui.actionLoadSetup.triggered.connect(self._loadSetup)
        self.ui.actionLogWarning.triggered.connect(self._updateLoggingLevel)
        self.ui.actionLogDebug.triggered.connect(self._updateLoggingLevel)
        self.ui.actionLogInfo.triggered.connect(self._updateLoggingLevel)
        self.ui.actionReloadDatabase.triggered.connect(self.loadModelLog)
        self.ui.actionCopyLogsToClipboard.triggered.connect(self._copyLogs)
        self.ui.actionCheckForUpdates.triggered.connect(self._checkUpdatesTrue)
        self.ui.actionResolveIefFiles.triggered.connect(self._resolveIefs)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionUpdateAllRunStatus.triggered.connect(self._updateAllRowStatus)
        
        # Keyboard shortcuts
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
        # Zip up and copy logs
        self.ui.actionCopyLogsToClipboard.setToolTip('Zip up and copy log files to clipboard')
        self.ui.actionCopyLogsToClipboard.setShortcut("Ctrl+Z")
        # Reload log database
        self.ui.actionReloadDatabase.setToolTip('Reload the log database and tables')
        self.ui.actionReloadDatabase.setShortcut("Ctrl+R")
        # Run Ief resolver tool
        self.ui.actionResolveIefFiles.setToolTip('Run the Ief Resolver tool')
        self.ui.actionResolveIefFiles.setShortcut("Ctrl+I")
        # Update all Run status information
        self.ui.actionUpdateAllRunStatus.setToolTip('Update all run status information')
        self.ui.actionUpdateAllRunStatus.setShortcut("Ctrl+U")
        
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
        logger.debug('Slot connection complete')
        
        # Load the user settings from the last time the software was used 
        self._loadSettings()
        logger.debug('Load settings complete')
        self._setupUiContainer()
        logger.debug('Setup UIContainer complete')
        self._setColumnWidths()
        logger.debug('Set column widths complete')
        
        # Use those settings to get the file path and try and load the last log
        # database that the user had open
        self.loadModelLog()
        logger.debug('Attempt to laod model log complete')
        self.all_logs = None
        
        # Set default logging level if used in release
        if not gs.__DEV_MODE__:
            self.ui.actionLogWarning.setChecked(False)
            self.ui.actionLogDebug.setChecked(False)
            self.ui.actionLogInfo.setChecked(True)

            logging.getLogger().setLevel(logging.INFO)
            self.settings.logging_level = logging.INFO
            logger.info('Logging level set to: INFO')
            logger.debug('info set check')
        
        logger.debug('MainGui construction complete')

        
    def startupChecks(self):
        """Check for new versions and show release notes if needed."""
        self._showReleaseNotes()
        self._checkUpdatesFalse()
        
    
    def _setupUiContainer(self):
        """Create a convenient holding object for the gui inputs.
        """
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
        self._addWidgets()
    
    
    def _addWidgets(self):
        """Adds tool widgets to the tabbed interface."""
        self.widgets = {}
        
        # New Entry
        new_entry = NewEntry.NewEntry_UI(cur_location)
        self.widgets[new_entry.tool_name] = new_entry
        self.ui.tabWidget.insertTab(self.ui.tabWidget.count(), new_entry, new_entry.tool_name)
        self.widgets[new_entry.tool_name].addSingleLogEntryButton.clicked.connect(self._createLogEntry)
        self.widgets[new_entry.tool_name].addMultiLogEntryButton.clicked.connect(self._createMultipleLogEntry)
        # Update all Run status information
        self.widgets[new_entry.tool_name].addSingleLogEntryButton.setToolTip('Add model details to log database (Ctrl-A)')
        self.widgets[new_entry.tool_name].addSingleLogEntryButton.setShortcut("Ctrl+A")
        self.widgets[new_entry.tool_name].addMultiLogEntryButton.setToolTip('Add model details to log database (Alt-A)')
        self.widgets[new_entry.tool_name].addMultiLogEntryButton.setShortcut("Alt+A")
        
        
        # Model Extractor
        model_extractor = ModelExtractor.ModelExtractor_UI(cur_location)
        self.widgets[model_extractor.tool_name] = model_extractor
        self.ui.tabWidget.insertTab(self.ui.tabWidget.count(), model_extractor, model_extractor.tool_name)
        
        # Run Summary
        run_summary = RunSummary.RunSummary_UI(cur_location) 
        self.widgets[run_summary.tool_name] = run_summary
        self.ui.tabWidget.insertTab(self.ui.tabWidget.count(), run_summary, run_summary.tool_name)
        
        # Connect slots and load the settings.
        for w in self.widgets.values():
            try:
                self.connect(w, QtCore.SIGNAL("statusUpdate"), self._updateStatusBar)
                self.connect(w, QtCore.SIGNAL("setRange"), self._updateMaxProgress)
                self.connect(w, QtCore.SIGNAL("updateProgress"), self._updateCurrentProgress)
            except:
                logger.warning('Unable to connect slots for %s' % (w.tool_name))
            
            try:
                w.loadSettings(self.settings.tool_settings[w.tool_name])
            except:
                logger.info('No loadSettings() found for %s' % (w.tool_name))

        # Do this here so it accounts for all the tabs
        self.ui.tabWidget.setCurrentIndex(self.settings.main['cur_tab'])
    
    
    def _checkUpdatesFalse(self):
        self._checkUpdates(False)
        
    def _checkUpdatesTrue(self):
        self._checkUpdates(True)
        
    def _checkUpdates(self,  show_has_latest=True):     
        """Check if this is the latest version or not.
        
        If it isn't it gives the user the option to download and install the
        updated version.
        """        
        is_latest = Controller.checkVersionInfo(gs.__VERSION__, gs.__VERSION_CHECKPATH__)
        if is_latest[0]:
            logger.info('Latest version of LogIT (version %s) installed' % (gs.__VERSION__))
            if show_has_latest:
                msg = 'You have the latest version of LogIT'
                self.launchQMsgBox('Version Information', msg, 'info')
        else:
            msg = 'There is a new version (%s). Would you like to download it?' % (is_latest[1])
            download_filename = gs.__DOWNLOAD_FILENAME__ + is_latest[1]
            
            response = self.launchQtQBox('New version available', msg)
            if not response == False:
                success = Controller.downloadNewVersion(cur_location,
                                                        gs.__SERVER_PATH__,
                                                        download_filename)
                if not success:
                    msg = 'Failed to autoinstall new version. It can be downloaded from here:\n' + gs.__SERVER_PATH__
                    self.launchQMsgBox('Update Failure', msg)
                else:
                    msg = ('Download complete.\nYou can close this version ' +
                           'and launch the new one.\n' +
                           'This version can be deleted if you want.')
                    self.launchQMsgBox('Update Success', msg)
    
    
    def _highlightEditRow(self):
        """Highlightes the calling cell in the View Tables."""
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
            
        
    def _copyToClipboard(self):
        """Copies the contents of a textbox to clipboard.
        Textbox to copy is based on the calling action name.
        """
        caller = self.sender()
        call_name = caller.objectName()
        
    
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
        updateMultipleRowAction = menu.addAction("Update Row(s)")
        deleteRowAction = menu.addAction("Delete Row")
        
        # Find who called us and get the object that the name refers to.
        sender = self.sender()
        sender = str(sender.objectName())
        has_extras = False
        if sender == self.view_tables.tables['RUN'].name:
            deleteAllRowAction = menu.addAction("Delete Associated Entries")
            paths_menu = menu.addMenu('Update Paths')
            updateIefRowAction = paths_menu.addAction("Update Ief Location")
            updateTcfRowAction = paths_menu.addAction("Update Tcf Location")
            updateLogRowAction = paths_menu.addAction("Update Logs Location")
            updateStatusAction = menu.addAction("Update Status")
            tools_menu = menu.addMenu('Send to Tool')
            extractRowAction = tools_menu.addAction("Extract Model")
            addToRunSummaryAction = tools_menu.addAction("Add to Run Summary")
            has_extras = True
        
        # lookup the table and database table name
        table_obj = self.view_tables.getTable(name=sender)
        
        # Get the action and do whatever it says
        action = menu.exec_(table_obj.ref.viewport().mapToGlobal(pos))
             
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
        
        # These are only available on the RUN table
        elif has_extras:
        
            if action == deleteAllRowAction:
                self._deleteRowFromDatabase(table_obj, True)
            
            # Send model path to ModelExtractor
            elif action == extractRowAction:
                if not 'Model Extractor' in self.widgets.keys(): return
                errors = GuiStore.ErrorHolder()
                row = table_obj.currentRow()
                row_dict = table_obj.getValues(row=row, names=['ID', 'IEF', 'IEF_DIR', 'TCF', 'TCF_DIR'])
                errors, in_path = Controller.extractModel(
                                                self.settings.cur_settings_path, 
                                                row_dict, errors)
                
                if errors.has_errors:
                    if errors.msgbox_error:
                        self.launchQMsgBox(errors.msgbox_error.title, 
                                       errors.msgbox_error.message)
                else:
                    self.widgets['Model Extractor'].extractModelFileTextbox.setText(in_path)
                    self.ui.tabWidget.setCurrentWidget(self.widgets['Model Extractor'])
            
            # Send log path to RunSummary tool
            elif action == addToRunSummaryAction:
                if not 'Run Summary' in self.widgets.keys(): return
                row = table_obj.currentRow()
                row_dict = table_obj.getValues(row=row, names=['ID', 'LOG_DIR', 'TCF'])
                tcf = row_dict['TCF'][1:-1]
                tcf = tcf.split(',')[0]
                tcf_name = os.path.splitext(tcf)[0]
                tlf_file = os.path.join(row_dict['LOG_DIR'], tcf_name + '.tlf')
                
                if os.path.exists(tlf_file):
                    self.ui.tabWidget.setCurrentWidget(self.widgets['Run Summary'])
                    self.widgets['Run Summary'].loadIntoTable(tlf_file)
                else:
                    msg = ("Cannot find .tlf file in LOG_DIR does it exist?\n" +
                           "Search here:" + tlf_file)
                    self.launchQMsgBox('File Error', msg) 
            
            # Update IEF_DIR, TCF_DIR, or LOG_DIR
            elif action == updateIefRowAction or action == updateTcfRowAction or action == updateLogRowAction:
                if 'model' in gs.path_holder.keys():
                    p = gs.path_holder['model']
                elif 'log' in gs.path_holder.keys():
                    p = gs.path_holder['log']
                else:
                    p = cur_location
                    
                d = MyFileDialogs(parent=self)
                if action == updateIefRowAction or action == updateTcfRowAction:
                    if action == updateIefRowAction:
                        file_types = 'IEF(*.ief)'
                        lookup_name = 'IEF_DIR'
                    else:
                        file_types = 'TCF(*.tcf)'
                        lookup_name = 'TCF_DIR'
                        
                    open_path = d.openFileDialog(p, file_types=file_types, 
                                                     multi_file=False)
                else:
                    open_path = d.dirFileDialog(p)
                    lookup_name = 'LOG_DIR'
                    
                if not open_path == False:
                    open_path = str(open_path)
                    p = os.path.split(open_path)[0]
                    row = table_obj.currentRow()
                    row_dict = table_obj.getValues(row=row, names=['ID', lookup_name])
                    row_dict[lookup_name] = p
                    table_obj.addRowValues(row_dict, row)
                    self._saveViewChangesToDatabase(table_obj, row)
                    self.loadModelLog()
                    gs.setPath('model', p)
            
            # Update the MB and RUN_STATUS values
            elif action == updateStatusAction:
                # Get the tcf dir path and tcf name
                row = table_obj.currentRow()
                row_dict = table_obj.getValues(row=row, names=['ID', 'TCF_DIR', 'TCF'])
                tcf = row_dict['TCF'][1:-1]
                tcf = tcf.split(',')[0]
                
                # Find the latest values and update the RUN table
                results = Controller.getRunStatusInfo(row_dict['TCF_DIR'], tcf)
                if not results[0] and not results[1]:
                    msg = "Failed to update status (ID=%s).\nIs the TCF_DIR correct and does in contain '_ TUFLOW Simulations.log' file?" % (row_dict['ID'])
                    self.launchQMsgBox('Update Failed', msg)
                elif not results[0]:
                    msg = "Run is not yet complete(ID=%s).\nYou can only update status for a completed run" % (row_dict['ID'])
                    self.launchQMsgBox('Update Failed', msg)
                else:
                    del row_dict['TCF_DIR']
                    row_dict['RUN_STATUS'] = results[1]
                    row_dict['MB'] = results[2]
                    table_obj.addRowValues(row_dict, row)
                    self._saveViewChangesToDatabase(table_obj, row)
                    self.loadModelLog()
            
    
    def _updateAllRowStatus(self):
        """Update the RUN_STATUS and MB of all rows in RUN table."""
        run_table = self.view_tables.getTable('RUN')
        
        failures = []
        row_count = run_table.ref.rowCount()
        self._updateMaxProgress(row_count+1)
        for row in range(0, run_table.ref.rowCount()):
            self._updateStatusBar('Updating row %s of %s' % (row, row_count))
            self._updateCurrentProgress(row)
            row_dict = run_table.getValues(row=row, names=['ID', 'TCF_DIR', 'TCF'])
            id = row_dict['ID']
            tcf_dir = row_dict['TCF_DIR']
            tcf = row_dict['TCF'][1:-1]
            tcf = tcf.split(',')[0]
            success, status, mb = Controller.getRunStatusInfo(tcf_dir, tcf)
            if not success:
                failures.append(id)
            else:
                row_dict['RUN_STATUS'] = status
                row_dict['MB'] = mb
                run_table.addRowValues(row_dict, row)
                self._saveViewChangesToDatabase(run_table, row)

        self.loadModelLog()
        
        if failures:
            msg = "Failed to update status (ID(s)=%s).\nAre the TCF_DIR's correct and do they contain '_ TUFLOW Simulations.log' file(s)?" % (row_dict['ID'])
            self.launchQMsgBox('Update Failer', msg)
        
        self._updateStatusBar('')
        self._updateCurrentProgress(0)
        
    
    def _deleteRowFromDatabase(self, table, all_entry):
        """Deletes the row in the database based on the location that the mouse
        was last clicked.
        This is fine because this function is called from the context menu and
        therefore relies on the user right-clicking on the correct row.
        
        Args:
            table(TableWidget): to get the row data from.
            all_entry(bool): if True deletes associated entries as well.
        """
        
        # Get the currently active row in the table and find it's ID value
        row = table.currentRow()
        row_dict = table.getValues(row=row, names=['ID'])
        
        # Just make sure we meant to do this
        if not all_entry:
            message = "Delete this row?\nTable = %s, Row ID = %s" % (table.name, row_dict['ID'])
        else:
            message = "Delete this row AND all associated rows?\nTable = %s, Row ID = %s" % (table.name, row_dict['ID'])
        answer = self.launchQtQBox('Confirm Delete?', message)            
        if answer == False:
            return
        
        # Delete from database
        errors = GuiStore.ErrorHolder()
        errors = Controller.deleteDatabaseRow(gs.path_holder['log'],
                                table.key, row_dict['ID'], errors, all_entry)
        # and then from the table
        if errors.has_errors:
            if errors.msgbox_error:
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
        errors = Controller.editDatabaseRow(gs.path_holder['log'], 
                                        table.key, id_key, save_dict, errors)
        
        if errors.has_errors:
            logger.error('Row ID=%s failed to update' % (id_key))
            if errors.msgbox_error:
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
            errors = Controller.checkDatabaseVersion(gs.path_holder['log'], errors)
            if errors.has_errors:
                if errors.msgbox_error:
                    self.launchQMsgBox(errors.msgbox_error.title,
                                                errors.msgbox_error.message)
                return
            
            self.view_tables.clearAll()
            self.all_logs = None
             
            # load each of the tables from the database
            table_list = []
            for table in self.view_tables.tables.values():
                table_list.append([table.key, table.name])
            
            entries, errors = Controller.fetchTableValues(gs.path_holder['log'],
                                                          table_list, errors)
            
            if errors.has_errors:
                if errors.msgbox_error:
                    self.launchQMsgBox(errors.msgbox_error.title,
                                                errors.msgbox_error.msg) 
                return
             
            # Add the results to the database tables
            for entry in entries:
                if entry[2]:
                    table = self.view_tables.getTable(name=entry[1])
                    table.ref.setRowCount(entry[3])
                    table.addRows(entry[4], 0)
            

    def _createLogEntry(self):
        """Take the updated data in the provisional table and load it into the
        model log.
        """
        # Check that we have a database
        if not self.checkDbLoaded(): return
        
        all_logs = self.widgets['New Entry'].getSingleLogEntry()
        if not all_logs == None:
            
            try:
                errors = GuiStore.ErrorHolder()
                errors, all_logs = Controller.updateLog(
                            gs.path_holder['log'], all_logs, errors) 
                
                if errors.has_errors:
                    if errors.msgbox_error:
                        self.launchQMsgBox(errors.msgbox_error.title, 
                                            errors.msgbox_error.message)
                    del errors
                    return
                
                # Add the new entries to the view table as well
                self.loadModelLog()
            except:
                self._updateStatusBar('')
                msg = ("Critical Error - Oooohhh Nnnooooooooo....\nThis has " +
                       "all gone terribly wrong. You're on your own dude.\n" +
                       "Don't look at me...DON'T LOOK AT MMMEEEEE!!!\n" +
                       "Game over man, I'm outta here <-((+_+))->")
                logger.error(msg)
                self.launchQMsgBox('Critical Error', msg)
                return
            
            # Update the status bar message
            self.ui.statusbar.showMessage("Log Database successfully updated")
            logger.info('Log Database successfully updated')
            del errors
            
    
    def _createMultipleLogEntry(self):
        """Takes all the files in the multiple model list, load them and add
        them to the database.        
        """
        errors = GuiStore.ErrorHolder()
        # Check that we have a database
        if not self.checkDbLoaded(): 
            if self._TEST_MODE: return errors
            else:
                self.launchQMsgBox('No Database', 'Please load a log database first')
                return
        errors = Controller.checkDatabaseVersion(gs.path_holder['log'], errors)
        if errors.has_errors:
            if errors.msgbox_error and not self._TEST_MODE:
                self.launchQMsgBox(errors.msgbox_error.title,
                                            errors.msgbox_error.message)
            return errors
        
        # Get all of the file paths from the list
        model_paths = self.widgets['New Entry'].getMultipleModelPaths()
        if not model_paths: return errors
        
        # Setup the progress monitor. It updates prgress bars etc
        total = len(model_paths)
        prog_count = 1
        self._updateMaxProgress(total)
        
        # Get the global user supplied log variables
        input_vars = self.widgets['New Entry'].getInputVars()
        
        try:
            for path in model_paths:
                
                self._updateStatusBar('Loading model %s of %s' % (prog_count, total))
                self._updateCurrentProgress(prog_count)
                prog_count += 1
                errors, all_logs = Controller.fetchAndCheckModel(
                                        gs.path_holder['log'], path, errors)
                
                if errors.has_local_errors:
                    continue
                
                run = all_logs.getLogEntryContents('RUN', 0)
                run['MODELLER'] = input_vars['MODELLER']
                run['TUFLOW_BUILD'] = input_vars['TUFLOW_BUILD'] 
                run['ISIS_BUILD'] = input_vars['ISIS_BUILD'] 
                run['EVENT_NAME'] = input_vars['EVENT_NAME'] 

                errors, all_logs = Controller.updateLog(gs.path_holder['log'], 
                                    all_logs, errors, check_new_entries=True)
                
                # If there was an issue updating the database drop out now and 
                # launch the error.
                if errors.msgbox_error and errors.msgbox_error.type == self.DB_UPDATE:
                    if not self._TEST_MODE:
                        self.launchQMsgBox(errors.msgbox_error.title, 
                                                errors.msgbox_error.message)
                    break
                
                if errors.has_local_errors:
                    errors.has_local_errors = False
                    continue

            self.loadModelLog()
        except Exception, err:
            self._updateStatusBar('')
            self._updateCurrentProgress(0)
            msg = ("Critical Error - Oooohhh Nnnooooooooo....\nThis has " +
                   "all gone terribly wrong. You're on your own dude.\n" +
                   "Don't look at me...DON'T LOOK AT MMMEEEEE!!!\n" +
                   "Game over man, I'm outta here <-((+_+))->")
            logger.error(msg + str(err))
            
            if self._TEST_MODE:
                return errors
            else:
                self.launchQMsgBox('Critical Error', msg)
                return

        if errors.has_errors:
            self._updateStatusBar('')
            self._updateCurrentProgress(0)
            text = errors.formatErrors('Some models could not be logged:')
            self.widgets['New Entry'].setMultipleErrorText(text)
            message = 'Some files could not be logged.\nSee Error Logs window for details'
            if not self._TEST_MODE: self.launchQMsgBox('Logging Error', message)

        else:
            logger.info('Log Database updated successfully')
            self.ui.statusbar.showMessage("Log Database successfully updated")
            self._updateCurrentProgress(0)
        
        # Clear the list entries
        self.widgets['New Entry'].clearMultipleModelTable()

        if self._TEST_MODE:
            return errors

    
    def _loadSettings(self):
        """Get the settings loaded from file if they exist.
        """
        try:
            if self.settings.logging_level == logging.WARNING:
                self.ui.actionLogWarning.setChecked(True)
            elif self.settings.logging_level == logging.INFO:
                self.ui.actionLogInfo.setChecked(True)
            elif self.settings.logging_level == logging.DEBUG:
                self.ui.actionLogDebug.setChecked(True)                
            logging.getLogger().setLevel(self.settings.logging_level)
            gs.path_holder = self.settings.path_holder
            
        except:
            logger.warning('Was unable to retrieve previous settings - Has LogIT been updated?')
        
    
    def _writeSettings(self, save_path):
        """Need a custom close event so that we can save the user settings.
        """
        
        def _writeWidgetSettings():
            """Write external widget settings."""
            for w in self.widgets.values():
                try:
                    settings = w.saveSettings()
                    self.settings.tool_settings[w.tool_name] = settings
                except:
                    logger.info('No saveSettings() found for %s' % (w.tool_name))
            
         
        logger.info('Closing program')
        logger.info('Saving user settings to: ' + save_path)
        try:
            self.settings.main['cur_tab'] = self.ui.tabWidget.currentIndex()
            self.settings.path_holder = gs.path_holder
            self._getColumnWidths()
            _writeWidgetSettings()
        except:
            logger.error('Unable to save settings - resetting to new')
            self.settings = LogitSettings()

        try:
            with open(save_path, "wb") as p:
                cPickle.dump(self.settings, p)
        except:
            logger.info('Unable to save user defined settings')
    
    
    def _saveSetup(self):
        """Write the current LogIT setup to file.
        """
        d = MyFileDialogs(parent=self)
        save_path = d.saveFileDialog(path=os.path.split(gs.path_holder['log'])[0], 
                                     file_types='Log Settings (*.logset)')
        
        if save_path == False:
            return
        self._writeSettings(str(save_path))
        
    
    def _loadSetup(self):
        """Load LogIT setup from file.
        """
        errors = GuiStore.ErrorHolder()
        d = MyFileDialogs(parent=self)
        open_path = d.openFileDialog(self.settings.cur_settings_path, 
                        file_types='Log Settings (*.logset)')
        settings, errors = Controller.loadSetup(open_path, errors)
         
        if settings == None:
            if errors.has_errors:
                if errors.msgbox_error:
                    QtGui.QMessageBox.warning(self, errors.msgbox_error.title, 
                                                errors.msgbox_error.message)
            return
        else:
            self.settings = settings
            self._loadSettings()
        
    
    def closeEvent(self, event):
        """Do the things that need doing before closing window.
        """
        save_path = self.settings.cur_settings_path
        self._writeSettings(save_path)

 
    def _updateDatabaseVersion(self): 
        """Checks if the databse at the given path is compatible with the
        latest version of LogIT.
        """
        d = MyFileDialogs(parent=self)
        if not self.checkDbLoaded():
            open_path = d.openFileDialog(path=gs.path_holder['log'], 
                                        file_types='LogIT database(*.logdb)')
        else:
            open_path = d.openFileDialog(path=self.settings.cur_settings_path, 
                                        file_types='LogIT database(*.logdb)')
        if open_path == False:
            return None
        open_path = str(open_path)
        errors = GuiStore.ErrorHolder()
        errors = Controller.updateDatabaseVersion(open_path, errors)
        if errors.has_errors:
            if errors.msgbox_error:
                self.launchQMsgBox(errors.msgbox_error.title, 
                                            errors.msgbox_error.message)
        else:
        
            msg = "Update Successfull\nWould you like to load updated database?"
            reply = self.launchQtQBox('Update Successful', msg)
            if not reply == False:
                temp = gs.path_holder['log'] = open_path
                try:
                    self.loadModelLog()
                    self.ui.statusbar.showMessage("Current log: " + open_path)
                except:
                    logger.error('Cannot load database: see log for details')
                    self.launchQMsgBox(errors.types[errors.DB_UPDATE].title, 
                                       errors.types[errors.DB_UPDATE].message)
    
    
    def _createNewLogDatabase(self):
        """Create a new model log database.
        """
        self.launchQMsgBox('', 'In new log create')
        if 'log' in gs.path_holder.keys():
            p = gs.path_holder['log']
        else:
            p = cur_location
        self.launchQMsgBox('', 'After path variable check')
            
        d = MyFileDialogs(parent=self)
        save_path = d.saveFileDialog(path=p, file_types='LogIT database(*.logdb)')
        
        if not save_path == False:
            try:
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                gs.setPath('log', save_path)
                self.view_tables.clearAll()
                self.ui.statusbar.showMessage('Building new log database...')
                self.ui.centralwidget.setEnabled(False)
                #DatabaseFunctions.createNewLogDatabase(str(save_path))
                DatabaseFunctions.createNewLogDatabase(gs.path_holder['log'])
                self.ui.centralwidget.setEnabled(True)
                self.ui.statusbar.showMessage("Current log: " + save_path)
            except Exception, err:
                logger.error('Problem loading cache: ' + err)
            finally:
                self.emit(QtCore.SIGNAL("statusUpdate"), '')
                self.emit(QtCore.SIGNAL("updateProgress"), 0)
                QtGui.QApplication.restoreOverrideCursor()
    
    
    def _loadDatabaseFromUser(self):
        """Load database chosen by user in dialog.
        """
        d = MyFileDialogs(parent=self)
        if self.checkDbLoaded(False):
            open_path = d.openFileDialog(path=gs.path_holder['log'],
                                        file_types='LogIT database(*.logdb)')
        else:
            open_path = d.openFileDialog(path=cur_location,
                                        file_types='LogIT database(*.logdb)')
        if open_path == False:
            return
        open_path = str(open_path)
        
        if self.settings == False:
            self.settings = LogitSettings()
        
        gs.setPath('log', open_path)
        try:
            self.loadModelLog()
            self.ui.statusbar.showMessage("Current log: " + open_path)
        except:
            logger.error('Cannot load database: see log for details')
    
    
    def _exportDatabase(self, call_name):
        """Exports the database based on calling action.
        """
        if self.checkDbLoaded():
            p = gs.path_holder['log']
            if 'export' in gs.path_holder.keys(): p = gs.path_holder['export']
            d = MyFileDialogs(parent=self)
            save_path = d.saveFileDialog(path=gs.path_holder['log'], 
                                         file_types='Excel File (*.xls)')
            if save_path == False:
                return

            save_path = str(save_path)
            gs.setPath('export', save_path)
            errors = GuiStore.ErrorHolder()
            errors = Controller.exportToExcel(gs.path_holder['log'],
                                              self.export_tables, save_path,
                                                                    errors)
            if errors.has_errors:
                if errors.msgbox_error:
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
            
            
    def _getModelFileDialog(self, multi_paths=False, path=None):
        """Launches an open file dialog to get .ief or .tcf files.
        
        :param multi_paths=False: if set to True it will return a list of all
               the user selected paths, otherwise a single string path.
        :return: The chosen file path, a list of paths or false if the user 
                 cancelled.
        """

        # Check that we have a database
        if not self.checkDbLoaded():
            return False          

        p = gs.path_holder['model']
        if not path is None: p = path
            
        open_path = GuiStore.getModelFileLocation(multi_paths,
                                                  p, gs.path_holder['log'],
                                                  self.settings.cur_settings_path)
        return open_path
    
          
    def _resolveIefs(self):
        """Attempt to automatically update ief files references to current dir.
        
        When .ief files are moved to a new location they retain the old paths
        from the build location. This tool attempts to convert the paths from
        the old location to the new location.
        """
        
        def finalize():
            """Set status update back to default."""
            self._updateStatusBar('')
            self._updateCurrentProgress(0)
        
        p = cur_location
        if 'ief' in gs.path_holder.keys(): p = gs.path_holder['ief']
        elif 'model' in gs.path_holder.keys(): p = gs.path_holder['model']
        d = MyFileDialogs(parent=self)
        ief_paths = d.openFileDialog(path=p, 
                file_types='ISIS/TUFLOW (*.ief *.IEF)', multi_file=True)
        if ief_paths == False:
            return
        
        # Convert QString's to str's
        file_list = []
        for i in ief_paths:
            file_list.append(str(i))
            gs.setPath('ief', i)
        # DEBUG
#         file_list = [r'C:\Users\duncan.runnacles.KEN\Desktop\Temp\logit_test\model\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief',
#                  r'C:\Users\duncan.runnacles.KEN\Desktop\Temp\logit_test\model\isis\iefs\kennford_1%AEP_FINAL_v5.18_dsbd-20%.ief',
#                  r'C:\Users\duncan.runnacles.KEN\Desktop\Temp\logit_test\model\isis\iefs\Kennford_1%AEP_FINAL_v5.18_ExeRd_b25%.ief'
#                 ]
        
        self._updateStatusBar('Attempting to automatically resolve ief file...')
        self._updateMaxProgress(4)
        self._updateCurrentProgress(1)
        ief_holders, ief_fail = IefResolver.autoResolveIefs(file_list)
        
        # If we couldn't find the reference file
        if not ief_holders:
            msg = ('Could not locate intial reference file(s). This means that\n' +
                   'it will not be possible to automated the update of these ' +
                   'iefs.')
            self.launchQMsgBox('Ief Update Error', msg)
            finalize()
            return
        
        # check if there were any files that couldn't be found on first attempt
        missing_keys = []
        for ief_holder in ief_holders:
            miss = ief_holder.getMissingFileKeys()
            if miss:
                for m in miss:
                    if not m in missing_keys:
                        missing_keys.append(m)

        # If there were then use the secondary method to try and get them
        required_search = None
        if missing_keys:
            self._updateStatusBar('Attempting to find missing paths (this may take a while) ...')
            self._updateCurrentProgress(2)
            ief_holders, required_search = IefResolver.resolveUnfoundPaths(ief_holders)
            
            i=0
        
        # Write out the updated files
        self._updateStatusBar('Updating Ief files and writing to file...')
        self._updateCurrentProgress(3)
        ief_objs = IefResolver.updateIefObjects(ief_holders)
        success = IefResolver.writeUpdatedFiles(ief_objs)
        
        self._updateStatusBar('')
        self._updateCurrentProgress(4)
        if not success:
            msg = 'There was an error when writing the updated ief files to disk.'
            self.launchQMsgBox('Ief Write Error', msg)
            finalize()
            return
        
        # Output a summary of any difficulties with the file update
        summary = IefResolver.getUpdateSummary(ief_objs)
        ief_dialog = IefResolver.IefResolverDialog(summary, ief_fail, required_search, parent=self)
        ief_dialog.resize(600, 400)
        ief_dialog.setWindowTitle('Ief Resolver Search Summary')
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(QtCore.QString.fromUtf8(":/icons/images/Logit_Logo2_75x75.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ief_dialog.setWindowIcon(icon)
        ief_dialog.exec_()
        finalize() 
        

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
        elif type == 'critical':
            QtGui.QMessageBox.critical(self, title, message)
        elif type == 'info':
            QtGui.QMessageBox.information(self, title, message)
    
    
    def checkDbLoaded(self, show_dialog=True):
        """Check if there's a database filepath set.
        """
        path, exists = gs.getPath('log')
        if not exists:
            if show_dialog:
                QtGui.QMessageBox.warning(self, "No Database Loaded",
                        "No log database active. Please load or create one from the file menu.")
            logger.error('No log database found. Load or create one from File menu')
            return False
        
        else:
            return True
    
    
    def _copyLogs(self):
        """Zip up all of the log file and copy them to the system clipbaord."""
        zip_log = Controller.prepLogsForCopy(log_path)
        data = QtCore.QMimeData()
        url = QtCore.QUrl.fromLocalFile(zip_log)
        data.setUrls([url])
        QtGui.QApplication.clipboard().setMimeData(data)
    
    
    def _getColumnWidths(self):
        """Store the current column widths for the view tables."""
        for key, table in self.view_tables.tables.iteritems():
            self.settings.main['column_widths'][key] = []
            count = table.ref.columnCount()
            for i in range(0, count):
                self.settings.main['column_widths'][key].append(table.ref.columnWidth(i))


    def _setColumnWidths(self):
        """Load the saved column widths for the view tables."""
        for key, table in self.view_tables.tables.iteritems():
            count = table.ref.columnCount()
            for i in range(0, count):
                if key in self.settings.main['column_widths'].keys():
                    try:
                        table.ref.setColumnWidth(i, self.settings.main['column_widths'][key][i])
                    except IndexError:
                        pass # If we've added new columns since save state
    
    
    def _showReleaseNotes(self):
        """Show the release notes for this version to the user."""
        if gs.__DEV_MODE__ == True: return
        
        if self.settings.main['release_notes_version'] == gs.__VERSION__: return
        
        self.settings.main['release_notes_version'] = gs.__VERSION__
        
        try:
            version_dialog = GuiStore.VersionInfoDialog(
                        gs.__RELEASE_NOTES_PATH__,
                        gs.__VERSION__, parent=self)
            version_dialog.resize(400, 400)
            version_dialog.setWindowTitle('LogIT Update Summary')
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(QtCore.QString.fromUtf8(":/icons/images/Logit_Logo2_75x75.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            version_dialog.setWindowIcon(icon)
            version_dialog.exec_()
        
        except Exception, err:
            logger.error('Could not show release notes' + str(err))
            self.settings.main['release_notes_version'] = ''
        
    
    ''' 
        Progress bar and status bar updates.
    '''
    def _updateStatusBar(self, string): 
        self.ui.statusbar.showMessage(string)
        logger.debug('updating status bar: ' + string)
        QtGui.QApplication.processEvents()
        
    def _updateMaxProgress(self, value):
        """"""
        self.progress_bar.setMaximum(value)
        
    def _updateCurrentProgress(self, value):
        """"""
        self.progress_bar.setValue(value)
        QtGui.QApplication.processEvents()
    


class LogitSettings(object):
    """Storage class for holding all of the settings that the current user has
   stored.
    """
    
    def __init__(self):
        """Constructor.
        """
        self.path_holder = {}
        self.tool_settings = {}
        self.main = self.getMainToolSettings()
        self.cur_settings_path = ''
        self.logging_level = 0

    
    def getMainToolSettings(self):
        """"""
        return {'release_notes_version': '', 'column_widths': {}, 'cur_tab': 0}
    
    
    def copySettings(self, existing_settings):
        """Update this class with another LogitSettings object.
        
        Set the class members equal to those of the loaded settings, ignoring
        any that are not longer user and adding any new ones. Then set the
        main dict values with the loaded settings if they exist in the current
        setup as well.
        
        Args:
            existing_settings(LogitSettings): 
        """
        settings_attrs = [s for s in dir(self) if not s.startswith('__') and not s == 'copySettings' and not s == 'getMainToolSettings']
        for s in settings_attrs:
            if hasattr(existing_settings, s):
                setattr(self, s, getattr(existing_settings, s))
        
        if hasattr(existing_settings, 'main'):
            main_dict = existing_settings.main
            for key, val in self.main.iteritems():
                if key in main_dict.keys():
                    self.main[key] = main_dict[key]
        
        
        
def main():
    # Need to do this so that the icons show up properly
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(gs.__APPID__)
    QPlugin = QtCore.QPluginLoader("qico4.dll")
     
    cur_location = os.getcwd()
    settings_path = os.path.join(cur_location, 'settings.logset')
    new_set = LogitSettings()
 
    try:
        # Load the settings dictionary
        cur_settings = cPickle.load(open(settings_path, "rb"))
        
        # Check that this version of the settings has all the necessary
        # attributes, and if not add the missing ones
        new_set.copySettings(cur_settings)
        cur_settings = new_set
    except:
        print 'Unable to load user defined settings'
    cur_settings = new_set
    cur_settings.cur_settings_path = settings_path
         
    # Launch the user interface.
    app = QtGui.QApplication(sys.argv)
    myapp = MainGui(cur_settings)
    icon_path = os.path.join(settings_path, 'Logit_Logo.ico')
    app.setWindowIcon(QtGui.QIcon(':images/Logit_Logo.png'))
    myapp.show()
    if not gs.__DEV_MODE__:
        myapp.startupChecks()
    
    sys.exit(app.exec_())

 
 
if __name__ == '__main__': main()

