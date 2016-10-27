"""
###############################################################################
    
 Name: LogIT (Logger for Isis and Tuflow) 
 Author: Duncan Runnacles
 Copyright: (C) 2015 Duncan Runnacles
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


 Module:           logit.py
 Date:             05/12/2015
 Author:           Duncan Runnacles
 Since-Version:    0.3
 
 Summary:
    Convenience classes for use with the UI. Nothing kept here will be of
    use to anything other than the GUI. It's a collection of classes for 
    helping the GUI manage code bloat.

 UPDATES:
    DR - 13/12/2015:
        Added ErrorHolder and ErrorType classes. These are used to simplify
        the lauching of errors from the GUI. They can be handed to any
        business coded and updated with new errors that the GUI can deal with
        as it likes later. Useful for easy message box launching and storing 
        a series of errors that need writing out somewhere in the UI.
    DR - 04/03/2016:
        Added TableWidgetDragRows class. Subclasses the QTableWidget class to 
        allow for internal dragging and dropping (reordering) of rows within
        the table.
    DR - 08/09/2016:
        Cleared out the old table holder classes. All functionality is now
        catered for in the TableWidgetDb class with subclasses QTableWidget
        

 TODO:
    
###############################################################################
"""

from PyQt4 import QtCore, QtGui

from ship.utils.qtclasses import MyFileDialogs
from ship.utils.qtclasses import QNumericSortTableWidgetItem

import logging
logger = logging.getLogger(__name__)

import LogClasses
import peeweeviews as pv


