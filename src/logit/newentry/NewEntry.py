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
     DR (28/04/2016):
         Changed use of ToolSettings class to use of a dictionary instead. This
         should cause less hassle when additional variables need to be added.
         Also now shares the path_holder dict in globalsettings.py.
         Now using the AWidget interface.
    DR (08/09/2016):
         Big rewrite to use the new database backend (peewee). Model load and
         data display code updated to work with the new setup.
    

 TODO:
    

###############################################################################
"""

import os

import logging
logger = logging.getLogger(__name__)

from PyQt5 import Qt, QtCore, QtGui, QtWidgets

from qtclasses import MyFileDialogs
    
from AWidget import AWidget
import GuiStore
import Controller
from . import NewEntry_Widget_qt5 as newentrywidget
logger.debug('NewEntry_Widget import complete')
# from app_metrics import utils as applog
import globalsettings as gs

import peeweeviews as pv


class NewEntry_UI(newentrywidget.Ui_NewEntryWidget, AWidget):
    

    def __init__(self, cwd, parent=None, f=QtCore.Qt.WindowFlags()):
        
        super().__init__(parent=parent, f=f, tool_name='New Entry', cwd=cwd)
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
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.loadMultiModelTable.setHorizontalHeaderItem(0, item)
        item.setText('')
        
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.loadMultiModelTable.setHorizontalHeaderItem(1, item)
        item.setText("TCF / IEF File Name")
        
        item = QtWidgets.QTableWidgetItem()
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
        self.modelEntryTreeView.header().sectionResized.connect(self._singleModelResize)
        # Keyboard shortcuts
        self.loadModelButton.setToolTip('Load a new model into table (Ctrl-L)')
        self.loadModelButton.setShortcut("Ctrl+L")
        self.addMultiModelButton.setToolTip('Add model to multiple model list (Ctrl-M)')
        self.addMultiModelButton.setShortcut("Ctrl+M")
        self.removeMultiModelButton.setToolTip('Remove selected models from multiple model list (Ctrl-X)')
        self.removeMultiModelButton.setShortcut("Ctrl+X")
    
    def _singleModelResize(self, index, oldSize, newSize):
        if index == 0:
            self.settings['singleload_column_width'] = self.modelEntryTreeView.columnWidth(0)
            print('Index {0}'.format(index))
            print('Old Size {0}'.format(oldSize))
            print('New Size {0}'.format(newSize))

    def getInputVars(self):
        """Get the main user supplied variables from the input boxes.
        
        Return:
            dict - containing an entry for each variable with the key set as
                the standard access name for that variable in the RUN table.
        """
        input_vars = {'MODELLER': str(self.modellerTextbox.text()),
                      'TUFLOW_BUILD': str(self.tuflowVersionTextbox.text()),
                      'ISIS_BUILD': str(self.isisVersionTextbox.text()),
                      'EVENT_NAME': str(self.eventNameTextbox.text()),
                      'RUN_OPTIONS': str(self.runOptionsTextbox.text())
                     }
        return input_vars
    
    
    def clearSingleModelTable(self):
        """Removes all entries from the single model selection table."""
        self.tree_model.clear()
    
    
    def clearMultipleModelTable(self):
        """Removes all entries from the multiple model selection table."""
        self.loadMultiModelTable.setRowCount(0)
        
    
    def _updateNewEntryTree(self):
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
        
        def createEntry(entry, model_items, name, check_exists=True):
            """
            """ 
            if not entry['TYPE'] in model_items.keys():
                model_items[entry['TYPE'] + 'TOP'] = []
                model_items[entry['TYPE'] + 'ITEM'] = QtGui.QStandardItem(entry['TYPE'])
                model_items[entry['TYPE'] + 'TOP'].append( model_items[entry['TYPE'] + 'ITEM'])
                self.tree_model.appendRow(model_items[entry['TYPE'] + 'TOP'])
            else:
                model_items[entry['TYPE'] + 'ITEM'] = model_items[entry['TYPE']]
            
            entry_item = QtGui.QStandardItem(name)
            model_items[entry['TYPE'] + 'ITEM'].appendRow(entry_item)
            do_update = True
            
            if check_exists == True and entry['EXISTS'] == True:
                entry_item.setBackground(brush_red)
                do_update = False
                
            # Create an entry for each item in the log
            for data_key, data in entry.items():
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
        
        ''' END OF INNER FUNCTION '''
        
        model_items = {}
        brush_green = QtGui.QBrush(QtGui.QColor(204, 255, 153)) # Light green
        brush_red = QtGui.QBrush(QtGui.QColor(255, 204, 204)) # Light red
        self.tree_model = QtGui.QStandardItemModel()
        self.tree_model.setColumnCount(2)
        self.tree_model.setHorizontalHeaderLabels(['Log Type', 'Variables'])

        # RUN
        self.all_logs.run['TYPE'] = 'RUN'
        createEntry(self.all_logs.run, model_items, self.all_logs.run_hash, check_exists=False)  

        # DAT
        if self.all_logs.dat is not None:
            self.all_logs.dat['TYPE'] = 'DAT'
            createEntry(self.all_logs.dat, model_items, self.all_logs.dat['NAME'])   
        
        # IED
        for ied in self.all_logs.ieds:
            createEntry(ied, model_items, ied['NAME'])
        
        # MODEL FILES
        for entry in self.all_logs.models:
            createEntry(entry, model_items, entry['NAME'])
            
        self.modelEntryTreeView.setModel(self.tree_model)
        self.modelEntryTreeView.expandAll()
        self.modelEntryTreeView.setColumnWidth(0, self.settings['singleload_column_width'])
            

    def _loadSingleLogEntry(self, testpath=''):

        if not self.checkDbLoaded():
            return

        # Launch dialog and get a file
        chosen_path = self.cur_location
        if 'model' in gs.path_holder.keys():
            chosen_path = gs.path_holder['model']
        d = MyFileDialogs(parent=self)
        open_path = d.openFileDialog(path=chosen_path, 
                                     file_types='ISIS/TUFLOW (*.ief *.IEF *.tcf *.TCF)', 
                                     multi_file=False)
        
        # If the user doesn't cancel
        if not open_path == False:
            
            try:
                open_path = str(open_path)
                self.loadModelTextbox.setText(open_path)
                gs.setPath('model', open_path)
                
                run_options = str(self.runOptionsTextbox.text())
                errors = GuiStore.ErrorHolder()
                errors, self.all_logs = Controller.fetchAndCheckModel(open_path, run_options, errors)
                
                
                # Check what's already in the database
                if not errors.has_errors:
                    # They might have been collected from .ief so get them again here
                    run_options = self.all_logs.run['RUN_OPTIONS']
                    for i, m in enumerate(self.all_logs.models):
                        if pv.modelExists(m['NAME']):
                            self.all_logs.models[i]['EXISTS'] = True
                    
                    if self.all_logs.dat is not None:
                        if pv.datExists(self.all_logs.dat['NAME']):
                            self.all_logs.dat['EXISTS'] = True
                                    
                if errors.has_errors:
                        self.launchQMsgBox("Load Error", errors.formatErrors())
                else:
                    self.statusUpdateSignal.emit('Loaded model at: %s' % (open_path))
#                     self.emit(QtCore.SIGNAL("statusUpdate"), 'Loaded model at: %s' % (open_path))
                    input_vars = self.getInputVars()
                    self.all_logs.run['MODELLER'] = self.settings['modeller'] = input_vars['MODELLER']
                    self.all_logs.run['TUFLOW_BUILD'] = self.settings['tuflow_model'] = input_vars['TUFLOW_BUILD'] 
                    self.all_logs.run['ISIS_BUILD'] = self.settings['isis_build'] = input_vars['ISIS_BUILD']
                    self.all_logs.run['EVENT_NAME'] = self.settings['event_name'] = input_vars['EVENT_NAME'] 
                    self.all_logs.run['RUN_OPTIONS'] = self.settings['run_options'] = run_options 
                    
                    self._updateNewEntryTree()
                    self.submitSingleModelGroup.setEnabled(True)
                    
            except Exception as err:
                self.statusUpdateSignal.emit('')
#                 self.emit(QtCore.SIGNAL("statusUpdate"), '')
                msg = ("Critical Error - Oooohhh Nnnooooooooo....\nThis has " +
                       "all gone terribly wrong. You're on your own dude.\n" +
                       "Don't look at me...DON'T LOOK AT MMMEEEEE!!!\n" +
                       "Game over man, I'm outta here <-((+_+))->")
                logger.error(msg)
                logger.exception(err)
        
    
    def getSingleLogEntry(self):
        """Get the data loaded into the single log entry tab.
        
        Return:
            AllLogs - containing the loaded log data and any user updates.
        """
        if self.all_logs is None: return None
        
        self.settings['singleload_column_width'] = self.modelEntryTreeView.columnWidth(0)
        
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
        for log_key, log in data.items():
            for i in log:
                self.all_logs.updateLogEntry(log_key, i)
#             self.all_logs.updateSubLog(log, log_key)
        
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
        run_options = str(self.runOptionsTextbox.text())
        try:
            for row in range(0, allRows):
                model_paths.append(str(self.loadMultiModelTable.item(row,2).text()))
        except AttributeError as err:
            logger.error('Blank entries in load table: ' + str(err))
            self.launchQMsgBox('Corrupted Inputs', 
                               ('Somehow the input table has been corrupted. ' +
                                'Please reload files and try again'))
            return []
        
        return model_paths, run_options
    
        
    def _updateMultipleLogSelection(self, test_callname='', test_paths=[]):
        """Updates the contents of the loadMultiModelListView.
        Called by both the add and remove buttons. It will open a multiple
        choice file dialog by the former or remove the selected items by the
        latter.
        """
        if not self.checkDbLoaded():
            return
        
        if not self._TEST_MODE:
            caller = self.sender()
            call_name = caller.objectName()
            logger.debug('Caller = ' + call_name)
        else:
            call_name = test_callname
        
        # Add a new file
        if call_name == 'addMultiModelButton':
            
            if not self._TEST_MODE:
                chosen_path = self.cur_location
                if 'model' in gs.path_holder.keys():
                    chosen_path = gs.path_holder['model']
                
                d = MyFileDialogs(parent=self)
                open_paths = d.openFileDialog(path=chosen_path, 
                    file_types='ISIS/TUFLOW (*.ief *.IEF *.tcf *.TCF)',
                    multi_file=True)
                if open_paths == False:
                    return
            else:
                open_paths = test_paths
            
            self.loadMultiModelTable.setSortingEnabled(False)
            for p in open_paths:
                gs.setPath('model', p)
                
                # Insert a new row first if needed
                row_count = self.loadMultiModelTable.rowCount()
                self.loadMultiModelTable.insertRow(row_count)
                
                # Get the filename
                d, fname = os.path.split(str(p))
                
                # Create a couple of items and add to the table
                cbox = QtWidgets.QTableWidgetItem()
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
    
    
    def checkDbLoaded(self, show_dialog=True):
        """Check if there's a database filepath set.
        
        If a path is set it will initiate the database.
        """
        path, exists = gs.getPath('log')
        if not exists:
            if show_dialog:
                QtWidgets.QMessageBox.warning(self, "No Database Loaded",
                        "No log database active. Please load or create one from the file menu.")
            logger.error('No log database found. Load or create one from File menu')
            return False
         
        else:
            return True 
    
    
    def _clearMultiErrorText(self):
        """Clears the error outputs in multi model load error textbox.
        """
        self.multiModelLoadErrorTextEdit.clear()
    
    
    def setMultipleErrorText(self, text):
        """Adds the given text to the error box on the multiple model loader."""
        self.multiModelLoadErrorTextEdit.setText(text)
    
    
    def _copyToClipboard(self):
        """Copies the contents of a textbox to clipboard.
        Textbox to copy is based on the calling action name.
        """
        caller = self.sender()
        call_name = caller.objectName()
         
        if call_name == 'multiModelErrorCopyButton':
            AWidget._copyToClipboard(self, self.multiModelLoadErrorTextEdit)
    
    
    def getSettingsAttrs(self):
        """Setup the ToolSettings attributes for this widget.
        
        Overrides superclass method.
        
        Return:
            dict - member varibles and initial state for ToolSettings.
        """
        attrs = {'modeller': '', 'tuflow_version': '', 'isis_version': '', 
                 'event_name': '', 'run_options': '' , 'cur_load_tab': 0, 
                 'singleload_column_width': 100}
        return attrs
    
    
    def loadSettings(self, settings):
        """Load any pre-saved settings provided."""
        
        AWidget.loadSettings(self, settings)
        self.modellerTextbox.setText(settings['modeller'])
        self.tuflowVersionTextbox.setText(settings['tuflow_version'])
        self.isisVersionTextbox.setText(settings['isis_version'])
        self.eventNameTextbox.setText(settings['event_name'])
        self.runOptionsTextbox.setText(settings['run_options'])
        self.loadModelTab.setCurrentIndex(settings['cur_load_tab'])
        if self.settings['singleload_column_width'] < 100:
            self.settings['singleload_column_width'] = 100

    
    def saveSettings(self):
        """Return state of settings back to caller.
        
        Overrides superclass method.
        """
        self.settings['modeller'] = str(self.modellerTextbox.text())
        self.settings['tuflow_version'] = str(self.tuflowVersionTextbox.text())
        self.settings['isis_version'] = str(self.isisVersionTextbox.text())
        self.settings['event_name'] = str(self.eventNameTextbox.text())
        self.settings['run_options'] = str(self.runOptionsTextbox.text())
        self.settings['cur_load_tab'] = self.loadModelTab.currentIndex()
        return self.settings
    
    
        