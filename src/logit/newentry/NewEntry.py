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

 UPDATES:
    

 TODO:
    

###############################################################################
"""

import os
import time
import shutil
import re

import logging
logger = logging.getLogger(__name__)

from PyQt4 import QtCore, QtGui

from tmactools.utils.filetools import MyFileDialogs
from tmactools.utils.fileloaders.fileloader import FileLoader
from tmactools.tuflow.tuflowfilepart import SomeFile
from tmactools.tuflow.data_files import datafileloader
from tmactools.utils import filetools
    
import GuiStore
import Controller
import NewEntry_Widget as newentrywidget
from app_metrics import utils as applog
import globalsettings as gs


class NewEntry_UI(QtGui.QWidget, newentrywidget.Ui_NewEntryWidget):
    

    def __init__(self, cwd, cur_log_path, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QWidget.__init__(self, parent, f)
        
        self.tool_name = 'New Entry'
        self.settings = ToolSettings()
        self.settings.cur_location = cwd
        self.cur_log_path = cur_log_path
        self.all_logs = None
        
        self.setupUi(self)
        
    
        
        # Setup a custom QTableWidget for multiple model choice table so that
        # It can be drag and dropped into order
        self.horizontalLayout_5.removeItem(self.verticalLayout_21)
        self.loadMultiModelTable = GuiStore.TableWidgetDragRows(0, 3, self)
        #self.ui.loadMultiModelTable.setHorizontalHeaderLabels(['Check', 'File name', 'Abs Path'])
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
        self.horizontalLayout_5.addWidget(self.loadMultiModelTable)
        self.horizontalLayout_5.addItem(self.verticalLayout_21)
        
        # Connect the slots
        self.loadModelButton.clicked.connect(self._loadSingleLogEntry)
        self.addMultiModelButton.clicked.connect(self._updateMultipleLogSelection)
        self.removeMultiModelButton.clicked.connect(self._updateMultipleLogSelection)
        self.multiModelErrorClearButton.clicked.connect(self._clearMultiErrorText)
        self.multiModelErrorCopyButton.clicked.connect(self._copyToClipboard)
        
    
    
    def getInputVars(self, all_logs):
        """
        """
        run = all_logs.getLogEntryContents('RUN', 0)
        run['MODELLER'] = str(self.modellerTextbox.text())
        run['TUFLOW_BUILD'] = str(self.tuflowVersionTextbox.text())
        run['ISIS_BUILD'] = str(self.isisVersionTextbox.text())
        run['EVENT_NAME'] = str(self.eventNameTextbox.text())
        
        return all_logs
    
    
    def _updateNewEntryTree(self, model_log):
        """
        """
        # DEBUG
#         model_log.log_pages['TGC'].update_check = True
        model_log = self.getInputVars(model_log)
        
        brush_green = QtGui.QBrush(QtGui.QColor(204, 255, 153)) # Light green
        brush_red = QtGui.QBrush(QtGui.QColor(255, 204, 204)) # Light red

        self.tree_model = QtGui.QStandardItemModel()
        self.tree_model.setColumnCount(2)
        self.tree_model.setHorizontalHeaderLabels(['Item', 'Value'])

        # Create an entry for each log type that exist in the model
        for key, log_type in model_log.log_pages.iteritems():
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
                if log_type.update_check:
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
                    if do_update and data_key in model_log.editing_allowed:
                        item1.setBackground(brush_green)
                    else:
                        item2.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
                    
                    child.append(item1)
                    child.append(item2)
                    
                    entry_item.appendRow(child)
        
        self.modelEntryTreeView.setModel(self.tree_model)
        self.modelEntryTreeView.setColumnWidth(0, self.settings.singleLoadColumnWidth)
        self.modelEntryTreeView.expandAll()
    
    
    def _loadSingleLogEntry(self):
        """
        """
#         open_path = r'P:\00 Project Files\13059 EA SW Consultancy Support\Technical\Kennford_model\model\hydraulics\Final_Model\model\isis\iefs\kennford_1%AEP_FINAL_v5.18.ief'
#         open_path = r'C:\Users\duncan.runnacles\Documents\Programming\Python\TMacTools\Code\TmacTools\src\tests\testinputdata\Model\tuflow\runs\Option1aPlus_ilo3_Cul6_Grange_T100D5CC_CWI_Run3_F_MHWS_v1-01 - Copy.tcf'
        
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
            
            if not error.has_errors:
                # Create a list of all of the available tables and their names
                table_list = []
                for log_key, log in self.all_logs.log_pages: #self.new_entry_tables.tables.values():
                    for entry_key, entry in log[0]:
                        if log_key == 'RUN': continue
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

            if errors.has_errors:
                self.launchQMsgBox("Load Error", 
                                   errors.formatErrors())
#                 self.ui.statusbar.showMessage('Failed to load model at: %s' % open_path)
            else:
#                 self.ui.statusbar.showMessage('Loaded model at: %s' % open_path)
                self._updateNewEntryTree(self.all_logs)
                self.submitSingleModelGroup.setEnabled(True) 
    
    
    def getSingleLogEntry(self):
        """
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
        self.tree_model.clear()
        
        return self.all_logs
        
    
    def getMultipleModelPaths(self):
        """
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
            chosen_path = self.settings.cur_location
            if not self.settings.cur_model_path == '':
                chosen_path = self.settings.cur_model_path
            
            d = MyFileDialogs()
            open_paths = d.openFileDialog(path=chosen_path, 
                file_types='ISIS/TUFLOW (*.ief *.IEF *.tcf *.TCF)',
                multi_file=True)
            if open_paths == False:
                return
            
            self.loadMultiModelTable.setSortingEnabled(False)
            row_count = self.loadMultiModelTable.rowCount()
            for p in open_paths:
                
                # Insert a new row first if needed
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
            text = self.multiModelLoadErrorTextEdit.toPlainText()
        
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(text)
            event = QtCore.QEvent(QtCore.QEvent.Clipboard)
            QtGui.QApplication.sendEvent(clipboard, event)
    
    
    def launchQMsgBox(self, title, message, type='warning'):
        """Launch a QMessageBox
        """
        if type == 'warning':
            QtGui.QMessageBox.warning(self, title, message)
        
        elif type == 'info':
            QtGui.QMessageBox.information(self, title, message)
            
        
    def loadSettings(self, settings):
        """Load any pre-saved settings provided."""
        
        # Check that this version of the settings has all the necessary
        # attributes, and if not add the missing ones
        temp_set = ToolSettings()
        settings_attrs = [s for s in dir(temp_set) if not s.startswith('__')]
        for s in settings_attrs:
            if not hasattr(settings, s):
                setattr(settings, s, getattr(temp_set, s))
        
        self.modellerTextbox.setText(settings.modeller)
        self.tuflowVersionTextbox.setText(settings.tuflow_version)
        self.isisVersionTextbox.setText(settings.isis_version)
        self.eventNameTextbox.setText(settings.event_name)
        self.loadModelTab.setCurrentIndex(settings.cur_load_tab)
        self.settings = settings
    
    
    def saveSettings(self):
        """Return state of settings back to caller."""
        
        self.settings.modeller = str(self.modellerTextbox.text())
        self.settings.tuflow_version = str(self.tuflowVersionTextbox.text())
        self.settings.isis_version = str(self.isisVersionTextbox.text())
        self.settings.event_name = str(self.eventNameTextbox.text())
        self.settings.cur_load_tab = self.loadModelTab.currentIndex()
        return self.settings
    
    
#     def _getModelFileDialog(self, multi_paths=False):
#         """Launches an open file dialog to get .ief or .tcf files.
#         
#         :param multi_paths=False: if set to True it will return a list of all
#                the user selected paths, otherwise a single string path.
#         :return: The chosen file path, a list of paths or false if the user 
#                  cancelled.
#         """
#         
#         open_path = d.openFileDialog(path=chosen_path, 
#                 file_types='ISIS/TUFLOW (*.ief *.IEF *.tcf *.TCF)',
#                 multi_file=True)
#         
#         return open_path
    
        
        
class ToolSettings(object):
    """Store the settings used by this class."""
    
    def __init__(self):
        
        self.tool_name = 'New Entry'
        self.cur_model_path = ''
        self.cur_output_dir = ''
        self.cur_location = ''
        self.modeller = ''
        self.tuflow_version = ''
        self.isis_version = ''
        self.event_name = ''
        self.cur_load_tab = 0
        self.singleLoadColumnWidth = 100
        
        