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


 Module:          Query.py 
 Date:            31/10/2016
 Author:          Duncan Runnacles
 Since-Version:   1.3
 
 Summary:
     Contains the Query qidget for the ViewLogs tab. All logic and GUI code
     needed for the tab is located in here. Any interaction required for the 
     rest of the ViewLogs tab is dealt with in signals to the MainGui.
     Contains the Simple Query, ModelFile Query, and Complex Query tabs.

 UPDATES:
    

 TODO:
    

###############################################################################
"""

import logging
logger = logging.getLogger(__name__)

import os
from PyQt4 import QtCore, QtGui

from ship.utils.filetools import MyFileDialogs

from AWidget import AWidget
import Query_Widget as querywidget
import peeweeviews as pv
import peeweemodels as pm
import globalsettings as gs
import GuiStore


class Query_UI(querywidget.Ui_QueryWidget, AWidget):
    

    def __init__(self, cwd, parent=None, f=QtCore.Qt.WindowFlags()):

        AWidget.__init__(self, 'Query', cwd, parent, f, create_data_dir=False)
        self.setupUi(self)

        self.db_design_label = None
        self.do_update = True
        self.current_script_row = -1

        tchoice = pv.getTableChoice()
        tchoice[0] = 'All Modelfiles'
        tchoice.append('RUN Event')
        tchoice.append('RUN Options')
        self.queryTableCbox.addItems(tchoice)
        self.queryTableCbox.currentIndexChanged.connect(self.changeSimpleQueryStatus)
        self.queryFileCheck.stateChanged.connect(self._queryIncludeFilesChange)
        self.fileQueryAddSelectedBut.clicked.connect(self._updateRunIdLists)
        self.fileQueryAddAllBut.clicked.connect(self._updateRunIdLists)
        self.fileQueryRemoveSelectedBut.clicked.connect(self._updateRunIdLists)
        self.fileQueryRemoveAllBut.clicked.connect(self._updateRunIdLists)
        self.fileQueryAvailableList.itemClicked.connect(self._showFileSummaryIdDetails)
        self.fileQuerySelectedList.itemClicked.connect(self._showFileSummaryIdDetails)
        self.fileQueryRunBut.clicked.connect(self.runFileSummaryQuery)
        self.runSimpleQueryBut.clicked.connect(self.runSimpleQuery)
        self.runComplexQueryBut.clicked.connect(self.runComplexQuery)
        self.newQueryScriptBut.clicked.connect(self.newQueryScript)
        self.saveQueryScriptBut.clicked.connect(self.saveQueryScript)
        self.saveAsQueryScriptBut.clicked.connect(self.saveAsQueryScript)
        self.loadQueryScriptBut.clicked.connect(self.loadQueryScript)
        self.complexScriptList.currentRowChanged.connect(self.scriptListItemChanged)

        self.complexScriptList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.complexScriptList.customContextMenuRequested.connect(self._listPopup)

        font = QtGui.QFont()
        font.setFamily( "Courier" )
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.complexScriptText = QtGui.QTextEdit()
        self.complexScriptText.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Ignored)
        self.complexScriptText.setFont(font)
        highlighter = MyHighlighter(self.complexScriptText, "Classic")
        self.editorLayout.addWidget(self.complexScriptText)
        self.complexScriptText.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.complexScriptText.customContextMenuRequested.connect(self._scriptPopup)

        self.addTable()
        

    def addTable(self):
        """Adds a TableWidgetDb object to the query layout."""
        query_table = GuiStore.TableWidgetQuery('QUERY', 0, 0)
        self.query_table = query_table
        self.connect(self.query_table, QtCore.SIGNAL("queryFileSummary"), self._queryFileSummary)
        self.tableQueryGroup.layout().addWidget(self.query_table)
    
    

    '''
    ######################
    COMPLEX QUERY
    ######################
    '''
    def scriptListItemChanged(self, row):
        """Called when an item on the complex query tab script list widget changes.
        
        If self.do_update == False this will do nothing. Stops painful updates
        occurring during processes.
        
        Args:
            row(int): the row number of the new selection.
        """
        if self.do_update:
            if not self.current_script_row == -1:
                old_name = str(self.complexScriptList.item(self.current_script_row).text())
                self.settings['scripts'][old_name][0] = str(self.complexScriptText.toPlainText()) 
            name = str(self.complexScriptList.item(row).text()) 
            self.settings['active_script'] = name
            self.complexScriptText.setPlainText(self.settings['scripts'][name][0])
            self.current_script_row = row

    
    def newQueryScript(self):
        """Creates a new complex query script entry in the list.
        
        Launches an input box to request a name for the script.
        """
        self.do_update = False
        if not self.current_script_row == -1:
            old_name = str(self.complexScriptList.item(self.current_script_row).text())
            self.settings['scripts'][old_name][0] = str(self.complexScriptText.toPlainText()) 
        name = self.launchQtQInput('Name of Script', 'Script Name: ')
        if name == False: return
        
        name = str(name)
        self.settings['scripts'][name] = [None, None]
        self.settings['scripts'][name][0] = ''
        self.settings['scripts'][name][1] = ''
        self.complexScriptList.clear()
        self.complexScriptText.clear()
        self.complexScriptList.addItems(self.settings['scripts'].keys())
        self.settings['active_script'] = name
        for i, val in enumerate(self.settings['scripts'].keys()):
            if str(self.complexScriptList.item(i).text()) == name:
                self.complexScriptList.setItemSelected(self.complexScriptList.item(i), True)
                self.complexScriptList.setCurrentRow(i)
                self.current_script_row = i
        
        self.complexScriptText.setEnabled(True)
        self.do_update = True
    
    
    def saveQueryScript(self):
        """Updates the stored query script in memory.
        
        Updates the value of self.settings['scripts'][name][0] where name is
        current value of self.settings['active_script'].
        """
        if not self.current_script_row == -1:
            self.settings['scripts'][self.settings['active_script']][0] = str(self.complexScriptText.toPlainText())
                
    
    def saveAsQueryScript(self):
        """Saves the currently selected script to file.
        
        Launches a save file dialog to the user and writes the contents of the
        script to file.
        
        The contents are in the format::
        :
            tool=logit
            version=vX.X.X
            type=sql
            whatever query is
            on multiple lines here
        """
        item = self.complexScriptList.item(self.complexScriptList.currentRow())
        if item is None:
            self.launchQMsgBox('Script Error', 'Select or add a script first')
            return

        cur_name = str(item.text())
        p = os.path.join(os.path.dirname(gs.path_holder['last_path']), cur_name)
        if not self.settings['script_path'] == '':
            p = os.path.join(os.path.dirname(gs.path_holder['script_path']), cur_name)
        d = MyFileDialogs(parent=self)
        save_path = d.saveFileDialog(p, file_types='Logit Scripts(*.ls)')
        if save_path == False:
            return
        save_path = str(save_path)
        gs.setPath('last_path', save_path)
        name = os.path.splitext(os.path.basename(save_path))[0]
            
        text = self.complexScriptText.toPlainText()
        try:
            with open(save_path, 'w') as f:
                f.write('tool=logit\n')
                f.write('version=' + gs.__VERSION__ + '\n')
                f.write('type=sql\n')
                f.write(text)
        except Exception, err:
            logger.error('Could not write sql script to file')
            logger.exception(err)
            self.launchQMsgBox('Write Error', 'Unable to write script to file')
            return
        
        self.do_update = False
        if not name == cur_name:
            self.settings['scripts'][name] = [None, None]
            self.settings['scripts'][name][0] = str(self.complexScriptText.toPlainText()) 
            self.settings['scripts'][name][1] = save_path
            if cur_name in self.settings['scripts'].keys():
                del self.settings['scripts'][cur_name]
        else:
            self.settings['scripts'][name][0] = str(self.complexScriptText.toPlainText()) 
            self.settings['scripts'][name][1] = save_path
            
        self.complexScriptList.clear()
        self.complexScriptList.addItems(self.settings['scripts'].keys())
        for i, val in enumerate(self.settings['scripts'].keys()):
            if str(self.complexScriptList.item(i).text()) == name:
                self.complexScriptList.setItemSelected(self.complexScriptList.item(i), True)
                self.complexScriptList.setCurrentRow(i)
        self.do_update = True
    
    
    def loadQueryScript(self):
        """Loads a complex query script from file.
        
        Launches a file dialog to get path. Adds the new script to the script
        list, sets the script editing window to the loaded script contents and
        sets the script as active.
        """
        if not self.current_script_row == -1:
            old_name = str(self.complexScriptList.item(self.current_script_row).text())
            self.settings['scripts'][old_name][0] = str(self.complexScriptText.toPlainText()) 

        p = gs.path_holder['last_path']
        if not self.settings['script_path'] == '':
            p = self.settings['script_path']
        d = MyFileDialogs(parent=self)
        load_path = d.openFileDialog(p, file_types='Logit Scripts(*.ls)')
        if load_path == False:
            return
        load_path = str(load_path)
        gs.setPath('last_path', load_path)
        
        name = os.path.splitext(os.path.basename(load_path))[0]
        data = []
        try:
            with open(load_path, 'rb') as f:
                for line in f.readlines():
                    data.append(line)
        except Exception, err:
            logger.error('Could not read sql script to file')
            logger.exception(err)
            self.launchQMsgBox('Read Error', 'Unable to read script from file')
            return
    
        if not data[0].strip() == 'tool=logit': 
            self.launchQMsgBox('Script Error', 'Script is not a logit script')
        elif not data[2].strip() == 'type=sql':
            self.launchQMsgBox('Script Error', 'Script is not a logit SQL script')
        else:
            self.do_update = False
            text = ' '.join(data[3:])
            self.complexScriptText.setPlainText(text)
            self.settings['scripts'][name] = [None, None]
            self.settings['scripts'][name][0] = text
            self.settings['scripts'][name][1] = load_path
            self.settings['active_script'] = name
            self.complexScriptList.addItem(name)
            for i, val in enumerate(self.settings['scripts'].keys()):
                if str(self.complexScriptList.item(i).text()) == name:
                    self.complexScriptList.setItemSelected(self.complexScriptList.item(i), True)
                    self.complexScriptList.setCurrentRow(i)
                    self.current_script_row = i
            self.complexScriptText.setEnabled(True)
            self.do_update = True

    
    def _listPopup(self):
        """Contex menu for the complex query scripts list."""
        menu = QtGui.QMenu()
        removeAction = menu.addAction("Remove Script")
        sender_obj = self.sender()
        sender = str(sender_obj.objectName())
        cursor = QtGui.QCursor()
        action = menu.exec_(cursor.pos())
        
        if action == removeAction:
            self.do_update = False
            item = self.complexScriptList.takeItem(self.complexScriptList.currentRow())
            name = str(item.text())
            if name in self.settings['scripts'].keys(): 
                del self.settings['scripts'][name]
                if self.settings['active_script'] == name:
                    self.settings['active_script'] = ''

            if self.complexScriptList.count() < 1:
                self.complexScriptText.clear()
                self.complexScriptText.setEnabled(False)
                self.current_script_row = -1
            self.do_update = True

    
    def _scriptPopup(self, pos):
        """Context menu for the complex query editing window.
        
        Current only used to show the database design image.
        """
        menu = QtGui.QMenu()
        dbDesignAction = menu.addAction("Show DB design")
        sender_obj = self.sender()
        sender = str(sender_obj.objectName())
        cursor = QtGui.QCursor()
        action = menu.exec_(cursor.pos())
        
        if action == dbDesignAction:
            if not self.db_design_label is None:
                self.db_design_label.refresh()
                self.db_design_label.show()
            else:
                self.db_design_label = DbDesignLabel(f=QtCore.Qt.WindowStaysOnTopHint) 
                self.db_design_label.refresh()
                self.db_design_label.show()
                self.connect(self.db_design_label, QtCore.SIGNAL("closingForm"), self._closeLabel)
    
    def _closeLabel(self):
        """Gracefully shutdown db_design graphics window."""
        try:
            del self.db_design_label
            self.db_design_label = None
        except:
            logger.info('No db_design_label to close')
        
    
    def runComplexQuery(self):
        """Calls the complex query view.
        
        Takes the contents of the script editing window adds the resultant query
        data to the query table. Queries that attempt to update, edit or delete
        data are refused.
        
        Displays the sql error messages to the user if returned.
        """
        self.saveQueryScript()
        raw_query = str(self.complexScriptText.toPlainText())
        
        if not self.checkDbLoaded(): return
        if 'ORDER BY' in raw_query.upper():
            self.query_table.setSortingEnabled(False)
        cols, rows, error = pv.complexQuery(gs.path_holder['log'], raw_query)
        
        if cols is None:
            self.launchQMsgBox('Query Error', error)
        else:
            self.query_table.addRows(cols, rows)
        
        if 'ORDER BY' in raw_query.upper():
            self.query_table.setSortingEnabled(True)
            
        

    def _queryFileSummary(self, ids):
        """Slot called by table context menu."""
        self.emit(QtCore.SIGNAL("queryFileSummary"), ids) 
    '''
    ######################
    END COMPLEX QUERY
    ######################
    '''

     
    '''
    ######################
    SIMPLE QUERY
    ######################
    '''
    def changeSimpleQueryStatus(self):
        """Sets include subfiles and filter by run id enabled status.
        
        Called when a change is made to the queryTableCbox (table combo).
        """
        txt = str(self.queryTableCbox.currentText())
        if txt == 'DAT' or txt =='IED' or txt == 'RUN Options' or txt == 'RUN Event':
            self.queryFileCheck.setChecked(False)
            if txt != 'DAT' and txt != 'IED':
                self.queryFilterRunCbox.setChecked(False)
    
    
    def runSimpleQuery(self):
        """Run a query on the simple query tab.
        
        Called by the Run Query button on the simple query tab.
        Takes the current values of the form and runs calls the getSimpleQuery
        function in peeweeviews.
        
        Return:
            tuple - 
        """
        if not self.checkDbLoaded(): return
        table = str(self.queryTableCbox.currentText())
        q1_vtext = str(self.queryModelTextbox.text())
        q2_vtext = str(self.queryFileTextbox.text())
        with_files = self.queryFileCheck.isChecked()
        new_sub_only = self.queryNewSubOnlyCheck.isChecked()
        new_model_only = self.queryNewModelOnlyCheck.isChecked()
        use_runid = self.queryFilterRunCbox.isChecked()
        run_id = -1
        if use_runid: run_id = self.queryRunIdSbox.value()
        if self.queryFileTextbox.isEnabled() and table != 'DAT' and \
                                table != 'IED' and \
                                table != 'Run Options' and table != 'Run Event':
            cols, rows = pv.getSimpleQuery(table, q1_vtext, with_files, new_sub_only, new_model_only, run_id, q2_vtext)
        else:
            cols, rows = pv.getSimpleQuery(table, q1_vtext, with_files, new_sub_only, new_model_only, run_id)
        
        if table == 'RUN Options' or table == 'RUN Event':
            self.query_table.subname = 'EventOptions'
        else:
            self.query_table.subname = ''
            
        self.query_table.addRows(cols, rows)

    
    def queryModelTable(self, table_type, query_type, id):
        """Run a query on the Models tab table.
        
        Args:
            table_type(str): TGC, TBC, TEF, etc.
            query_type(str): the text value of the context menu.
            id(str): the ModelFile.name value to query.
        """
        # setup the form values
        self.clearQueryForm()
        self.queryTabWidget.setCurrentIndex(0)
        self.queryModelTextbox.setText(id)
        self.queryFilterRunCbox.setChecked(False)
        self.queryNewModelOnlyCheck.setChecked(False)
        index = self.queryTableCbox.findText(table_type, QtCore.Qt.MatchFixedString)
        if index >= 0: self.queryTableCbox.setCurrentIndex(index)
        self.queryFileCheck.setChecked(True)
        
        # Setup form based on query_type
        with_files = True
        new_model_only = False
        if query_type == 'Subfiles':
            self.queryNewSubOnlyCheck.setChecked(False)
            new_sub_only = False

        elif query_type == 'Subfiles - New only':
            self.queryNewSubOnlyCheck.setChecked(True)
            new_sub_only = True
        
        # Run the simple query and add the returned rows to the QUERY table
        cols, rows = pv.getSimpleQuery(table_type, id, with_files, new_sub_only, new_model_only, -1)
        self.query_table.addRows(cols, rows)
        
    
    def queryRunTable(self, query_type, id):
        """Run a query on the Run log tab table.
        
        Args:
            query_type(str): the text value of the context menu.
            id(int): the Run.id value to query.
        """
        # Setup the simple query forms
        self.clearQueryForm()
        self.queryTabWidget.setCurrentIndex(0)
        self.queryFilterRunCbox.setChecked(True)
        self.queryRunIdSbox.setValue(id)
        index = self.queryTableCbox.findText('All Modelfiles', QtCore.Qt.MatchFixedString)
        if index >= 0: self.queryTableCbox.setCurrentIndex(index)
        table = 'All Modelfiles'
        new_sub_only = False
        new_model_only = False
        with_files = False
        
        # Setup form based on query_type
        if query_type == 'Dat file':
            index = self.queryTableCbox.findText('DAT', QtCore.Qt.MatchFixedString)
            if index >= 0: self.queryTableCbox.setCurrentIndex(index)
            table = 'DAT'

        if query_type == 'Ied files':
            index = self.queryTableCbox.findText('IED', QtCore.Qt.MatchFixedString)
            if index >= 0: self.queryTableCbox.setCurrentIndex(index)
            table = 'IED'
        
        elif query_type == 'Modelfiles':
            self.queryFileCheck.setChecked(False)
            self.queryNewSubOnlyCheck.setChecked(False)
            self.queryNewModelOnlyCheck.setChecked(False)
        
        elif query_type == 'Modelfiles - New only':
            self.queryFileCheck.setChecked(False)
            self.queryNewModelOnlyCheck.setChecked(True)
            self.queryNewSubOnlyCheck.setChecked(False)
            new_sub_only = False
            new_model_only = True

        elif query_type == 'Modelfiles with Subfiles':
            self.queryFileCheck.setChecked(True)
            self.queryNewModelOnlyCheck.setChecked(False)
            self.queryNewSubOnlyCheck.setChecked(False)
            with_files = True
            new_sub_only = False
            new_model_only = False

        elif query_type == 'New Modelfiles with Subfiles':
            self.queryFileCheck.setChecked(True)
            self.queryNewModelOnlyCheck.setChecked(True)
            self.queryNewSubOnlyCheck.setChecked(False)
            new_sub_only = False
            new_model_only = True
            with_files = True

        # Run the simple query and add the returned rows to the QUERY table
        cols, rows = pv.getSimpleQuery(table, '', with_files, new_sub_only, new_model_only, id)
        self.query_table.addRows(cols, rows)
    '''
    ######################
    END SIMPLE QUERY
    ######################
    '''
   
    '''
    ######################
    MODEL FILE QUERY
    ######################
    '''
    def updateFileSummaryQueryList(self, ids=[]):
        """
        """
        self.fileQueryAvailableList.clear()
        self.fileQuerySelectedList.clear()
        cols, rows = pv.getRunData()
        if ids:
            for r in rows:
                id = int(r[0])
                if id in ids:
                    self.fileQuerySelectedList.addItem(str(id))
                else:
                    self.fileQueryAvailableList.addItem(str(id))
        else:
            for r in rows:
                id = str(r[0])
                self.fileQueryAvailableList.addItem(id)
                
                
    def _updateRunIdLists(self):
        """"""
        caller = self.sender()
        call_name = caller.objectName()
        
        if call_name == 'fileQueryAddSelectedBut':
            # sort rows in descending order in order to compensate shifting due to takeItem
            rows = sorted([index.row() for index in self.fileQueryAvailableList.selectedIndexes()],
                          reverse=True)
            for row in rows:
                self.fileQuerySelectedList.addItem(self.fileQueryAvailableList.takeItem(row))
            
        elif call_name == 'fileQueryAddAllBut':
            for row in reversed(range(self.fileQueryAvailableList.count())):
                self.fileQuerySelectedList.addItem(self.fileQueryAvailableList.takeItem(row))
        
        elif call_name == 'fileQueryRemoveSelectedBut':
            rows = sorted([index.row() for index in self.fileQuerySelectedList.selectedIndexes()],
                          reverse=True)
            for row in rows:
                self.fileQueryAvailableList.addItem(self.fileQuerySelectedList.takeItem(row))

        elif call_name == 'fileQueryRemoveAllBut':
            for row in reversed(range(self.fileQuerySelectedList.count())):
                self.fileQueryAvailableList.addItem(self.fileQuerySelectedList.takeItem(row))
        
        self.fileQuerySelectedList.sortItems()
        self.fileQueryAvailableList.sortItems()
    
    def _showFileSummaryIdDetails(self, item):
        """"""
        
        id = item.text()
        run = pv.getRunRow(id)
        tcf = run['tcf']
        ief = run['ief']
        run_options = run['run_options']
        self.fileQueryTcfLine.setText(tcf)
        self.fileQueryIefLine.setText(ief)
        self.fileQueryRunOptionsLine.setText(run_options)
    
    
    def runFileSummaryQuery(self):
        """Run a query on the File Summary query tab.
        
        Called by the file summary query button. Takes the id values that are 
        currently in the selected list widget populates the query table with
        a summary of all the files in the chosen runs.
        """
        ids = []
        for index in xrange(self.fileQuerySelectedList.count()):
            ids.append(self.fileQuerySelectedList.item(index).text())
        
        cols, rows, new_status = pv.getFileSummaryQuery(ids)
        if not self.queryFilesHighlightCbox.isChecked(): new_status = []
        self.query_table.addRows(cols, rows, sort_col=0, custom_highlight=new_status)
   
        
    def checkDbLoaded(self, show_dialog=True):
        """Check if there's a database filepath set.
        
        If a path is set it will initiate the database.
        """
        path, exists = gs.getPath('log')
        if not exists:
            if show_dialog:
                self.launchQMsgBox(self, "No Database Loaded",
                        "No log database active. Please load or create one from the file menu.")
            logger.error('No log database found. Load or create one from File menu')
            return False
         
        else:
            pm.logit_db.init(path)
            return True 
    
    
    def _queryIncludeFilesChange(self, state):
        """Change the enabled status of New only on simple query form.
        
        Sets enabled status of the new model only and new subfile only boxes.
        """
        if state == QtCore.Qt.Unchecked:
            self.queryNewModelOnlyCheck.setEnabled(True)
            self.queryNewSubOnlyCheck.setEnabled(False)
        else:
            self.queryNewModelOnlyCheck.setEnabled(False)
            self.queryNewSubOnlyCheck.setEnabled(True)
        
        
    def clearQueryForm(self):
        """Reset the Query tab form to default."""
        self.queryNewModelOnlyCheck.setChecked(False)
        self.queryNewSubOnlyCheck.setChecked(False)
        self.queryFileCheck.setChecked(False)
        self.queryFilterRunCbox.setChecked(False)
        self.queryModelTextbox.setText('')
        self.queryFileTextbox.setText('')
        self.queryTableCbox.setCurrentIndex(0)
    
    
    def getSettingsAttrs(self):
        """Setup the ToolSettings attributes for this widget.
        
        Overrides superclass method.
        
        Return:
            dict - member varibles and initial state for ToolSettings.
        """
        attrs = {'scripts': {}, 'active_script': '', 'script_path': ''} 
        return attrs
    

    def saveSettings(self):
        return self.settings
    
    
    def deactivate(self):
        """Overrides superclass method."""
        self._closeLabel()

    
    def loadSettings(self, settings):
        """Load any pre-saved settings provided.
        
        Overrides superclass method. Does some additional checks on the log
        summary data loaded from the settings and checks the sanity of the
        cache data.
        
        Args:
            settings(ToolSettings): to update the widget settings with.
        """
        AWidget.loadSettings(self, settings)
        
        self.complexScriptList.clear()
        self.complexScriptList.addItems(self.settings['scripts'].keys())
        if self.complexScriptList.count() < 1:
            self.complexScriptText.setEnabled(False)
            return
        for i, val in enumerate(self.settings['scripts'].keys()):
            if str(self.complexScriptList.item(i).text()) == self.settings['active_script']:
                self.complexScriptList.setItemSelected(self.complexScriptList.item(i), True)
                self.complexScriptList.setCurrentRow(i)
                self.current_script_row = i
        


class DbDesignLabel(QtGui.QDialog):
    """Display the database design image.
    
    Dialog window containing a label with the image of the database design.
    """
    
    def __init__(self, title='Database Design', parent=None, f=QtCore.Qt.WindowFlags()):
        """
        Args:
            title(str): window title.
        """
        QtGui.QDialog.__init__(self, parent, f)
        self.resize(800, 600)
       
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0,)
        self.layout.setSpacing(0)
        
        self.scroll = QtGui.QScrollArea()
        self.layout.addWidget(self.scroll)
        
        self.label = QtGui.QLabel()
        self.refresh()
        self.layout.addWidget(self.label)
        self.scroll.setWidget(self.label)
        
        QtGui.QWidget.setWindowTitle(self, title)
    

    def refresh(self):
        """Update the graph displayed."""
        pixmap = QtGui.QPixmap(QtCore.QString.fromUtf8(":/images/db_model_image.png"))
        self.label.setPixmap(pixmap)

    
    def closeEvent(self, event):
        """Custom window close event."""
        self.emit(QtCore.SIGNAL("closingForm"))
        event.ignore()

        
class MyHighlighter(QtGui.QSyntaxHighlighter):

    def __init__( self, parent, theme ):
        QtGui.QSyntaxHighlighter.__init__( self, parent )
        self.parent = parent
        keyword = QtGui.QTextCharFormat()
        reservedClasses = QtGui.QTextCharFormat()
        fields = QtGui.QTextCharFormat()
        assignmentOperator = QtGui.QTextCharFormat()
        delimiter = QtGui.QTextCharFormat()
        number = QtGui.QTextCharFormat()
        string = QtGui.QTextCharFormat()
        singleQuotedString = QtGui.QTextCharFormat()

        self.highlightingRules = []

        # keyword
        brush = QtGui.QBrush(QtCore.Qt.darkRed, QtCore.Qt.SolidPattern )
        keyword.setForeground( brush )
        keyword.setFontWeight( QtGui.QFont.Bold )
        keywords = QtCore.QStringList( ["where", "like", "on", "select", "from",
                                        "insert", "delete", "drop", "truncate",
                                        "and", "or", "join", "create", "alter",
                                        "into", "in", "inner join", "outer join",
                                        "max", "min", "group by", "avg", "count",
                                        "sum", "escape", "as", "order by", "left",
                                        "right", "cross join", "not", "null",
                                        "union", "alias", "full join", "is",
                                        "between", "having", "subquery", "into",
                                        "rowid", "limit", "offset", "asc", "desc",
                                        "by", "all", "column", "current_date",
                                        "current_time", "current_timestamp",
                                        "distinct", "if", "each", "else", "end",
                                        "for", "ignore", "intersect", "isnull",
                                        "no", "of", "primary", "regexp", "row",
                                        "unique", "using", "when", "with", 
                                        "without", "date", "ifnull", "length",
                                        "lower", "round", "ltrim", "rtrim",
                                        "substr", "trim", "upper", "time",
                                        "datetime", "strftime", "count",
                                        "group_concat",
                                        "WHERE", "LIKE", "ON", "SELECT", "FROM",
                                        "INSERT", "DELETE", "DROP", "TRUNCATE",
                                        "AND", "OR", "JOIN", "CREATE", "ALTER",
                                        "INTO", "IN", "INNER JOIN", "OUTER JOIN",
                                        "MAX", "MIN", "GROUP BY", "AVG", "COUNT",
                                        "SUM", "ESCAPE", "AS", "ORDER BY", "LEFT",
                                        "RIGHT", "CROSS JOIN", "NOT", "NULL",
                                        "UNION", "ALIAS", "FULL JOIN", "IS",
                                        "BETWEEN", "HAVING", "SUBQUERY", "INTO",
                                        "ROWID", "LIMIT", "OFFSET", "ASC", "DESC",
                                        "BY", "ALL", "COLUMN", "CURRENT_DATE",
                                        "CURRENT_TIME", "CURRENT_TIMESTAMP",
                                        "DISTINCT", "IF", "EACH", "ELSE", "END",
                                        "FOR", "IGNORE", "INTERSECT", "ISNULL",
                                        "NO", "OF", "PRIMARY", "REGEXP", "ROW",
                                        "UNIQUE", "USING", "WHEN", "WITH", "WITHOUT",
                                        "DATE", "IFNULL", "LENGTH","LOWER", 
                                        "ROUND", "LTRIM", "RTRIM", "SUBSTR", 
                                        "TRIM", "UPPER", "TIME", "DATETIME", 
                                        "STRFTIME", "COUNT", "GROUP_CONCAT"])
        for word in keywords:
            pattern = QtCore.QRegExp("\\b" + word + "\\b")
            rule = HighlightingRule( pattern, keyword )
            self.highlightingRules.append( rule )

        # reservedClasses
        brush = QtGui.QBrush(QtCore.Qt.darkBlue, QtCore.Qt.SolidPattern )
        reservedClasses.setForeground( brush )
        reservedClasses.setFontWeight( QtGui.QFont.Bold )
        keywords = QtCore.QStringList(["run", "run_modelfile", "run_subfile",
                                       "run_ied", "modelfile", "modelfile_subfile",
                                       "subfile", "dat", "ied"])
        for word in keywords:
            pattern = QtCore.QRegExp("\\b" + word + "\\b")
            rule = HighlightingRule( pattern, reservedClasses )
            self.highlightingRules.append( rule )

        # fields
        brush = QtGui.QBrush(QtCore.Qt.darkCyan, QtCore.Qt.SolidPattern )
        fields.setForeground( brush )
        fields.setFontWeight( QtGui.QFont.Bold )
        keywords = QtCore.QStringList(["id", "dat_id", "run_hash", "setup",
                                       "comments", "ief", "tcf", "initial_conditions",
                                       "isis_results", "tuflow_results", 
                                       "event_duration", "run_Status", "mb",
                                       "modeller", "isis_version", "tuflow_version", 
                                       "event_name", "ief_dir", "tcf_dir", 
                                       "log_dir", "run_options", "timestamp",
                                       "run_id", "ied_id", "model_file_id",
                                       "new_file", "sub_file_id", "name",
                                       "amendments", "comments", "ref",
                                       "model_type" 
                                      ])
        
        for word in keywords:
            pattern = QtCore.QRegExp("\\b" + word + "\\b")
            rule = HighlightingRule( pattern, fields )
            self.highlightingRules.append( rule )

        # assignmentOperator
        brush = QtGui.QBrush( QtCore.Qt.magenta, QtCore.Qt.SolidPattern )
        pattern = QtCore.QRegExp("[\.=%\-\+\\\\/\<\>]")
        assignmentOperator.setForeground( brush )
        assignmentOperator.setFontWeight( QtGui.QFont.Bold )
        rule = HighlightingRule( pattern, assignmentOperator )
        self.highlightingRules.append( rule )

        # delimiter
        pattern = QtCore.QRegExp( "[\)\(]+|[\{\}]+|[][]+" )
        delimiter.setForeground( brush )
        delimiter.setFontWeight( QtGui.QFont.Bold )
        rule = HighlightingRule( pattern, delimiter )
        self.highlightingRules.append( rule )

        # number
        brush = QtGui.QBrush( QtCore.Qt.red, QtCore.Qt.SolidPattern )
        pattern = QtCore.QRegExp( "[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?" )
        pattern.setMinimal( True )
        number.setForeground( brush )
        rule = HighlightingRule( pattern, number )
        self.highlightingRules.append( rule )

        # string
        brush = QtGui.QBrush( QtCore.Qt.green, QtCore.Qt.SolidPattern )
        pattern = QtCore.QRegExp( "\".*\"" )
        pattern.setMinimal( True )
        string.setForeground( brush )
        rule = HighlightingRule( pattern, string )
        self.highlightingRules.append( rule )
        
        # singleQuotedString
        pattern = QtCore.QRegExp( "\'.*\'" )
        pattern.setMinimal( True )
        singleQuotedString.setForeground( brush )
        rule = HighlightingRule( pattern, singleQuotedString )
        self.highlightingRules.append( rule )

        

    def highlightBlock( self, text ):
        for rule in self.highlightingRules:
            expression = QtCore.QRegExp( rule.pattern )
            index = expression.indexIn( text )
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat( index, length, rule.format )
                index = text.indexOf( expression, index + length )
        self.setCurrentBlockState( 0 )


class HighlightingRule():
    def __init__(self, pattern, format):
        self.pattern = pattern
        self.format = format 
        
        