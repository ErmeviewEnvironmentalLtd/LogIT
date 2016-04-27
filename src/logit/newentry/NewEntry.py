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


 Module:          NewEntry.py 
 Date:            12/04/2016
 Author:          Duncan Runnacles
 Since-Version:   0.6
 
 Summary:
     Used for loading models into either a single model entry table, that can
     be updated prior to entering into the database, or a multiple model load
     table which will be added as is.
     
     This module doesn't actually add anything to the database. It leaves that
     up to the main gui callers. It contains two methods for getting the
     data in the single and multiple model load tables.

 UPDATES:
    

 TODO:
    

###############################################################################
"""

import os

import logging
logger = logging.getLogger(__name__)

from PyQt4 import QtCore, QtGui

from ship.utils.filetools import MyFileDialogs
    
from AWidget import AWidget
import GuiStore
import Controller
import NewEntry_Widget as newentrywidget
logger.debug('NewEntry_Widget import complete')
# from app_metrics import utils as applog


class NewEntry_UI(newentrywidget.Ui_NewEntryWidget, AWidget):
    

    def __init__(self, cwd, cur_log_path, parent=None, f=QtCore.Qt.WindowFlags()):
        
        AWidget.__init__(self, 'New Entry', cwd, cur_log_path, parent, f)
        self.cur_log_path = cur_log_path
        self.all_logs = None
        self._TEST_MODE = False
        self.setupUi(self)
        
        '''
            Multiple model load table setup.
        '''
        # Setup a custom QTableWidget for multiple model choice table so that
        # It can be drag and dropped into order
        self.multipleModelLayoutH.removeItem(self.multipleModelLayoutV)
        self.loadMultiModelTable = GuiStore.TableWidgetDragRows(0, 3, self)
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.loadMultiModelTable.setHorizontalHeaderItem(0, item)
        item.setText('')
        
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.loadMultiModelTable.setHorizontalHeaderItem(1, item)
        item.setText("TCF / IEF File Name")
        
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.loadMultiModelTable.setHorizontalHeaderItem(2, item)
        item.setText("Absolute Path")
        
        self.loadMultiModelTable.horizontalHeader().setDefaultSectionSize(300)
        self.loadMultiModelTable.horizontalHeader().setMinimumSectionSize(300)
        self.loadMultiModelTable.horizontalHeader().setStretchLastSection(True)
        self.loadMultiModelTable.setColumnWidth(0, 30)
        self.loadMultiModelTable.setStyleSheet('QTableWidget {background-color: rgb(255, 255, 255);}')
        self.loadMultiModelTable.setSortingEnabled(True)
        self.multipleModelLayoutH.addWidget(self.loadMultiModelTable)
        self.multipleModelLayoutH.addItem(self.multipleModelLayoutV)
        '''
            End of Multiple model load table setup.
        '''
        
        # Connect the slots
        self.loadModelButton.clicked.connect(self._loadSingleLogEntry)
        self.addMultiModelButton.clicked.connect(self._updateMultipleLogSelection)
        self.removeMultiModelButton.clicked.connect(self._updateMultipleLogSelection)
        self.multiModelErrorClearButton.clicked.connect(self._clearMultiErrorText)
        self.multiModelErrorCopyButton.clicked.connect(self._copyToClipboard)
        
    
    def getInputVars(self):
        """Get the main user supplied variables from the input boxes.
        
        Return:
            dict - containing an entry for each variable with the key set as
                the standard access name for that variable in the RUN table.
        """
        input_vars = {'MODELLER': str(self.modellerTextbox.text()),
                      'TUFLOW_BUILD': str(self.tuflowVersionTextbox.text()),
                      'ISIS_BUILD': str(self.isisVersionTextbox.text()),
                      'EVENT_NAME': str(self.eventNameTextbox.text())
                     }
        return input_vars
    
    
    def clearSingleModelTable(self):
        """Removes all entries from the single model selection table."""
        self.tree_model.clear()
    
    
    def clearMultipleModelTable(self):
        """Removes all entries from the multiple model selection table."""
        self.loadMultiModelTable.setRowCount(0)
        
    
    def _updateNewEntryTree(self, entry_status):
        """Update the single entry TreeView with the contents of all_logs.
        
        Creates a TreeView separated by the different log types and the names
        of the files under that type. Under the file name is the list of 
        variables loaded for that model. The variables are color coded and 
        made editable if they can be changed. If one of the files already
        exists in the database the filename is colored red.
        
        Args:
            entry_status (dict): containing a status flag for each of the loaded
                files, indicating whether they are new or already exist in the
                database. 
        """
        brush_green = QtGui.QBrush(QtGui.QColor(204, 255, 153)) # Light green
        brush_red = QtGui.QBrush(QtGui.QColor(255, 204, 204)) # Light red

        self.tree_model = QtGui.QStandardItemModel()
        self.tree_model.setColumnCount(2)
        self.tree_model.setHorizontalHeaderLabels(['Log Type', 'Variables'])

        # Create an entry for each log type that exist in the model
        for key, log_type in self.all_logs.log_pages.iteritems():
            if not log_type.has_contents: continue

            top = []
            top_item = QtGui.QStandardItem(log_type.name)
            top.append(top_item)
            self.tree_model.appendRow(top)
            
            # Create child for each list item under log type
            for entry in log_type.contents:
                
                do_update = True
                
                if log_type.name == 'RUN':
                    entry_item = QtGui.QStandardItem('RUN')
                else:
                    entry_item = QtGui.QStandardItem(entry[log_type.name])
                
                # Mark red if it won't be loaded into database. This is 
                # because that file is already in there
                if not log_type.name == 'RUN' and not entry_status[log_type.name][entry[log_type.name]]['Do Update']:
                    entry_item.setBackground(brush_red)
                    do_update = False
                top_item.appendRow(entry_item)
            
                # Create an entry for each item in the log
                for data_key, data in entry.iteritems():
                    child = []
                    item1 = QtGui.QStandardItem(data_key)
                    item2 = QtGui.QStandardItem(str(data))
                    item1.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )

                    # If the entry is editable by user mark it so and color
                    # it green
                    if do_update and data_key in self.all_logs.editing_allowed:
                        item1.setBackground(brush_green)
                    else:
                        item2.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    
                    child.append(item1)
                    child.append(item2)
                    
                    entry_item.appendRow(child)
        
        self.modelEntryTreeView.setModel(self.tree_model)
        self.modelEntryTreeView.setColumnWidth(0, self.settings.singleLoadColumnWidth)
        self.modelEntryTreeView.expandAll()
    
    
    def _loadSingleLogEntry(self, testpath=''):
        """Loads a model and checkes the contents against the database.
        
        Calls LogBuilder to load the model from file. Then checks the loaded
        filenames against those in the database and flags them if they already
        exist.
        
        Finally gets the user entered main variables and calls the 
        updateNewTree method to display the data to the user.
        """
        if self._TEST_MODE:
            open_path = testpath
        else:
            if not os.path.exists(self.cur_log_path):
                self.launchQMsgBox('No log Database', 'There is no log database loaded.\n Please load one first.')
                return
            
            # Launch dialog and get a file
            chosen_path = self.settings.cur_location
            if not self.settings.cur_model_path == '':
                chosen_path = self.settings.cur_model_path
            d = MyFileDialogs()
            open_path = d.openFileDialog(path=chosen_path, 
                                         file_types='ISIS/TUFLOW (*.ief *.IEF *.tcf *.TCF)', 
                                         multi_file=False)
        
        # If the user doesn't cancel
        if not open_path == False:
            if not os.path.exists(self.cur_log_path):
                self.launchQMsgBox('No Database', 'Please load a log database first')
                return
            
            open_path = str(open_path)
            self.loadModelTextbox.setText(open_path)
            self.settings.cur_model_path = open_path
            
            errors = GuiStore.ErrorHolder()
            errors, self.all_logs = Controller.fetchAndCheckModel(self.cur_log_path, open_path, errors)
            
            # Init a dict to hold the exists/not exists status of the data
            # being loaded
            if not errors.has_errors:
                entry_dict = {}
                for log_key, log in self.all_logs.log_pages.iteritems(): 
                    if log_key == 'RUN' or log.has_contents == False: continue
                    entry_dict[log_key] = {}
                    for item in log.contents:
                        entry_dict[log_key][item[log_key]] = {}
                 
                # check the new entries against the database and return them with
                # flags set for whether they are new entries or already exist
                errors = GuiStore.ErrorHolder()
                entry_status, errors = Controller.loadEntrysWithStatus(
                        self.cur_log_path, self.all_logs, entry_dict, errors)

            if errors.has_errors:
                self.launchQMsgBox("Load Error", 
                                   errors.formatErrors())
            else:
                self.emit(QtCore.SIGNAL("statusUpdate"), 'Loaded model at: %s' % (open_path))
                input_vars = self.getInputVars()
                run = self.all_logs.getLogEntryContents('RUN', 0)
                run['MODELLER'] = input_vars['MODELLER']
                run['TUFLOW_BUILD'] = input_vars['TUFLOW_BUILD'] 
                run['ISIS_BUILD'] = input_vars['ISIS_BUILD'] 
                run['EVENT_NAME'] = input_vars['EVENT_NAME'] 
                self._updateNewEntryTree(entry_status)
                self.submitSingleModelGroup.setEnabled(True) 
    
    
    def getSingleLogEntry(self):
        """Get the data loaded into the single log entry tab.
        
        Return:
            AllLogs - containing the loaded log data and any user updates.
        """
        if self.all_logs is None: return None
        
        self.settings.singleLoadColumnWidth = self.modelEntryTreeView.columnWidth(0)
        
        # Get the data from the new entry tree view
        data = {}
        model = self.modelEntryTreeView.model()
        for i in range(model.rowCount()):
            
            type_row = model.item(i)
            type_text = str(type_row.text())
            num_types = type_row.rowCount()
            data[type_text] = []
 
            for j in range(num_types):
                item = type_row.child(j)
                item_text = str(item.text())
                num_items = item.rowCount()
                temp_dict = {}
                 
                for k in range(num_items):
                    child1 = str(item.child(k).text())
                    child2 = str(item.child(k, 1).text())
                    temp_dict[child1] = child2
                
                data[type_text].append(temp_dict)
        
        # Update the log pages with any user corrections
        for log_key, log in data.iteritems():
            self.all_logs.updateSubLog(log, log_key)
        
        # Reset the tree
        self.clearSingleModelTable()
        self.submitSingleModelGroup.setEnabled(False)
        
        return self.all_logs
        
    
    def getMultipleModelPaths(self):
        """Get the model paths in the multiple model loader table.
        
        Return:
            list - absolute paths added to the table.
        """
        
        # Get all of the file paths from the list
        model_paths = []
        allRows = self.loadMultiModelTable.rowCount()
        try:
            for row in xrange(0, allRows):
                model_paths.append(str(self.loadMultiModelTable.item(row,2).text()))
        except AttributeError, err:
            logger.error('Blank entries in load table: ' + str(err))
            self.launchQMsgBox('Corrupted Inputs', 
                               ('Somehow the input table has been corrupted. ' +
                                'Please reload files and try again'))
            return []
        
        return model_paths
    
        
    def _updateMultipleLogSelection(self, test_callname='', test_paths=[]):
        """Updates the contents of the loadMultiModelListView.
        Called by both the add and remove buttons. It will open a multiple
        choice file dialog by the former or remove the selected items by the
        latter.
        """
        if not self._TEST_MODE:
            caller = self.sender()
            call_name = caller.objectName()
            logger.debug('Caller = ' + call_name)
        else:
            call_name = test_callname
        
        # Add a new file
        if call_name == 'addMultiModelButton':
            
            if not self._TEST_MODE:
                chosen_path = self.settings.cur_location
                if not self.settings.cur_model_path == '':
                    chosen_path = self.settings.cur_model_path
                
                d = MyFileDialogs()
                open_paths = d.openFileDialog(path=chosen_path, 
                    file_types='ISIS/TUFLOW (*.ief *.IEF *.tcf *.TCF)',
                    multi_file=True)
                if open_paths == False:
                    return
            else:
                open_paths = test_paths
            
            self.loadMultiModelTable.setSortingEnabled(False)
            for p in open_paths:
                self.settings.cur_model_path = str(p)
                
                # Insert a new row first if needed
                row_count = self.loadMultiModelTable.rowCount()
                self.loadMultiModelTable.insertRow(row_count)
                
                # Get the filename
                d, fname = os.path.split(str(p))
                self.settings.last_model_directory = d
                
                # Create a couple of items and add to the table
                cbox = QtGui.QTableWidgetItem()
                cbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
                cbox.setCheckState(QtCore.Qt.Unchecked)
                self.loadMultiModelTable.setItem(row_count, 0, cbox)
                self.loadMultiModelTable.setItem(row_count, 1, 
                                        Controller.createQtTableItem(fname, drag_enabled=True))
                self.loadMultiModelTable.setItem(row_count, 2, 
                                        Controller.createQtTableItem(p, drag_enabled=True))
                
            # Set the sumbit button to enabled
            self.submitMultiModelGroup.setEnabled(True)
            self.loadMultiModelTable.sortItems(0,  QtCore.Qt.AscendingOrder)
            self.loadMultiModelTable.setSortingEnabled(False)
                
            
        elif call_name == 'removeMultiModelButton':

            # Get the selected rows, reverse them and remove them
            rows = self.loadMultiModelTable.rowCount()
            for r in range(rows-1, -1, -1):
                cbox = self.loadMultiModelTable.item(r, 0)
                if cbox.checkState() == QtCore.Qt.Checked:
                    self.loadMultiModelTable.removeRow(r)
            
            # Deactivate the log button if there's no rows left
            if self.loadMultiModelTable.rowCount() < 1:
                self.submitMultiModelGroup.setEnabled(False)
        
        else:
            logger.info('Caller %s not recongnised' % call_name)
    
    
    def _clearMultiErrorText(self):
        """Clears the error outputs in multi model load error textbox.
        """
        self.multiModelLoadErrorTextEdit.clear()
    
    
    def _copyToClipboard(self):
        """Copies the contents of a textbox to clipboard.
        Textbox to copy is based on the calling action name.
        """
        caller = self.sender()
        call_name = caller.objectName()
         
        if call_name == 'multiModelErrorCopyButton':
            AWidget.copyToClipboard(self, self.multiModelLoadErrorTextEdit)
    
    
    def getSettingsAttrs(self):
        """Setup the ToolSettings attributes for this widget.
        
        Overrides superclass method.
        
        Return:
            dict - member varibles and initial state for ToolSettings.
        """
        attrs = {'cur_model_path': '', 'cur_output_dir': '',
                 'cur_location': '', 'modeller': '', 'tuflow_version': '',
                 'isis_version': '', 'event_name': '', 'cur_load_tab': 0,
                 'singleLoadColumnWidth': 100}
        return attrs
    
    
    def loadSettings(self, settings):
        """Load any pre-saved settings provided."""
        
        AWidget.loadSettings(self, settings)
        self.modellerTextbox.setText(settings.modeller)
        self.tuflowVersionTextbox.setText(settings.tuflow_version)
        self.isisVersionTextbox.setText(settings.isis_version)
        self.eventNameTextbox.setText(settings.event_name)
        self.loadModelTab.setCurrentIndex(settings.cur_load_tab)
    
    
    def saveSettings(self):
        """Return state of settings back to caller.
        
        Overrides superclass method.
        """
        
        self.settings.modeller = str(self.modellerTextbox.text())
        self.settings.tuflow_version = str(self.tuflowVersionTextbox.text())
        self.settings.isis_version = str(self.isisVersionTextbox.text())
        self.settings.event_name = str(self.eventNameTextbox.text())
        self.settings.cur_load_tab = self.loadModelTab.currentIndex()
        return self.settings
    
    
        