class TableWidgetDb(QtGui.QTableWidget):
    """Subclass of QTableWidget with Logit Log View specific behaviour."""
    
    def __init__(self, name, rows, cols, subname='', hidden_cols={}, parent=None):
        """
        Args:
            name(str): the name of this table (RUN, MODEL, QUERY).
            rows(int): number of rows.
            cols(int): number of columns.
            subname=''(str): a subname for this table (TGC, TEF, etc).
            hidden_cols=[]: {col name: index} of columns that should be hidden.
        """
        QtGui.QTableWidget.__init__(self, rows, cols, parent)

        self.name = name
        self.subname = str(subname)
        self.hidden_columns = hidden_cols
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._tablePopup)
        self.editing_allowed = [
           'comments', 'modeller', 'setup', 
           'event_name', 'event_duration', 'isis_version',
           'tuflow_version', 'amendments', 'run_options', 'mb',
           'run_status', 'run_name',
        ]
        
        self.horizontalHeader().setStretchLastSection(True)
        self.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        
        if name == 'MODEL':
            self.id_col = 1
        else:
            self.id_col = 0
        
        self._unsaved_entries = []
        if not name == "QUERY":
            self.cellChanged.connect(self._highlightEditRow)
            self.horizontalHeader().setStretchLastSection(True)
    
    def addRows(self, cols, rows):
        """Add row data to this table.
        
        Uses the TableWidgetItemDb class to create the QTableWidgetItem's.
        
        Args:
            cols(list): columns header strings.
            rows(list): containing lists of cell data to be added to rows.
        """
        
        self.setSortingEnabled(False)
        self.setColumnCount(len(cols))
        
        # For show/hide columns on RUN table (not available on others)
        if self.name == 'RUN':
            self.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.horizontalHeader().customContextMenuRequested.connect(self.showHeaderMenu)
        for k, c in enumerate(cols):
            item = QtGui.QTableWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
            item.setBackgroundColor(QtGui.QColor(187, 185, 185)) # Light Grey
            self.setHorizontalHeaderItem(k, item)
            item.setText(c)
        
        self.setRowCount(len(rows))
        self.blockSignals(True)
        for i, r in enumerate(rows):
            for j, t in enumerate(r):
                item = TableWidgetItemDb(str(t))
                if str(self.horizontalHeaderItem(j).text()) in self.editing_allowed:
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
                else:
                    item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.setItem(i, j, item)
        
        if self.name == 'MODEL' or self.name == 'QUERY':
            self.resizeColumnsToContents()
            self.horizontalHeader().setStretchLastSection(True)
        if self.name == 'RUN':
            for k, v in self.hidden_columns.items():
                self.horizontalHeader().hideSection(v)
                
        self.blockSignals(False)
        self.setSortingEnabled(True)
    

    @QtCore.pyqtSlot()
    def _highlightEditRow(self):
        """Highlightes the calling cell in the View Tables."""
        item = self.currentItem()
        if not item is None:
            row = item.row()
            id = str(self.item(item.row(), self.id_col).text())
            # Need to do this because it keeps calling the slot twice
            if not id in self._unsaved_entries:
                self._unsaved_entries.append(id)
                headercount = self.columnCount()
                for x in range(0,headercount,1):
                    self.item(row, x).setBackgroundColor(QtGui.QColor(178, 255, 102)) # Light Green
                
                
    def saveTableEdits(self): 
        """Save the active edits in the table.
        
        Clears the self._unsaved_entries lists after updating.
        """
        total_updates = 0
        cur_prog = 1
        total_updates += len(self._unsaved_entries)
        self.emit(QtCore.SIGNAL("setRange"), total_updates + 1)
        
        if self._unsaved_entries:
            for row in range(self.rowCount()):
                id = str(self.item(row, self.id_col).text())
                if id in self._unsaved_entries:
                    self.emit(QtCore.SIGNAL("statusUpdate"), 'Updating edit %s of %s' % (cur_prog, total_updates))
                    self.emit(QtCore.SIGNAL("updateProgress"), cur_prog)

                    keep_cells = {}
                    headercount = self.columnCount()
                    for x in range(0,headercount,1):
                        headertext = str(self.horizontalHeaderItem(x).text())
                        if not headertext == 'id':
                            keep_cells[headertext] = str(self.item(row, x).text())
                    
                    if self.name == 'RUN':
                        pv.updateRunRow(keep_cells, int(id))
                    elif self.name == 'MODEL':
                        if self.subname == 'DAT':
                            pv.updateDatRow(keep_cells, id)
                        if self.subname == 'IED':
                            pv.updateIedRow(keep_cells, id)
                        else:
                            pv.updateModelRow(keep_cells, id)
                    
                    cur_prog += 1
                    
        self._unsaved_entries = []
        self.emit(QtCore.SIGNAL("updateProgress"), 0)
        self.emit(QtCore.SIGNAL("statusUpdate"), '')
        self.emit(QtCore.SIGNAL("dbUpdated"))
    
    
    def _deleteRowFromDatabase(self, all_entry):
        """Deletes the row in the database based on the location that the mouse
        was last clicked.
        This is fine because this function is called from the context menu and
        therefore relies on the user right-clicking on the correct row.
        
        Args:
            table(TableWidget): to get the row data from.
            all_entry(bool): if True deletes associated entries as well.
        """
        
        # Get the currently active row in the table and find it's ID value
        row = self.currentRow()
        row_id = str(self.item(row, self.id_col).text())
        
        # Just make sure we meant to do this
        if self.subname == '':
            n = self.name
        else:
            n = self.subname
        
        if self.name == 'RUN':
            if not all_entry:
                message = "Delete RUN entry for ID = %s" % (row_id) 
            else:
                message = "Delete this RUN entry AND all associated entries?\nID = %s" % (row_id)       
            answer = self.launchQtQBox('Confirm Delete?', message)        
            if answer == False:
                return
            
            try:
                self.emit(QtCore.SIGNAL("setRange"), 3)
                self.emit(QtCore.SIGNAL("updateProgress"), 1)
                self.emit(QtCore.SIGNAL("statusUpdate"), 'Deleting Run and Model files ...')
                pv.deleteRunRow(int(row_id), delete_recursive=all_entry)
                self.emit(QtCore.SIGNAL("statusUpdate"), 'Deleting orphaned files ...')
                pv.deleteOrphanFiles(int(row_id))
                self.emit(QtCore.SIGNAL("updateProgress"), 2)
                self.emit(QtCore.SIGNAL("statusUpdate"), 'Recalculating file status ...')
                pv.updateNewStatus()
                self.emit(QtCore.SIGNAL("statusUpdate"), 'Delete complete')
                self.emit(QtCore.SIGNAL("updateProgress"), 0)

            except Exception, err:
                self.emit(QtCore.SIGNAL("statusUpdate"), 'Delete failed')
                self.emit(QtCore.SIGNAL("updateProgress"), 0)
                msg = ('There was an issue deleting some of the components of ' +
                       'this run.\nYou should run the Clean Database tool to ' +
                       'make sure all orphaned files have been removed.')
                self.launchQMsgBox('Database Error', msg)
                logger.exception(err)
          
        else:
            message = "Delete this entry?\nTable = %s, ID = %s" % (self.subname, row_id) 
            answer = self.launchQtQBox('Confirm Delete?', message)    
            if answer == False:
                return
              
            if self.subname == 'DAT':
                pv.deleteDatRow(row_id)
            else:
                pv.deleteModelRow(row_id)
        
        self.emit(QtCore.SIGNAL("dbUpdated"))
    

    def launchQMsgBox(self, title, message, type='warning'):
        """Launch a QMessageBox
        """
        if type == 'warning':
            QtGui.QMessageBox.warning(self, title, message)
        elif type == 'critical':
            QtGui.QMessageBox.critical(self, title, message)
        elif type == 'info':
            QtGui.QMessageBox.information(self, title, message)
    
    def launchQtQBox(self, title, message):
        """Launch QtQMessageBox.
        """
        answer = QtGui.QMessageBox.question(self, title, message,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if answer == QtGui.QMessageBox.No:
            return False
        else:
            return True
    
    
    def addColumn(self):
        """Shows the currently hidden column."""
        sender = str(self.sender().text())
        self.horizontalHeader().showSection(self.hidden_columns[sender])
        del self.hidden_columns[sender]
        
    
    def showHeaderMenu(self, pos):
        """Display the table header context menu.""" 
        
        col = self.horizontalHeader().logicalIndexAt(pos.x())
        menu = QtGui.QMenu()
        hide_action = menu.addAction('Hide column')
        show_menu = menu.addMenu('Show column')
        for h in self.hidden_columns.keys():
            act = show_menu.addAction(h)
            act.triggered.connect(self.addColumn)
            
        action = menu.exec_(self.horizontalHeader().mapToGlobal(pos))
        
        if action == hide_action:
            self.horizontalHeader().hideSection(col)
            self.hidden_columns[str(self.horizontalHeaderItem(col).text())] = col
        
            logger.debug('Hiding header: %s' % col)
                
    def _tablePopup(self, pos):
        """This is the action performed when the user opens the context menu
        with right click on on of the tables in the View Log tab.
        
        Finds out what the user selected from the menu and then performs the
        appropriate action.
        
        Deals with some actions locally. Others are sent to the MainGui by
        emmitting a signal.
        
        Args:
            pos(QPoint): the QPoint of the mouse cursor when clicked.
        """
        index = self.itemAt(pos)
        if index is None: return
        
        menu = QtGui.QMenu()
        
        copyAction = menu.addAction("Copy")
        if not self.name == 'QUERY':
            updateRowsAction = menu.addAction("Save updates")
            deleteRowAction = menu.addAction("Delete row")
            
            # Find who called us and get the object that the name refers to.
            has_run = False
            if self.name == "RUN":
                deleteAllRowAction = menu.addAction("Delete associated entries")
                updateStatusAction = menu.addAction("Update status")
                query_menu = menu.addMenu("Query")
                queryRunDatAction = query_menu.addAction("Dat file")
                queryRunIedAction = query_menu.addAction("Ied files")
                queryRunModelAction = query_menu.addAction("Modelfiles")
                queryRunModelFilesAction = query_menu.addAction("Modelfiles with Subfiles")
                queryRunModelNewAction = query_menu.addAction("Modelfiles - New only")
                queryRunModelFilesNewAction = query_menu.addAction("New Modelfiles with Subfiles")
                paths_menu = menu.addMenu('Update paths')
                updateIefRowAction = paths_menu.addAction("Update Ief location")
                updateTcfRowAction = paths_menu.addAction("Update Tcf location")
                updateLogRowAction = paths_menu.addAction("Update Logs location")
                tools_menu = menu.addMenu('Send to tool')
                extractRowAction = tools_menu.addAction("Extract Model")
                addToRunSummaryAction = tools_menu.addAction("Run Summary")
                has_run = True
        
        has_model = False
        if self.name == 'MODEL' and self.subname != 'DAT' and self.subname != 'IED':
            query_menu = menu.addMenu("Query")
            queryModelFilesAction = query_menu.addAction("Subfiles")
            queryModelFilesNewAction = query_menu.addAction("Subfiles - New only")
            has_model = True
        
        
        # Get the action and do whatever it says
        action = menu.exec_(self.viewport().mapToGlobal(pos))
        if action is None: return
        
        if action == copyAction:
            clipboard = QtGui.QApplication.clipboard()
            clipboard.setText(self.currentItem().text())
            
        elif action == updateRowsAction:
            self.saveTableEdits()
            
        elif action == deleteRowAction:
            self._deleteRowFromDatabase(False)
        
        # These are only available on the MODEL tables
        elif has_model:
            
            if action == queryModelFilesNewAction or action == queryModelFilesAction:
                row = self.currentRow()
                id = str(self.item(row, self.id_col).text())
                self.emit(QtCore.SIGNAL("queryModelTable"), self.subname, str(action.text()), id)
            
        # These are only available on the RUN table
        elif has_run:
            
            if action == queryRunModelFilesNewAction or action == queryRunModelFilesAction or \
                        action == queryRunModelAction  or action == queryRunModelNewAction  or \
                        action == queryRunDatAction or action == queryRunIedAction:
                row = self.currentRow()
                id = str(self.item(row, self.id_col).text())
                self.emit(QtCore.SIGNAL("queryRunTable"), str(action.text()), int(id))
        
            if action == deleteAllRowAction:
                self._deleteRowFromDatabase(True)
            
            # Send model path to ModelExtractor
            # Send log path to RunSummary tool
            elif action == extractRowAction or action == addToRunSummaryAction:
                row = self.currentRow()
                id = str(self.item(row, self.id_col).text())
                self.emit(QtCore.SIGNAL("runTableContextTool"), str(action.text()), id)
            
            # Update IEF_DIR, TCF_DIR, or LOG_DIR
            elif action == updateIefRowAction or action == updateTcfRowAction or action == updateLogRowAction:
                row = self.currentRow()
                id = str(self.item(row, self.id_col).text())
                self.emit(QtCore.SIGNAL("runTableContextPathUpdate"), str(action.text()), id)
                
            # Update the MB and RUN_STATUS values
            elif action == updateStatusAction:
                row = self.currentRow()
                id = str(self.item(row, self.id_col).text())
                self.emit(QtCore.SIGNAL("runTableContextStatusUpdate"), id)
                


class TableWidgetItemDb(QtGui.QTableWidgetItem):
    """Overriddes QTableWidgetItem with Logit specific behaviour."""
    
    def __init__ (self, value):
        super(TableWidgetItemDb, self).__init__(QtCore.QString('%s' % value))

    def __lt__ (self, other):
        """Check order of two values.
        
        Tries to convert the value to a float. If successful it will return 
        the order of those two values. 
        
        If value is not numeric or is not a QCustomTableWidgetItem type it
        will return the standard string compare output.
        
        Args:
            other(QTableWidgetItem): value to compare with that stored by this.
        
        Return:
            Bool - True if given value is less than this.
        """
        if (isinstance(other, TableWidgetItemDb)):
            try:
                self_data_value  = float(self.data(QtCore.Qt.EditRole).toString())
                other_data_value = float(other.data(QtCore.Qt.EditRole).toString())
            except:
                return QtGui.QTableWidgetItem.__lt__(self, other)
            return self_data_value < other_data_value
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)


