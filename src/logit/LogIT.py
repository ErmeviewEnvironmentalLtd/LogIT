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
    DR - 08/09/2016:
        Massive rework of the way that the logs are stored and displayed. The
        peewee library is now used for all database interactions.
        The increasingly large number of tables to display log info has been
        reduced to 3. One for the run log one to be shared between the 
        model logs and one to show the results of querying the other two.

  TODO:
     
############################################################################## 
"""

# Python standard modules
import os
import shutil
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

TEMP_PATH = os.path.join(cur_location, 'temp')
try:
    if not os.path.exists(TEMP_PATH):
        os.mkdir(TEMP_PATH)
except:
    TEMP_PATH = None


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
#import DatabaseFunctions
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

import peeweemodels as pm
import peeweeviews as pv
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
        self._previous_widget = None
        self._unsaved_entries = {}
        self._on_viewlog = False
        
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
        self.ui.actionLoad.triggered.connect(self._loadNewModelLog)
        self.ui.actionExportToExcel.triggered.connect(self._exportDatabase)
        self.ui.actionNewModelLog.triggered.connect(self._createNewLogDatabase)
#         self.ui.actionUpdateDatabaseSchema.triggered.connect(self._updateDatabaseVersion)
        self.ui.actionCleanDatabase.triggered.connect(self.cleanDatabase)
        self.ui.actionSaveSetupAs.triggered.connect(self._saveSetup)
        self.ui.actionLoadSetup.triggered.connect(self._loadSetup)
        self.ui.actionLogWarning.triggered.connect(self._updateLoggingLevel)
        self.ui.actionLogDebug.triggered.connect(self._updateLoggingLevel)
        self.ui.actionLogInfo.triggered.connect(self._updateLoggingLevel)
        self.ui.actionReloadDatabase.triggered.connect(self._loadModelLog)
        self.ui.actionCopyLogsToClipboard.triggered.connect(self._copyLogs)
        self.ui.actionCheckForUpdates.triggered.connect(self._checkUpdatesTrue)
        self.ui.actionResolveIefFiles.triggered.connect(self._resolveIefs)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionUpdateAllRunStatus.triggered.connect(self._updateAllRowStatus)
        self.ui.tabWidget.currentChanged.connect(self._tabChanged)
        self.ui.queryFileCheck.stateChanged.connect(self._queryIncludeFilesChange)

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
        
        # Load the user settings from the last time the software was used 
        self._loadSettings()
        lpath, e = gs.getPath('last_path')
        if not e: gs.path_holder['last_path'] = self.settings.cur_settings_path
        logger.debug('Load settings complete')
        self._addWidgets()
        logger.debug('Add Widgets complete')
#         self._setColumnWidths()
#         logger.debug('Set column widths complete')
        
        # Use those settings to get the file path and try and load the last log
        # database that the user had open
        self.table_info = {}
        self._setupDbTabs()
        if self.checkDbLoaded(False) and self.checkDatabaseVersion(gs.path_holder['log']):
            self._loadModelLog()
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
        
        self._previous_widget = self.ui.tabWidget.currentWidget()
        logger.debug('MainGui construction complete')


    def _setupDbTabs(self):
        """Adds Run Tab to the Log View tab holder and sets up table refs.
        
        Sets up the Run Log tab and table and connects all neccessary slots.
        Also sets up defaults for the MODEL and QUERY tables for when needed.
        """
        tchoice = pv.getTableChoice()
        tchoice[0] = 'All Modelfiles'
        tchoice.append('RUN Event')
        tchoice.append('RUN Options')
        self.ui.modelSelectCbox.addItems(pv.getTableChoice())
        self.ui.modelSelectCbox.currentIndexChanged.connect(self.loadModelDb)
        self.ui.queryTableCbox.addItems(tchoice)
        self.ui.queryTableCbox.currentIndexChanged.connect(self.changeSimpleQueryStatus)
        self.ui.runSimpleQueryBut.clicked.connect(self.runSimpleQuery)
        
        run_table = GuiStore.TableWidgetDb('RUN', 0, 0, hidden_cols=self.settings.main['run_hidden_cols'], parent=self)
        self.connect(run_table, QtCore.SIGNAL("statusUpdate"), self._updateStatusBar)
        self.connect(run_table, QtCore.SIGNAL("setRange"), self._updateMaxProgress)
        self.connect(run_table, QtCore.SIGNAL("updateProgress"), self._updateCurrentProgress)
        self.connect(run_table, QtCore.SIGNAL("dbUpdated"), self._loadModelLog)
        self.connect(run_table, QtCore.SIGNAL("runTableContextTool"), self.runTableContextTool)
        self.connect(run_table, QtCore.SIGNAL("runTableContextPathUpdate"), self.runTableContextPathUpdate)
        self.connect(run_table, QtCore.SIGNAL("runTableContextStatusUpdate"), self.runTableContextStatusUpdate)
        self.connect(run_table, QtCore.SIGNAL("queryRunTable"), self.queryRunTable)
        self.table_info['RUN'] = {'table': run_table}
        self.ui.logViewTab.insertTab(0, run_table, 'Runs')
        self.ui.logViewTab.widget(0).setLayout(QtGui.QVBoxLayout())
        self.ui.logViewTab.setCurrentIndex(0)
        
        self.table_info['MODEL'] = {'table': None}
        query_table = GuiStore.TableWidgetDb('QUERY', 0, 0)
        self.table_info['QUERY'] = {'table': query_table}
        self.ui.tableQueryGroup.layout().addWidget(query_table)
    
    
    def _updateAllRowStatus(self):
        """Update the RUN_STATUS and MB of all rows in RUN table."""
        
        failures = []
        row_count = self.table_info['RUN']['table'].rowCount()
        self._updateMaxProgress(row_count+1)
        errors = []
        for row in range(0, row_count):
            self._updateStatusBar('Updating row %s of %s' % (row, row_count))
            self._updateCurrentProgress(row)
            run_id = self.table_info['RUN']['table'].item(row, self.table_info['RUN']['table'].id_col).text()
            errors = self.runTableContextStatusUpdate(run_id, errors, show_error=False)
        if errors:
            errors.insert(0, 'The following updates failed:')
            msg = '\n'.join(errors)
            self.launchQMsgBox('Update Failure', msg)

        self._loadModelLog()
        self._updateStatusBar('')
        self._updateCurrentProgress(0)

    @QtCore.pyqtSlot(int)
    def runTableContextStatusUpdate(self, run_id, errors=[], show_error=True):
        """Update the status of a Run table entry.
        
        Args:
            run_id(int): the Run record to update.
            errors=[](list): will be appended with any errors and returned.
            show_error=True(bool): if True msgbox will be launched on error.
        
        Return:
            list - containing any errors.
        """
        run_data = pv.getRunRow(run_id)
        
        # Find the latest values and update the RUN table
        results = Controller.getRunStatusInfo(run_data['tcf_dir'], run_data['tcf'])
        if not results[0] and not results[1]:
            msg = "- Failed to update status (ID=%s).\n  Is the TCF_DIR correct and does in contain '_ TUFLOW Simulations.log' file?" % (run_id)
            if show_error:
                self.launchQMsgBox('Update Failed', msg)
            errors.append(msg)
        elif not results[0]:
            msg = "- Run is not yet complete(ID=%s).\n  You can only update status for a completed run" % (run_id)
            if show_error:
                self.launchQMsgBox('Update Failed', msg)
            errors.append(msg)
        else:
            vals = {'run_status': results[1], 'mb': results[2]}
            pv.updateRunRow(vals, run_id)
        
        return errors

    @QtCore.pyqtSlot(str, int)
    def runTableContextPathUpdate(self, context_text, run_id):
        """Update the path variables in a Run table record.
        
        Args:
            context_text(str): the text clicked on the context menu.
            run_id(int): the Run record id to update.
        """
        if 'model' in gs.path_holder.keys():
            p = gs.path_holder['model']
        elif 'log' in gs.path_holder.keys():
            p = gs.path_holder['log']
        else:
            p = cur_location
            
        d = MyFileDialogs(parent=self)
        open_path = False
        if context_text == 'Update Ief location' or context_text == 'Update Tcf location':
            if context_text == 'Update Ief location':
                file_types = 'IEF(*.ief)'
                lookup_name = 'ief_dir'
            else:
                file_types = 'TCF(*.tcf)'
                lookup_name = 'tcf_dir'
                
            open_path = d.openFileDialog(p, file_types=file_types, 
                                             multi_file=False)
            
        elif context_text == 'Update Logs location':
            open_path = d.dirFileDialog(p)
            lookup_name = 'log_dir'
        
        if not open_path == False:
            open_path = str(open_path)
            p = os.path.split(open_path)[0]
            row_dict = {lookup_name: p}
            pv.updateRunRow(row_dict, run_id)
            gs.setPath('model', p)
            
        
    @QtCore.pyqtSlot(str, int)
    def runTableContextTool(self, context_text, run_id):
        """Sets up and call any tools on the context menu.
        
        Args:
            context_text(str): the text clicked on the context menu.
            run_id(int): the Run record id to use.
        """
        if context_text == 'Extract Model':
            if not 'Model Extractor' in self.widgets.keys(): return
            errors = GuiStore.ErrorHolder()
            run_data = pv.getRunRow(run_id)
            row_dict = {'IEF': run_data['ief'], 'TCF': run_data['tcf'],
                        'IEF_DIR': run_data['ief_dir'], 'TCF_DIR': run_data['tcf_dir'],
                        'RUN_OPTIONS': run_data['run_options']}
            errors, in_path = Controller.extractModel(
                                            self.settings.cur_settings_path, 
                                            row_dict, errors)
            if errors.has_errors:
                if errors.msgbox_error:
                    self.launchQMsgBox(errors.msgbox_error.title, 
                                   errors.msgbox_error.message)
            else:
                self.widgets['Model Extractor'].resetForm()
                options = row_dict['RUN_OPTIONS']
                if not options == 'None':
                    self.widgets['Model Extractor'].extractRunOptionsTextbox.setText(options)
                self.widgets['Model Extractor'].extractModelFileTextbox.setText(in_path)
                self.ui.tabWidget.setCurrentWidget(self.widgets['Model Extractor'])
                
        elif context_text == 'Run Summary':
            if not 'Run Summary' in self.widgets.keys(): return
            run_data = pv.getRunRow(run_id)
            isis_results = str(run_data['isis_results'])
            if isis_results == '': isis_results = None

            tcf = run_data['tcf']
            tcf_name = os.path.splitext(tcf)[0]
            
            option_name = tcf_name
            if not run_data['run_options'] == '':
                option_name = Controller.resolveFilenameSEVals(tcf_name, 
                                                run_data['run_options'])
            
            tlf_file = str(os.path.join(run_data['log_dir'], option_name + '.tlf'))
            if os.path.exists(tlf_file):
                self.ui.tabWidget.setCurrentWidget(self.widgets['Run Summary'])
                self.widgets['Run Summary'].loadIntoTable(tlf_file, isis_results)
            else:
                msg = ("Cannot find .tlf file in LOG_DIR does it exist?\n" +
                       "Search here:" + tlf_file)
                self.launchQMsgBox('File Error', msg) 
    
    
    def clearQueryForm(self):
        """Reset the Query tab form to default."""
        self.ui.queryNewModelOnlyCheck.setChecked(False)
        self.ui.queryNewSubOnlyCheck.setChecked(False)
        self.ui.queryFileCheck.setChecked(False)
        self.ui.queryFilterRunCbox.setChecked(False)
        self.ui.queryModelTextbox.setText('')
        self.ui.queryFileTextbox.setText('')
        self.ui.queryTableCbox.setCurrentIndex(0)
    
    
    @QtCore.pyqtSlot(str, str, str)
    def queryModelTable(self, table_type, query_type, id):
        """Run a query on the Models tab table.
        
        Args:
            table_type(str): TGC, TBC, TEF, etc.
            query_type(str): the text value of the context menu.
            id(str): the ModelFile.name value to query.
        """
        # setup the form values
        self.clearQueryForm()
        self.ui.logViewTab.setCurrentIndex(2)
        self.ui.queryTabWidget.setCurrentIndex(0)
        self.ui.queryModelTextbox.setText(id)
        self.ui.queryFilterRunCbox.setChecked(False)
        self.ui.queryNewModelOnlyCheck.setChecked(False)
        index = self.ui.queryTableCbox.findText(table_type, QtCore.Qt.MatchFixedString)
        if index >= 0: self.ui.queryTableCbox.setCurrentIndex(index)
        self.ui.queryFileCheck.setChecked(True)
        
        # Setup form based on query_type
        with_files = True
        new_model_only = False
        if query_type == 'Subfiles':
            self.ui.queryNewSubOnlyCheck.setChecked(False)
            new_sub_only = False

        elif query_type == 'Subfiles - New only':
            self.ui.queryNewSubOnlyCheck.setChecked(True)
            new_sub_only = True
        
        # Run the simple query and add the returned rows to the QUERY table
        cols, rows = pv.getSimpleQuery(table_type, id, with_files, new_sub_only, new_model_only, -1)
        self.table_info['QUERY']['table'].addRows(cols, rows)
        
    
    @QtCore.pyqtSlot(str, int)
    def queryRunTable(self, query_type, id):
        """Run a query on the Run log tab table.
        
        Args:
            query_type(str): the text value of the context menu.
            id(int): the Run.id value to query.
        """
        # Setup the simple query forms
        self.clearQueryForm()
        self.ui.logViewTab.setCurrentIndex(2)
        self.ui.queryTabWidget.setCurrentIndex(0)
        self.ui.queryFilterRunCbox.setChecked(True)
        self.ui.queryRunIdSbox.setValue(id)
        index = self.ui.queryTableCbox.findText('All Modelfiles', QtCore.Qt.MatchFixedString)
        if index >= 0: self.ui.queryTableCbox.setCurrentIndex(index)
        table = 'All Modelfiles'
        new_sub_only = False
        new_model_only = False
        with_files = False
        
        # Setup form based on query_type
        if query_type == 'Dat file':
            index = self.ui.queryTableCbox.findText('DAT', QtCore.Qt.MatchFixedString)
            if index >= 0: self.ui.queryTableCbox.setCurrentIndex(index)
            table = 'DAT'
        
        elif query_type == 'Modelfiles':
            self.ui.queryFileCheck.setChecked(False)
            self.ui.queryNewSubOnlyCheck.setChecked(False)
            self.ui.queryNewModelOnlyCheck.setChecked(False)
        
        elif query_type == 'Modelfiles - New only':
            self.ui.queryFileCheck.setChecked(False)
            self.ui.queryNewModelOnlyCheck.setChecked(True)
            self.ui.queryNewSubOnlyCheck.setChecked(False)
            new_sub_only = False
            new_model_only = True

        elif query_type == 'Modelfiles with Subfiles':
            self.ui.queryFileCheck.setChecked(True)
            self.ui.queryNewModelOnlyCheck.setChecked(False)
            self.ui.queryNewSubOnlyCheck.setChecked(False)
            with_files = True
            new_sub_only = False
            new_model_only = False

        elif query_type == 'New Modelfiles with Subfiles':
            self.ui.queryFileCheck.setChecked(True)
            self.ui.queryNewModelOnlyCheck.setChecked(True)
            self.ui.queryNewSubOnlyCheck.setChecked(False)
            new_sub_only = False
            new_model_only = True
            with_files = True

        # Run the simple query and add the returned rows to the QUERY table
        cols, rows = pv.getSimpleQuery(table, '', with_files, new_sub_only, new_model_only, id)
        self.table_info['QUERY']['table'].addRows(cols, rows)
  
    
    def _queryIncludeFilesChange(self, state):
        """Change the enabled status of New only on simple query form.
        
        Sets enabled status of the new model only and new subfile only boxes.
        """
        if state == QtCore.Qt.Unchecked:
            self.ui.queryNewModelOnlyCheck.setEnabled(True)
            self.ui.queryNewSubOnlyCheck.setEnabled(False)
        else:
            self.ui.queryNewModelOnlyCheck.setEnabled(False)
            self.ui.queryNewSubOnlyCheck.setEnabled(True)
    
    def changeSimpleQueryStatus(self):
        """Sets include subfiles and filter by run id enabled status.
        
        Called when a change is made to the queryTableCbox (table combo).
        """
        txt = str(self.ui.queryTableCbox.currentText())
        if txt == 'DAT' or txt == 'RUN Options' or txt == 'RUN Event':
            self.ui.queryFileCheck.setChecked(False)
            if txt != 'DAT':
                self.ui.queryFilterRunCbox.setChecked(False)
            
        
    def runSimpleQuery(self):
        """Run a query on the simple query tab.
        
        Called by the Run Query button on the simple query tab.
        Takes the current values of the form and runs calls the getSimpleQuery
        function in peeweeviews.
        """
        table = str(self.ui.queryTableCbox.currentText())
        q1_vtext = str(self.ui.queryModelTextbox.text())
        q2_vtext = str(self.ui.queryFileTextbox.text())
        with_files = self.ui.queryFileCheck.isChecked()
        new_sub_only = self.ui.queryNewSubOnlyCheck.isChecked()
        new_model_only = self.ui.queryNewModelOnlyCheck.isChecked()
        use_runid = self.ui.queryFilterRunCbox.isChecked()
        run_id = -1
        if use_runid: run_id = self.ui.queryRunIdSbox.value()
        if self.ui.queryFileTextbox.isEnabled() and table != 'DAT' and\
                                table != 'Run Options' and table != 'Run Event':
            cols, rows = pv.getSimpleQuery(table, q1_vtext, with_files, new_sub_only, new_model_only, run_id, q2_vtext)
        else:
            cols, rows = pv.getSimpleQuery(table, q1_vtext, with_files, new_sub_only, new_model_only, run_id)
        self.table_info['QUERY']['table'].addRows(cols, rows)
        
    def checkUnsavedEntries(self, table, include_cancel_button=True):
        """Checks the unsaved entry status of open tables.
        
        Check the RUN and current MODEL tables to see if they have any user
        changes that have not been saved to the database. If they do it will
        warn the user and ask to save updates.
        
        If include_cancel_button==True return values are False if cancel selected or
        True otherwise.
        If it equals False return values are True for Yes, False for No.
        
        Args:
            table(str): TableWidgetDb.name.
        
        Return:
            bool.
        """
        if not table in self.table_info.keys(): return
        if not self.table_info[table]['table'] is None:
            if self.table_info[table]['table']._unsaved_entries:

                message = 'There are unsaved edits for %s table that will be lost\nSave Now?' % str(table)
                if include_cancel_button:
                    answer = QtGui.QMessageBox.question(self, 'Unsaved Edits', message, 
                                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel)
                    if answer == QtGui.QMessageBox.Yes:
                        self.table_info[table]['table'].saveTableEdits()
                    elif answer == QtGui.QMessageBox.Cancel:
                        return False
                else:
                    answer = QtGui.QMessageBox.question(self, 'Unsaved Edits', message, 
                                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    if answer == QtGui.QMessageBox.Yes:
                        self.table_info[table]['table'].saveTableEdits()
                    elif answer == QtGui.QMessageBox.No:
                        return False
        
        return True

    
    def checkDatabaseVersion(self, dbpath):
        """Test the database version and check compatibility.
        
        Ensures that the database at dbpath is compatible with this version
        of logit.
        """
        try:
            version = pv.checkDatabaseVersion(dbpath)
        except:
            msg = 'Could not connect to database. Please try again.'
            self.launchQMsgBox('Connection Error', msg)
            return False

        success =True
        if version == pm.DATABASE_VERSION_OLD:
            msg = ('This database was created with a LogIT version < 1.0.0\n' +
                   'You will need to use an older version of LogIT!')
            success = False
        elif version == pm.DATABASE_VERSION_HIGH:
            msg = ('This database was created with a newer version of LogIT\n'+
                   'Please upgrade to a newer version.')
            success = False
        elif version == pm.DATABASE_VERSION_LOW:
            msg = ('This database needs upgrading. Please contact anyone but Duncan.')
            success = False
        
        if not success:
            self.launchQMsgBox('Database version error', msg)
        
        return success
    
    def _loadNewModelLog(self):
        """Asks user for an existing .logdb file and loads."""
        path, exists = gs.getPath('log')
        if exists:
            p = path
        else:
            p = gs.path_holder['last_path']
        d = MyFileDialogs(parent=self)
        open_path = d.openFileDialog(path=p, file_types='LogIT database(*.logdb)')
        if open_path != False: 
            open_path = str(open_path)
            gs.setPath('log', open_path)
            success = self.checkDatabaseVersion(open_path)
            if success:
                self._loadModelLog()
            
    def _loadModelLog(self):
        """Reload the Run and Model tables."""
        loaded = self.checkDbLoaded()
        if loaded:
            self.loadModelDb()
            self.loadRunDb()
    
    def checkDbLoaded(self, show_dialog=True):
        """Check if there's a database filepath set.
        
        If a path is set it will initiate the database.
        """
        path, exists = gs.getPath('log')
        if not exists:
            if show_dialog:
                QtGui.QMessageBox.warning(self, "No Database Loaded",
                        "No log database active. Please load or create one from the file menu.")
            logger.error('No log database found. Load or create one from File menu')
            return False
         
        else:
            pm.logit_db.init(path)
            return True 

    def loadModelDb(self, index=None):
        """Load table data for the Model log tab on view logs.
        
        Assigns the ModelFile.model_type taken from the combo box to the
        table_info dict and creates a new TableWidgetDb and connects the signals.
        Then makes a call to get the data from the ModelFile table with the
        model_type and adds the returned rows to the new table. 
        """
        cur_text = self.ui.modelSelectCbox.currentText()
        if not cur_text == '':
            if not self.table_info['MODEL']['table'] is None:
                self.checkUnsavedEntries('MODEL', False)
                w = self.ui.tableModelGroupLayout.takeAt(0).widget()
                if w is not None:
                    w.deleteLater()
                    self.table_info['MODEL']['table'] = None
                
            model_table = GuiStore.TableWidgetDb('MODEL', 0, 0, subname=cur_text, parent=self)
            self.connect(model_table, QtCore.SIGNAL("statusUpdate"), self._updateStatusBar)
            self.connect(model_table, QtCore.SIGNAL("setRange"), self._updateMaxProgress)
            self.connect(model_table, QtCore.SIGNAL("updateProgress"), self._updateCurrentProgress)
            self.connect(model_table, QtCore.SIGNAL("dbUpdated"), self._loadModelLog)
            self.connect(model_table, QtCore.SIGNAL("queryModelTable"), self.queryModelTable)
            self.table_info['MODEL'] = {'table': model_table}
            self.ui.tableModelGroupLayout.addWidget(model_table)
            cols, rows = pv.getModelData(cur_text)
            self.table_info['MODEL']['table'].addRows(cols, rows)
    
    def loadRunDb(self):
        """Loads the Run table database data into the Run log tab table."""
        if not self.table_info['RUN']['table'] is None:
            if not self.checkUnsavedEntries('RUN'):
                return
        cols, rows = pv.getRunData()
        self.table_info['RUN']['table'].addRows(cols, rows)
        
    def _createNewLogDatabase(self):
        """Create a new .logdb database.
        
        Asks user for a filepath to create the new db.
        """
#         QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
#         QtGui.QApplication.restoreOverrideCursor()
        
        d = MyFileDialogs(parent=self)
        path, exists = gs.getPath('log')
        if exists:
            save_path = d.saveFileDialog(path=path, file_types='LogIT database(*.logdb)')
        else:
            save_path = d.saveFileDialog(path=cur_location, file_types='LogIT database(*.logdb)')

        if save_path != False:
            if os.path.exists(save_path):
                os.remove(save_path)
        else:
            return
        
        if not pm.createNewDb(save_path):
            msg = ('Failed to create new database. If this continues please\n' +
                  'report it as a bug.')
            self.launchQMsgBox('Database Error', msg)

        tables = pm.getAllTables()
                
        # Setup the progress monitor. It updates prgress bars etc
        total = len(tables)
        prog_count = 1
        self._updateMaxProgress(total)
         
        for t in tables:
            self._updateStatusBar('Creating table %s of %s' % (prog_count, total))
            self._updateCurrentProgress(prog_count)
            prog_count += 1
            pm.createTable(t, False)
        
        gs.setPath('log', save_path)
        self._loadModelLog()
        self._updateStatusBar('New database created: %s' % save_path)
        self._updateCurrentProgress(0)
        
    
    def startupChecks(self):
        """Check for new versions and show release notes if needed."""
        self._showReleaseNotes()
        self._checkUpdatesFalse()
        
    
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
        if str(self.ui.tabWidget.tabText(self.settings.main['cur_tab'])) == 'View Log':
            self._on_viewlog = True
        else:
            self._on_viewlog = False
    
    
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
            

    def _createLogEntry(self):
        """Take the updated data in the provisional table and load it into the
        model log.
        """
        temp_copy = os.path.join(TEMP_PATH, os.path.basename(gs.path_holder['log']))
        # Check that we have a database
        if not self.checkDbLoaded(): 
            self.launchQMsgBox('No Database', 'Please load a log database first')
            return
        
        # Check we don't have any unsaved data in the tables first
        if not self.checkUnsavedEntries('RUN'): return
        if not self.checkUnsavedEntries('MODEL'): return
        
        all_logs = self.widgets['New Entry'].getSingleLogEntry()
        if not all_logs is None:
            
            try:
                shutil.copy(gs.path_holder['log'], temp_copy)
            except IOError, err:
                logger.warning('Cound not create temp backup')
            
            try:
                if all_logs.dat is not None:
                    dat = pv.addDat(all_logs.dat)
                else:
                    dat = None
                run = pv.addRun(all_logs.run, all_logs.run_hash, all_logs.ief_dir, 
                                all_logs.tcf_dir, dat)
                pv.addAllModel(all_logs.models, run)

                # Add the new entries to the view table as well
                self._loadModelLog()
            except Exception, err:
                
                self._updateStatusBar('')
                msg = ("Critical Error - Oooohhh Nnnooooooooo....\nThis has " +
                       "all gone terribly wrong. You're on your own dude.\n" +
                       "Don't look at me...DON'T LOOK AT MMMEEEEE!!!\n" +
                       "Game over man, I'm outta here <-((+_+))->")
                logger.error('Critical error in create log entry')
                logger.exception(err)
                self.launchQMsgBox('Critical Error', msg)
                try:
                    os.remove(gs.path_holder['log'])
                    shutil.copy(temp_copy, gs.path_holder['log'])
                except IOError, err:
                    logger.warning('Could not reinstate backup!')
                    p = os.normpath(TEMP_PATH)
                    msg = "Couln't auto-reinstate the backup, but you can find\nit here and do it manually:\n" + p
                    self.launchQMsgBox('Backup failure', msg)
                return
            try:
                os.remove(temp_copy)
            except IOError, err:
                logger.warning('Cound not delete temp backup')
            
            # Update the status bar message
            self.ui.statusbar.showMessage("Log Database successfully updated")
            logger.info('Log Database successfully updated')
            
    
    def _createMultipleLogEntry(self):
        """Takes all the files in the multiple model list, load them and add
        them to the database.        
        """
        temp_copy = os.path.join(TEMP_PATH, os.path.basename(gs.path_holder['log']))
        try:
            shutil.copy(gs.path_holder['log'], temp_copy)
        except IOError, err:
            logger.warning('Cound not create temp backup')
                
        errors = GuiStore.ErrorHolder()
        # Check that we have a database
        if not self.checkDbLoaded(): 
            if self._TEST_MODE: return errors
            else:
                self.launchQMsgBox('No Database', 'Please load a log database first')
                return
        
        # Check we don't have any unsaved data in the tables first
        if not self.checkUnsavedEntries('RUN'): return
        if not self.checkUnsavedEntries('MODEL'): return
            
        # Get all of the file paths from the list
        model_paths, run_options = self.widgets['New Entry'].getMultipleModelPaths()
        if not model_paths: return errors
        
        # Setup the progress stuff
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
                errors, all_logs = Controller.fetchAndCheckModel(path, run_options, errors)
                
                if errors.has_local_errors:
                    errors.has_local_errors = False
                    continue
                
                all_logs.run['MODELLER'] = input_vars['MODELLER']
                all_logs.run['TUFLOW_BUILD'] = input_vars['TUFLOW_BUILD'] 
                all_logs.run['ISIS_BUILD'] = input_vars['ISIS_BUILD']
                all_logs.run['EVENT_NAME'] = input_vars['EVENT_NAME'] 
                all_logs.run['RUN_OPTIONS'] = run_options 

                if all_logs.dat is not None:
                    dat = pv.addDat(all_logs.dat)
                else:
                    dat = None
                run = pv.addRun(all_logs.run, all_logs.run_hash, all_logs.ief_dir, 
                                all_logs.tcf_dir, dat)
                pv.addAllModel(all_logs.models, run)

                if errors.has_local_errors:
                    errors.has_local_errors = False
                    continue

            self._loadModelLog()
        except Exception, err:
            self._updateStatusBar('')
            self._updateCurrentProgress(0)
            msg = ("Critical Error - Oooohhh Nnnooooooooo....\nThis has " +
                   "all gone terribly wrong. You're on your own dude.\n" +
                   "Don't look at me...DON'T LOOK AT MMMEEEEE!!!\n" +
                   "Game over man, I'm outta here <-((+_+))->")
            logger.error('Critical error in multiple model load.')
            logger.exception(err)
            try:
                os.remove(gs.path_holder['log'])
                shutil.copy(temp_copy, gs.path_holder['log'])
            except IOError, err:
                logger.error('Cound not reinstate backup!')
                p = os.normpath(TEMP_PATH)
                msg = "Couldn't auto-reinstate the backup, but you can find\nit here and do it manually:\n" + p
                self.launchQMsgBox('Backup failure', msg)
            
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

        try:
            os.remove(temp_copy)
        except IOError, err:
            logger.warning('Cound not delete temp backup')

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
            self.settings.main['run_hidden_cols'] = self.table_info['RUN']['table'].hidden_columns
            self.settings.path_holder = gs.path_holder
#             self._getColumnWidths()
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
        # Make sure that all user edits are saved
        if not self.table_info['MODEL']['table'] is None:
            answer = self.checkUnsavedEntries('MODEL')
        if not self.table_info['RUN']['table'] is None:
            answer = self.checkUnsavedEntries('RUN')
        
        if answer == False: 
            event.ignore()
            return

        save_path = self.settings.cur_settings_path
        self._writeSettings(save_path)

 
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
#             save_path = r'C:/Users/duncan.runnacles/Desktop/TEMP/logit/db/excel_out.xls'

            try:
                # Setup the progress stuff
                self._updateMaxProgress(4)
                self._updateCurrentProgress(1)
                self._updateStatusBar('Exporting Model Files ...')
                model_out = pv.createModelExport()
                self._updateCurrentProgress(2)
                self._updateStatusBar('Exporting Run Files ...')
                run_out, run_header, dat_out, dat_header = pv.createRunDatExport()
                self._updateCurrentProgress(3)
                self._updateStatusBar('Writing to Excel ...')
                Exporters.newExportToExcel(run_out, run_header, dat_out, dat_header, model_out, save_path)
                self._updateCurrentProgress(0)
                self._updateStatusBar('Export Complete')
            
            except Exception, err:
                self._updateCurrentProgress(0)
                self._updateStatusBar('Export Failed')
                logger.exception(err)
                QtGui.QMessageBox.warning(self, "Export Failed",
                                      "Export to Excel failed!")
                
        else:
            logger.warning('Cannot export log - no database loaded')
            QtGui.QMessageBox.warning(self, "Cannot Export Log",
                                      "There is no log database loaded")
        

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
    
    
    def cleanDatabase(self):
         
        try:
            self._updateMaxProgress(3)
            self._updateCurrentProgress(1)
            self._updateStatusBar('Removing orphaned files ...')
            pv.deleteOrphanFiles()
            self._updateCurrentProgress(2)
            self._updateStatusBar('Recalculating file status ...')
            pv.updateNewStatus()
            self._updateCurrentProgress(0)
            self._updateStatusBar('Cleanup complete')

        except Exception, err:
            logger.warning('Cleanup database fail')
            logger.exception(err)
          
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
    
    
    def _copyLogs(self):
        """Zip up all of the log file and copy them to the system clipbaord."""
        zip_log = Controller.prepLogsForCopy(log_path)
        data = QtCore.QMimeData()
        url = QtCore.QUrl.fromLocalFile(zip_log)
        data.setUrls([url])
        QtGui.QApplication.clipboard().setMimeData(data)
    
    
#     def _getColumnWidths(self):
#         """Store the current column widths for the view tables."""
#         for key, table in self.view_tables.tables.iteritems():
#             self.settings.main['column_widths'][key] = []
#             count = table.ref.columnCount()
#             for i in range(0, count):
#                 self.settings.main['column_widths'][key].append(table.ref.columnWidth(i))


#     def _setColumnWidths(self):
#         """Load the saved column widths for the view tables."""
#         for key, table in self.view_tables.tables.iteritems():
#             count = table.ref.columnCount()
#             for i in range(0, count):
#                 if key in self.settings.main['column_widths'].keys():
#                     try:
#                         table.ref.setColumnWidth(i, self.settings.main['column_widths'][key][i])
#                     except IndexError:
#                         pass # If we've added new columns since save state
    
    
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
            
    
    def _tabChanged(self, int):
        """Lets a widget know that it's tab has just been activated / deactivated.
        
        Some of the widgets may want to load data or use memory intensive 
        objects. As the number of tools grows this will become more of an issue
        in terms of load times and runtime memory.
        
        To avoid this we let them know when they're needed or not needed and
        they can claim and release resources appropriately.
        """
        # Check we don't have any unsaved table view edits
        if self._on_viewlog == True:
            self._on_viewlog = False
            for k, v in self._unsaved_entries.items():
                if v:
                    msg = "Save your log edits? (or changes will be lost!)"
                    answer = self.launchQtQBox('Unsaved Edits', msg)
                    if not answer == False:
                        self.saveTableEdits()
                    break
        if str(self.ui.tabWidget.tabText(int)) == 'View Log': self._on_viewlog = True 

        try:
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            self.ui.tabWidget.setEnabled(False)
            current_widget = self.ui.tabWidget.currentWidget()
            
            
            # Try to call the activation notice
            try:
                current_widget.activate()
            except AttributeError:
                # It might be one of the main tabs and not have a 'tool_name'
                try:
                    logger.debug(current_widget.tool_name + ' has not implemented an activation notice')
                except AttributeError:
                    logger.debug('Unnamed tab has not implemented an activation notice')
            
            # Let the old tab know that we're going somewhere else
            if not self._previous_widget is None:
                try:
                    self._previous_widget.deactivate()
                except AttributeError:
                    # It might be one of the main tabs and not have a 'tool_name'
                    try:
                        logger.debug(self._previous_widget.tool_name + ' has not implemented an deactivation notice')
                    except AttributeError:
                        logger.debug('Unnamed tab has not implemented an deactivation notice')

            self._previous_widget = current_widget

        except Exception, err:
            logger.warning('Exception in activation/deactivation of tab')
            logger.exception(err)
        finally:
            self.ui.tabWidget.setEnabled(True)
            QtGui.QApplication.restoreOverrideCursor()
        
    
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
        return {
                'release_notes_version': '', 'column_widths': {}, 'cur_tab': 0,
                'run_hidden_cols': {}
                }
    
    
    def copySettings(self, existing_settings):
        """Update this class with another LogitSettings object.
        
        Set the class members equal to those of the loaded settings, ignoring
        any that are not longer user and adding any new ones. Then set the
        main dict values with the loaded settings if they exist in the current
        setup as well.
        
        Args:
            existing_settings(LogitSettings): 
        """
        settings_attrs = [s for s in dir(self) if not s.startswith('__') and not s == 'copySettings' and not s == 'getMainToolSettings' and not s == 'main']
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
    except:
        print 'Unable to load user defined settings'
    new_set.cur_settings_path = settings_path
         
    # Launch the user interface.
    app = QtGui.QApplication(sys.argv)
    myapp = MainGui(new_set)
    icon_path = os.path.join(settings_path, 'Logit_Logo.ico')
    app.setWindowIcon(QtGui.QIcon(':images/Logit_Logo.png'))
    myapp.show()
    if not gs.__DEV_MODE__:
        myapp.startupChecks()
    
    sys.exit(app.exec_())

 
 
if __name__ == '__main__': main()