class TableWidgetDragRows(QtGui.QTableWidget):

    def __init__(self, rows, cols, parent=None):
        QtGui.QTableWidget.__init__(self, rows, cols, parent)
    
        
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection) 
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.setDragEnabled(True)  
        self.setSortingEnabled(False)
        
    
    def dropEvent(self, event):
        if event.source() == self and (event.dropAction() == QtCore.Qt.MoveAction or self.dragDropMode() == QtGui.QAbstractItemView.InternalMove):
            
            success, row, col, topIndex = self.dropOn(event)
            if success:             
                selRows = self.getSelectedRowsFast()

                top = selRows[0]
                dropRow = row
                if dropRow == -1:
                    dropRow = self.rowCount()
                offset = dropRow - top

                for i, row in enumerate(selRows):
                    r = row + offset
                    if r > self.rowCount() or r < 0:
                        r = 0
                    self.insertRow(r)


                selRows = self.getSelectedRowsFast()

                top = selRows[0]
                offset = dropRow - top                
                for i, row in enumerate(selRows):
                    r = row + offset
                    if r > self.rowCount() or r < 0:
                        r = 0

                    for j in range(self.columnCount()):
                        source = QtGui.QTableWidgetItem(self.item(row, j))
                        self.setItem(r, j, source)

                event.accept()
            
                

        else:
            QtGui.QTableView.dropEvent(event)                


    def getSelectedRowsFast(self):
        selRows = []
        for item in self.selectedItems():
            if item.row() not in selRows:
                selRows.append(item.row())
        return selRows


    def droppingOnItself(self, event, index):
        dropAction = event.dropAction()

        if self.dragDropMode() == QtGui.QAbstractItemView.InternalMove:
            dropAction = QtCore.Qt.MoveAction

        if event.source() == self and event.possibleActions() & QtCore.Qt.MoveAction and dropAction == QtCore.Qt.MoveAction:
            selectedIndexes = self.selectedIndexes()
            child = index
            while child.isValid() and child != self.rootIndex():
                if child in selectedIndexes:
                    return True
                child = child.parent()

        return False


    def dropOn(self, event):
        if event.isAccepted():
            return False, None, None, None

        index = QtCore.QModelIndex()
        row = -1
        col = -1

        if self.viewport().rect().contains(event.pos()):
            index = self.indexAt(event.pos())
            if not index.isValid() or not self.visualRect(index).contains(event.pos()):
                index = self.rootIndex()

        if self.model().supportedDropActions() & event.dropAction():
            if index != self.rootIndex():
                dropIndicatorPosition = self.position(event.pos(), self.visualRect(index), index)

                if dropIndicatorPosition == QtGui.QAbstractItemView.AboveItem:
                    row = index.row()
                    col = index.column()
                elif dropIndicatorPosition == QtGui.QAbstractItemView.BelowItem:
                    row = index.row() + 1
                    col = index.column()
                else:
                    row = index.row()
                    col = index.column()

            if not self.droppingOnItself(event, index):
                return True, row, col, index

        return False, None, None, None


    def position(self, pos, rect, index):
        r = QtGui.QAbstractItemView.OnViewport
        margin = 2
        if pos.y() - rect.top() < margin:
            r = QtGui.QAbstractItemView.AboveItem
        elif rect.bottom() - pos.y() < margin:
            r = QtGui.QAbstractItemView.BelowItem 
        elif rect.contains(pos, True):
            r = QtGui.QAbstractItemView.OnItem

        if r == QtGui.QAbstractItemView.OnItem and not (self.model().flags(index) & QtCore.Qt.ItemIsDropEnabled):
            r = QtGui.QAbstractItemView.AboveItem if pos.y() < rect.center().y() else QtGui.QAbstractItemView.BelowItem

        return r
    


def getModelFileLocation(multi_paths, last_model_directory,
                                        cur_log_path, cur_settings_path):
    """Launch dialog for user to choose model to load.
    :param param: 
    """
    # Create a file dialog with an initial path based on the availability
    # of path variables.
    d = MyFileDialogs()
    if not last_model_directory == '' and \
                    not last_model_directory == False:
        chosen_path = last_model_directory
    elif not cur_log_path == ''  and not cur_log_path == False:
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
    """Container for errors logged for later use.
    """
    
    def __init__(self):
        self.reset()
        
    
    def addError(self, key, msg_add='', change_status=False,
                                                msgbox_error=False):
        """Adds a new error to the log list.
        :param key: the key to the error. If this doesn't exist it will raise a 
               KeyError. If you want to create a new type of error either add 
               it to the _initErrorTypes function or call addErrorType with an 
               ErrorType object if you only want it at run time.
        :param message_additional='': Any additional text to add to the error.
        :param change_status=False: If set to True the message_additional text
               will be added to the status text as well.
        """
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
        """Return the message from the error logs formatted as text.
        Takes the message from each of the ErrorType objects stored in the
        self.log and combines them into a single formatted text string.
        :param prologue: string containing any text that should be prepended
               to the output text.
        :return: string of formatted log messages.
        """
        if len(self.log) < 1:
            return ''
        else:
            out_err = []
            for l in self.log:
                out_err.append(l.message)
            out_err = '\n\n'.join(out_err)
            return out_err
        
    
    def addErrorType(self, error_type, key):
        """Adds a new ErrorType to the self.types dictionary.
        :param error_type: The ErrorType object to add.
        :param key: the key to use to access the error_type.
        """
        self.types[key] = error_type
        
    
    def reset(self):
        self.log = []
        self.msgbox_error = None
        self.types = self._initErrorTypes()
        self.has_errors = False
        self.has_local_errors = False
    
    
    def _initErrorTypes(self):
        """Initialise all of the available error types.
        """
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
        self.EXTRACT_MODEL = 'Extract Model Error'
        self.USER_CANCEL = 'User Cancelled File Error'
            
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
        
        #
        title = self.EXTRACT_MODEL
        status_bar = 'Extract Model Failed '
        message = 'Unable to extract model '
        errors[title] = ErrorType(title, status_bar, message)

        #
        title = self.USER_CANCEL
        status_bar = ''
        message = 'User cancelled file dialog. '
        errors[title] = ErrorType(title, status_bar, message)

        return errors


class ErrorType(object):
    """Holds details of error types for use in ErrorHolder.
    """
    
    def __init__(self, title, status_bar, message=None):        
        self.error_found = False
        self.title = title
        self.status_bar = status_bar
        if message == None:
            self.message = status_bar
        else:
            self.message = message


class VersionInfoDialog(QtGui.QDialog):
    """Dialog class for showing release information."""
    
    def __init__(self, release_dir, version, parent=None):
        super(VersionInfoDialog, self).__init__(parent)
        
        self.release_dir = release_dir + version + '.txt'
        self.version = version

        self.textBrowser = QtGui.QTextBrowser(self)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.textBrowser)
        
        output = []
        output.append(self.getOpeningRichText())
        output.extend(self.getReleaseNotes())
        output.append(self.getClosingRichText())
        output = ''.join(output)
        self.textBrowser.setText(output)
    

    def getReleaseNotes(self):
        """
        """
        out = []
        input = []
        try:
            with open(self.release_dir, 'rb') as f:
                lines = f.readlines()
                for l in lines:
                    input.append(l.strip())
#                     output.append(self.getStandardParagraphIn() + l.rstrip() + self.getStandardParagraphOut())
        except:
            self.textBrowser.append('Failed to load release notes from server')
            out.append('\nFailed to load release notes from server')
            return out
        
        input = ' '.join(input)
        input = input.split('-')
        for i in input:
            out.append(self.getStandardParagraphIn() + i.rstrip() + self.getStandardParagraphOut())
        
        return out
    
    
    def getStandardParagraphIn(self):
        """
        """
        return '''
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
<span style=" font-size:10pt;">
<li>
'''


    def getStandardParagraphOut(self):
        """
        """
        return '</li></span></p>'
    

    def getOpeningRichText(self):
        """
        """
        return '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'Arial'; font-size:10pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><img src=":/icons/images/Logit_Logo2_75x75.png" /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:14pt; font-weight:600; color:#0055ff;">LogIT ''' + self.version + '''</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600; text-decoration: underline;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:11pt; font-weight:600; text-decoration: underline;">Updates in this release</span></p>
<ul>
'''
        
    def getClosingRichText(self):
        """
        """
        return '</ul></body></html>'
    
    