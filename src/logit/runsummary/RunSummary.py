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


 Module:          RunSummary.py 
 Date:            26/04/2016
 Author:          Duncan Runnacles
 Since-Version:   0.7
 
 Summary:
     Displays the current status and key variables of a tuflow simulation by
     reading a tuflow .tlf file. Presents the outputs of the file contents in
     a graph and a table.

 UPDATES:
    

 TODO:
    

###############################################################################
"""

import logging
logger = logging.getLogger(__name__)

import os
import uuid
# import datetime
import math
import time
import re

from PyQt4 import QtCore, QtGui
import pyqtgraph as pg

from ship.utils.filetools import MyFileDialogs
from ship.utils.fileloaders import fileloader as fl

from AWidget import AWidget
import RunSummary_Widget as summarywidget
logger.debug('RunSummary_Widget import complete')
# from app_metrics import utils as applog
import globalsettings as gs


class RunformLabel(QtGui.QLabel):
    """Used to display the FMP runform diagnostics graphic."""
    
    def __init__(self, title='Some Model', parent=None, f=QtCore.Qt.WindowFlags()):
        """
        Args:
            title(str): window title.
        """
        QtGui.QLabel.__init__(self, '', parent, f)
        QtGui.QWidget.setWindowTitle(self, title)
    
    def refreshGraph(self, bmp_path):
        """Update the graph displayed."""
        pixmap = QtGui.QPixmap(bmp_path)
        self.setPixmap(pixmap)

    
    def closeEvent(self, event):
        """Custom window close event."""
        self.emit(QtCore.SIGNAL("closingForm"))
        event.ignore()


class RunSummary_UI(summarywidget.Ui_RunSummaryWidget, AWidget):
    

    def __init__(self, cwd, parent=None, f=QtCore.Qt.WindowFlags()):
        
        AWidget.__init__(self, 'Run Summary', cwd, parent, f)
        pg.setConfigOption('background', 'w')  # Background = White
        pg.setConfigOption('foreground', 'k')  # Axis & Labels = Black
        self.setupUi(self)
        self.runStatusTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self._setupPlot()
        
        # Connect the slots
        self.tlfAddButton.clicked.connect(self._loadLogFile)
        self.runStatusTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.runStatusTable.customContextMenuRequested.connect(self._tablePopup)
        self.runStatusTable.cellClicked.connect(self._activateRow)
        self.updateAllStatusButton.clicked.connect(self._updateAllStatus)
        self.autoUpdateButton.clicked.connect(self._autoUpdateEntry)
        self.showFmpRunCbox.stateChanged.connect(self._updateShowRunformStatus)
        
        # Keyboard shortcuts
        self.updateAllStatusButton.setToolTip('Update all entries in table (Ctrl-G)')
        self.updateAllStatusButton.setShortcut(QtCore.Qt.SHIFT + QtCore.Qt.Key_F5)
        self.tlfAddButton.setToolTip('Add a new log file to the table (Ctrl-T)')
        self.tlfAddButton.setShortcut("Ctrl+T")
        
        self.mMin = -10
        self.mMax = 10
        self.cur_guid = ''
        self.do_auto = False
        self.timer = None
        self.showFmpRunform = True
        self.runformLabel = None
    
    
    def _updateShowRunformStatus(self):
        self.showFmpRunform = self.showFmpRunCbox.isChecked()
        
    
    def keyPressEvent(self, event):
        """Catch keypress events fo updating the entry."""
        if type(event) == QtGui.QKeyEvent:
            
            if event.key() == QtCore.Qt.Key_F5:
                for i, entry in enumerate(self.settings['log_summarys']):
                    if entry.row_values['GUID'] == self.cur_guid:
                        self._updateEntry(entry, i)
            
    
    def _setupPlot(self):
        """Setups up the main layout and viewboxes for the graph.
        
        Creates three ViewBox's for the cross section, conveyance and mannings.
        All other data series are added to one of these.
        """
        self.p1 = self.simGraphGraphics.plotItem
        self.p1.setLabels(left=('Flow In & Flow Out'), bottom=('Time', 'h'), right='MB & DDV')
        self.p1.vb.menu.triggered.connect(self.myAutoRange)
        self.p1.autoBtn.clicked.connect(self.myAutoRange)
        
        # create second ViewBox for mannings data 
        self.p2 = pg.ViewBox(name='MB')
        self.p1.showAxis('right')
        self.p1.scene().addItem(self.p2)
        self.p1.getAxis('right').linkToView(self.p2)
        self.p2.setXLink(self.p1)
        
        self.updateViews()
        self.p1.vb.sigResized.connect(self.updateViews)
        self.p1.vb.scaleBy = self.scaleBy
    
    
    def _tablePopup(self, pos):
        """Called by items on the right-click context menu."""
        index = self.runStatusTable.itemAt(pos)
        if index is None: return

        menu = QtGui.QMenu()
        updateEntryAction = menu.addAction("Update Entry")
        deleteEntryAction = menu.addAction("Remove Entry")
        reloadRunAction = menu.addAction("Reload Run")
        runformAction = menu.addAction('Show latest FMP Runform')

        # Find who called us and get the object that the name refers to.
        sender = self.sender()
        sender = str(sender.objectName())
        
        # Get the action and find the associated entry by guid code
        action = menu.exec_(self.runStatusTable.viewport().mapToGlobal(pos))
        row = self.runStatusTable.currentRow()
        guid = str(self.runStatusTable.item(row, 0).text())
        logger.debug('Selected GUID = ' + guid)
        entry = None
        for log in self.settings['log_summarys']:
            if log.row_values['GUID'] == guid:
                entry = log
                break
        if entry is None: return
                
        # Remove an item from the table
        if action == deleteEntryAction or action == runformAction:
            self._closeLabel()
            entry_i = -1
            for i, log in enumerate(self.settings['log_summarys']):
                if log.row_values['GUID'] == entry.row_values['GUID']: 
                    entry_i = i
                    break

            if action == deleteEntryAction:
                self.runStatusTable.removeRow(row) 
                if not entry_i == -1: del self.settings['log_summarys'][entry_i]
                try:
                    os.remove(entry.stored_datapath)
                except IOError:
                    logger.warning('Unable to find cache file - may not exist or might need deleting manually')
                entry = None
                self.p1.clear()
                self.p2.clear()
            elif action == runformAction:
                try:
                    self._addRunformWindow(
                            self.settings['log_summarys'][entry_i].runform_path,
                            ignore_check_status=True)
                except: pass
        
        # Re-reads a file from scratch
        if action == reloadRunAction:
            self._reloadRun(entry, row)
                
        # Reads a file starting from the location of the last read.
        if action == updateEntryAction:
            self._updateEntry(entry, row)
    
    
    def _reloadRun(self, entry, row):
        """Completely reload the selected run.
        
        Instead of just updating from where we last left off it reloads it
        from the start of the file.
        
        Args:
            entry(LogSummaryEntry): with details for this run.
            row(int): the row in the run summary table to update.
        """
        open_path = os.path.join(self.data_dir, entry.row_values['GUID'] + '.dat')
        log_store = self._loadFromCache(open_path)
        try:
            runform_path = log_store.runform_path
        except: runform_path = None
        self.cur_guid = log_store.guid
        details = []
        for i, log in enumerate(self.settings['log_summarys']):
            if log.row_values['GUID'] == entry.row_values['GUID']: 
                details = [log.row_values['GUID'], log.row_values['NAME'],
                          log.tlf_path, i]
                break

        if details:
            try:
                self.emit(QtCore.SIGNAL("statusUpdate"), 'Loading file into table ...')
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                entry = LogSummaryEntry(details[0], details[1], self.data_dir, details[2])
                entry, log_store = self._loadLogContents(entry, details[2])
                if not runform_path is None:
                    entry.runform_path = runform_path
                    log_store.runform_path = runform_path
                    self._addRunformWindow(entry.runform_path)
                self.emit(QtCore.SIGNAL("statusUpdate"), 'Saving to cache ...')
                self._saveToCache(log_store, entry.stored_datapath)
                self._updateTableVals(entry, details[3]) # -1
                self._updateGraph(log_store, entry.row_values['NAME'])
                
                self.settings['log_summarys'][details[3]] = entry
            except Exception, err:
                logger.error('Problem loading model')
                logger.exception(err)
            finally:
                self.emit(QtCore.SIGNAL("statusUpdate"), '')
                self.emit(QtCore.SIGNAL("setRange"), 1)
                self.emit(QtCore.SIGNAL("updateProgress"), 0)
                QtGui.QApplication.restoreOverrideCursor()
    
    
    def _stopAutoUpdate(self):
        """Stops the automatic run update from running.
        
        Does a little clean up to make sure everything is reset properly.
        """
        self.autoUpdateButton.setText('Auto Update Active Run')
        self.emit(QtCore.SIGNAL("statusUpdate"), 'Run auto update stopped')
        self.emit(QtCore.SIGNAL("setRange"), 1)
        self.emit(QtCore.SIGNAL("updateProgress"), 0)
        QtGui.QApplication.restoreOverrideCursor()
        self.do_auto = False
        if not self.timer is None:
            self.timer.stop()
        
    
    def _autoUpdateEntry(self):
        """Automatically updates the currently active run.
        
        Launches a QTimer than continuously calls the runLoop function to
        check if the run's finished and if not update the status.
        """
        def runLoop():
            """QTimer function to auto update currently selected entry."""
            if entry.row_values['STATUS'] == 'Complete' or entry.row_values['STATUS'] == 'Failed' or entry.row_values['STATUS'] == 'Interrupted':
                self._stopAutoUpdate()
            self._updateEntry(entry, cur_row)
            
            
        if str(self.autoUpdateButton.text()) == 'Stop Update':
            self._stopAutoUpdate()
            return

        cur_row = self.runStatusTable.currentRow()
        if cur_row == -1:
            self.launchQMsgBox('Selection Error', 'Click on the required entry first')
            return
        
        guid = str(self.runStatusTable.item(cur_row, 0).text())
        for log in self.settings['log_summarys']:
            if log.row_values['GUID'] == guid:
                entry = log
                break
        if entry is None: return
        
        if entry.row_values['STATUS'] == 'Complete' or entry.row_values['STATUS'] == 'Failed' or entry.row_values['STATUS'] == 'Interrupted':
            return
        
        self.autoUpdateButton.setText('Stop Update')
        self.emit(QtCore.SIGNAL("statusUpdate"), 'Auto updating run ...')
        self.do_auto = True
        self._updateEntry(entry, cur_row)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(runLoop)
        self.timer.start(3000)
        
    
    def _updateEntry(self, entry, row):
        """Update the run summary entry at the given row.
        
        Continues to read from the .tlf file at the point where it last 
        finished checking.
        
        Args:
            entry(LogSummaryEntry): with details for this run.
            row(int): the row in the run summary table to update.
        """
        open_path = os.path.join(self.data_dir, entry.row_values['GUID'] + '.dat') 
        log_store = self._loadFromCache(open_path)
        self.cur_guid = log_store.guid
        try:
            runform_path = log_store.runform_path
        except: runform_path = None
        if not entry.row_values['STATUS'] == 'Complete' and not entry.row_values['STATUS'] == 'Failed' and not entry.row_values['STATUS'] == 'Interrupted':
            try:
                if not self.do_auto: # Stop tons of rubbish in logs
                    self.emit(QtCore.SIGNAL("statusUpdate"), 'Loading file into table ...')
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                entry, log_store = self._loadLogContents(entry, entry.tlf_path, log_store)
                if not self.do_auto:
                    self.emit(QtCore.SIGNAL("statusUpdate"), 'Saving to cache ...')
                self._saveToCache(log_store, entry.stored_datapath)
            except Exception, err:
                logger.error('Problem loading model: ' + err)
            finally:
                if not self.do_auto:
                    self.emit(QtCore.SIGNAL("statusUpdate"), '')
                    self.emit(QtCore.SIGNAL("setRange"), 1)
                    self.emit(QtCore.SIGNAL("updateProgress"), 0)
                QtGui.QApplication.restoreOverrideCursor()
        else:
            if not runform_path is None and not self.do_auto:
                self._addRunformWindow(runform_path)

        entry_i = -1
        for i, log in enumerate(self.settings['log_summarys']):
            if log.row_values['GUID'] == entry.row_values['GUID']: 
                entry_i = i
                break
        if not entry_i == -1: self.settings['log_summarys'][entry_i] = entry
            
        self._updateTableVals(entry, row)
        self._updateGraph(log_store, entry.row_values['NAME'])
        
        
  
    def _updateAllStatus(self):
        """Updates all of the files in the table.
        
        Reads additional data from the file from the point where reading stopped
        the last time.
        """
        logger.debug("Updating all status'")
        log_store = None
        length = len(self.settings['log_summarys'])
        try:
            self.emit(QtCore.SIGNAL("setRange"), length)
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            for i, log in enumerate(self.settings['log_summarys']):
                self.emit(QtCore.SIGNAL("updateProgress"), i)
                self.emit(QtCore.SIGNAL("statusUpdate"), 'Updating row %s of %s' % (i+1, length))
                open_path = os.path.join(self.data_dir, log.row_values['GUID'] + '.dat')
                log_store = self._loadFromCache(open_path)
                self.cur_guid = log_store.guid
                
                # If the run is finished don't read anymore
                if log.row_values['STATUS'] == 'Complete' or log.row_values['STATUS'] == 'Failed' or log.row_values['STATUS'] == 'Interrupted':
                    entry = log
                else:
                    entry, log_store = self._loadLogContents(log, log.tlf_path, log_store)
                    self._saveToCache(log_store, entry.stored_datapath)

                self._updateTableVals(entry, i)
                self.settings['log_summarys'][i] = entry

        except Exception, err:
            logger.error('Problem Updating one of the models: ' + err)
        finally:
            self.emit(QtCore.SIGNAL("statusUpdate"), '')
            self.emit(QtCore.SIGNAL("setRange"), 1)
            self.emit(QtCore.SIGNAL("updateProgress"), 0)
            QtGui.QApplication.restoreOverrideCursor()
            
        if not log_store is None: self._updateGraph(log_store, entry.row_values['NAME'])
        
    
    def _activateRow(self, row, col):
        """Sets the row at the given locations to be active.
        
        Loads the LogSummaryStore data from cache using the guid stored in the
        table row. Then updates the graph with the contents.
        """
        self._stopAutoUpdate()
        
        guid = str(self.runStatusTable.item(row, 0).text())
        if self.cur_guid == guid: return
        try:
            self.emit(QtCore.SIGNAL("statusUpdate"), 'Loading from cache ...')
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
#             self.runStatusTable.selectRow(row)
            guid = str(self.runStatusTable.item(row, 0).text())
            open_path = os.path.join(self.data_dir, guid + '.dat')
            log_store = self._loadFromCache(open_path)
            self.cur_guid = log_store.guid
            self._updateGraph(log_store, str(self.runStatusTable.item(row, 1).text()))
            self._setActiveRowStyle(row)
            
            status = str(self.runStatusTable.item(row, 4).text())
            if status == 'Complete' or status == 'Failed' or status == 'Interrupted':
                if not self.runformLabel is None:
                    self._closeLabel()
                try:
                    if not log_store.runform_path is None:
                        self._addRunformWindow(log_store.runform_path)
                except: pass
        except Exception, err:
            logger.error('Problem loading cache')
            logger.exception(err)
        finally:
            self.emit(QtCore.SIGNAL("statusUpdate"), '')
            self.emit(QtCore.SIGNAL("updateProgress"), 0)
            QtGui.QApplication.restoreOverrideCursor()
    
    
    def _setActiveRowStyle(self, row_no):
        """Set the style for the active row based on status."""
        row_count = self.runStatusTable.rowCount()
        if row_no > row_count:
            row_no = row_count
        
        for row in range(self.runStatusTable.rowCount()):
            for col in range(self.runStatusTable.columnCount()-1):
                
                item = self.runStatusTable.item(row, col)
                if row == row_no:
                    item.setFont(QtGui.QFont('Arial', 9, QtGui.QFont.Bold))
                else:
                    item.setFont(QtGui.QFont('Arial', 9, QtGui.QFont.Normal))
    
    
    def _loadRunform(self, results_path):
        """Find the latest .bmp runform graphic for this result path and load it.
        
        Checks all of the files in the folder and collects the ones that contain
        the filename stipulated by the results directory. It then sorts these
        to find the latest version (e.g. finename_003.bmp).
        
        Args:
            results_path(str): path to the results folder from the ief file.
        
        Return:
            str - path of the most recent run form diagnostics graph (.bmp)
        """
        path, name = os.path.split(results_path)
        file_list = os.listdir(path)
        
        bmps = []
        for f in file_list:
            parts = f.split(name)
            # If it's only the filename matched exactly
            if len(parts) < 2:
                continue
            # If second part is the start of the extension
            if parts[1].startswith('.'):
                if parts[1][1:] == 'bmp':
                    bmps.append(f)
                continue
            subparts = parts[1].split('.')
            if len(subparts) < 2:
                continue
            # If the extra bit before extension is an '_' followed by three
            # numbers (matches isis run output .bmp's)
            if re.match(r'[_]\d{3}', subparts[0]):
                bmps.append(f)
        
        if not bmps: 
            return False
        else:
            # Order by the last number and take the latest one
            bmps = sorted(bmps)
            return os.path.join(path, bmps[-1])
        

    def loadIntoTable(self, tlf_path, isis_path=None):
        """Loads a .tlf file and updates the table and graph with the contents.
        
        Creates LogSummaryInfo and LogEntry objects and loads them with data
        read from the .tlf file. Then activates the new table row and displays
        the loaded data into the graph.
        
        Args:
            tlf_path(str): path to a tlf file.
        """
        logger.debug('Load into table clicked')
        if not os.path.exists(tlf_path):
            self.launchQMsgBox(('Nonexistant tlf', 'TLF file does not exist ' +
                                'at:\n' + tlf_path))
            return
        for log in self.settings['log_summarys']:
            if log.tlf_path == tlf_path:
                self.launchQMsgBox('Load Error', ('This log file has already ' +
                                                 'been loaded into the table\n' +
                                                 'Either update the row or ' +
                                                 'remove and re-add it.'))
                return
        
        run_name = os.path.splitext(os.path.split(tlf_path)[1])[0]
        guid = str(uuid.uuid4())
        entry = LogSummaryEntry(guid, run_name, self.data_dir, tlf_path)
        if not isis_path is None:
            runformpath = self._loadRunform(isis_path)
            if not runformpath == False:
                entry.runform_path = isis_path
        
        try:
            self.emit(QtCore.SIGNAL("statusUpdate"), 'Loading file into table ...')
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            entry, log_store = self._loadLogContents(entry, tlf_path)
            self.emit(QtCore.SIGNAL("statusUpdate"), 'Saving to cache ...')
#             self._saveToCache(log_store, entry.stored_datapath)
            self.settings['log_summarys'].append(entry)
            self.emit(QtCore.SIGNAL("statusUpdate"), 'Updating graph and table ...')
            self._updateTableVals(entry)
            self._updateGraph(log_store, entry.row_values['NAME'])

            if not entry.runform_path == False:
#                 self._addRunformWindow(entry.runform_path)
                log_store.runform_path = entry.runform_path
                status = entry.row_values['STATUS']
                if status == 'Complete' or status == 'Failed' or status == 'Interrupted':
                    self._addRunformWindow(entry.runform_path)
            self._saveToCache(log_store, entry.stored_datapath)
            self.cur_guid = log_store.guid
            
        except Exception as err:
            logger.error('Problem loading model: ')
            logger.exception(err)
        finally:
            self.emit(QtCore.SIGNAL("setRange"), 1)
            self.emit(QtCore.SIGNAL("statusUpdate"), '')
            self.emit(QtCore.SIGNAL("updateProgress"), 0)
            QtGui.QApplication.restoreOverrideCursor()
    
    
    def _closeLabel(self):
        """Gracefully shutdown to 1d runform graphics window."""
        try:
            del self.runformLabel
            self.runformLabel = None
        except:
            logger.info('No runform label to close')
    
        
    def _addRunformWindow(self, results_path, ignore_check_status=False):
        """Opens up a new window with the 1d runform graphics in it.
        
        Args:
            results_path(str): path to the results directory(from ief).
            ignore_check_status=False(Bool): if True it will launch the 
                window regardless of whether the checkbox status says to or not.
        """
        if not ignore_check_status and not self.showFmpRunform: return
        
        bmp_path = self._loadRunform(results_path)
        if bmp_path == False: return
        name = os.path.basename(bmp_path)
        if not self.runformLabel is None:
            self.runformLabel.refreshGraph(bmp_path)
            self.runformLabel.show()
        else:
            self.runformLabel = RunformLabel(title=name, f=QtCore.Qt.WindowStaysOnTopHint) 
            self.runformLabel.refreshGraph(bmp_path)
            self.runformLabel.show()
            self.connect(self.runformLabel, QtCore.SIGNAL("closingForm"), self._closeLabel)
        
        
    
    def _updateTableVals(self, summary_obj, row_no=-1):
        """Loads the values of the LogSummaryEntry into the table.
        
        Calculates progress through the run based on the current timestep read
        from the file and the start and finish times and displays in the 
        progress bar.
        
        Colors the row green, red, or neutral based on a successful, failed
        or ongoing run.
        
        Args:
            summary_obj(LogSummaryEntry): containing the summary info from 
                reading the .tlf file.
            row_no=-1(int): the row to update. If no value given or the value
                given is higher than the number of rows it will be added to the
                end of the table.
        """
        row_count = self.runStatusTable.rowCount()
        if row_no == -1 or row_no > row_count:
            self.runStatusTable.setRowCount(row_count + 1)
            row_no = row_count
        
        status = summary_obj.row_values['STATUS']
        for col in range(self.runStatusTable.columnCount()):
            header = str(self.runStatusTable.horizontalHeaderItem(col).text())
            val = summary_obj.row_values[header]
            
            if header == 'COMPLETION':
                prog = QtGui.QProgressBar()
                finish_time = summary_obj.finish_time
                if int(finish_time) == 0 and int(summary_obj.start_time) == 0:
                    finish_time = 1
                
                # * 100 so if updates more frequently for low numbers
                prog.setMaximum(int(finish_time * 100))
                prog.setMinimum(int(summary_obj.start_time))
                prog.setValue(int(val * 100))
                self.runStatusTable.setCellWidget(row_no, col, prog)
            else:
                item = QtGui.QTableWidgetItem(str(val))
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled) 
                if status == 'Failed' or status == 'Interrupted':
                    item.setBackgroundColor(QtGui.QColor(255, 204, 204)) # Light Red
                    item.setFont(QtGui.QFont('Arial', 9, QtGui.QFont.Bold))
                elif status == 'Complete':
                    item.setBackgroundColor(QtGui.QColor(204, 255, 153)) # Light green
                    
                self.runStatusTable.setItem(row_no, col, item)
        self._setActiveRowStyle(row_no)
#         self.runStatusTable.selectRow(row_no)
          
    
    def getHoursFromDateStr(self, date_str):
        """Convert a time code in string format to hours in float format.
        
        Takes a time string of format HH:MM:SS or H:MM:SS and converts it to 
        total hours (e.g. 12.3453).
        
        Args:
            date_str(str): representing a time code.
        
        Return:
            tuple(float, datetime.time) - total hours between date_str and 0
                and the time struct created with strptime.
        
        Raises:
            ValueError: if date_str is not in the expected format.
        """
        if '24:00:00' in date_str: 
            i=0
        time = None
        if date_str[1] == ':': date_str = '0' + date_str
        try:
            time = date_str.split(':')
            hours = float(time[0])
            minutes = float(time[1])
            seconds = float(time[2])
        except ValueError:
            raise
        hours_in_mins = hours * 60
        hours = (hours_in_mins + minutes) / 60
        return hours, minutes, seconds
        
        
    def _loadLogContents(self, entry, tlf_path, log_store=None):
        """Reads the contents of a tlf file.
        
        Creates or updates a LogSummaryInfo object to store the values in the
        tlf run details file.
        
        Searches for the start and finish time info near the top of the file
        and then reads the output data from the run to extract the flow, ddv
        and mb values.
        
        if the log_store contains a cur_row value the loader will skip the
        parts of the file previous to that row and continue the load from 
        that point.
        """
        if not log_store is None:
            own_log = True
            start_time = log_store.start_time
            end_time = log_store.finish_time
        else:
            log_store = LogSummaryStore(entry.row_values['GUID'])
            own_log = False
            start_time = 0
            end_time = 1
        cur_row = 0

        try:
            with open(tlf_path, 'rb') as f:
                for line in f:
                    
                    if cur_row == 353:
                        i=0
                        
                    # Skip row if lower than previous visit
                    if own_log and (cur_row < entry.cur_row):
                        cur_row += 1
                        continue
                    else:
                        cur_row += 1
                    
                    # Find the start and finish times first
                    if not entry.in_results:
                        if line.startswith('Start Time (h):'):
                            start_time = float(line[22:34].strip())
                        if line.startswith('Finish Time (h):'):
                            end_time = float(line[22:34].strip())
                            self.emit(QtCore.SIGNAL("setRange"), math.fabs(end_time - start_time))

                        elif '..... Running' in line:
                            entry.in_results = True
                        
                        elif line.startswith('ERROR') or ': ERROR' in line:
                            entry.error = True
                            break
                
                    # Then load the simulation data
                    else:
                        # Break out when certain keywords are found
                        if 'Writing Output' in line: continue
                        if line.strip() == '': continue
                        if 'Run Finished' in line:
                            end_diff = end_time - entry.last_recorded_time
                            if end_diff > 1:
                                entry.error = True
                            else:
                                entry.finished = True
                            self.emit(QtCore.SIGNAL("updateProgress"), end_time)
                            break
                        if 'Run Interrupted' in line:
                            entry.interrupted = True
                            self.emit(QtCore.SIGNAL("updateProgress"), end_time)
                            break
                        if 'ERROR' in line:
                            entry.error = True
                            self.emit(QtCore.SIGNAL("updateProgress"), end_time)
                            break
                        
                        # Convert time to total in hours
                        try:
                            time = line[7:16].strip()
                            hours, minutes, seconds = self.getHoursFromDateStr(time)
                        except (ValueError, IndexError):
                            continue
                        if math.fabs(hours - entry.last_recorded_time) > 0.25:
                            #temp = math.fabs(start_time + hours)
                            if not self.do_auto:
                                self.emit(QtCore.SIGNAL("updateProgress"), math.fabs(start_time + hours))
                            entry.last_recorded_time = hours
                                                
                        # MB can be printed as ***** if greater than 100
                        mb = line[61:67].strip('%')
                        if '***' in mb:
                            mb = 99
                        else:
                            mb = float(mb) 
                        Qin = float(line[83:89])
                        Qout = float(line[93:99])
                        ddv = float(line[103:109])
                        
                        # Calc max ddv and mb (can be either a highest or
                        # lowest value so find absolute)
                        record = False
                        if math.fabs(mb) > math.fabs(entry.row_values['MAX_MB']):
                            entry.row_values['MAX_MB'] = mb
                            record = True
                        if math.fabs(ddv) > math.fabs(entry.row_values['MAX_DDV']):
                            entry.row_values['MAX_DDV'] = ddv
                            record = True
                        
                        # Add values to store
                        if seconds % 10 == 0:
                            record = True
                        
                        if record:
                            log_store.time_steps.append(hours)
                            log_store.mb.append(mb)
                            log_store.flow_in.append(Qin)
                            log_store.flow_out.append(Qout)
                            log_store.ddv.append(ddv)
                
        except IOError:
            logger.error('Unable to open log file at:\n' + tlf_path)
            entry.row_values['STATUS'] = 'Unfindable'
        
        # Set the appropriate status
        if entry.finished:
            entry.row_values['COMPLETION'] = end_time
            entry.row_values['STATUS'] = 'Complete'
        elif entry.interrupted:
            if not log_store.time_steps:
                entry.row_values['COMPLETION'] = 0
            else:
                entry.row_values['COMPLETION'] = log_store.time_steps[-1]
            entry.row_values['STATUS'] = 'Interrupted'
        
        elif entry.error:
            if not log_store.time_steps:
                entry.row_values['COMPLETION'] = 0
            else:
                entry.row_values['COMPLETION'] = log_store.time_steps[-1]
            entry.row_values['STATUS'] = 'Failed'
        else:
            if entry.in_results:
                entry.row_values['COMPLETION'] = log_store.time_steps[-1]
            entry.row_values['STATUS'] = 'In Progress'
        
        # Set start finish times from existing or newly found
        if own_log:
            entry.start_time = log_store.start_time
            entry.finish_time = log_store.finish_time
        else:
            log_store.start_time = entry.start_time = start_time
            log_store.finish_time = entry.finish_time = end_time
        entry.cur_row = cur_row

        return entry, log_store
            
        
    def _loadLogFile(self):
        """Launch dialog and load a tlf file.
        
        Launches a dialog to get the tlf file from the user.
        """
        path = self.cur_location
        if not self.settings['tlf_path'] == '':
            path = self.settings['tlf_path']
        elif 'model' in gs.path_holder.keys():
            path = gs.path_holder['model']
        d = MyFileDialogs(parent=self)
        open_path = d.openFileDialog(path, file_types='Tuflow log file (*.tlf)')
        if open_path == 'False' or open_path == False:
            return
        self.settings['tlf_path'] = open_path
        self.loadIntoTable(open_path)
    
    
    def myAutoRange(self):
        """Extends the autoBtnClicked functionality of PlotItem.
        
        Need to make sure that the other viewboxes are reset to the required
        extents after a reset.
        
        Calls the autoBtnClicked function afterwards.
        """
        self.p2.setYRange(self.mMin, self.mMax)
        self.p1.autoBtnClicked()
        
        
    def scaleBy(self, *args, **kwargs):
        """Attempt to scale the different axis at the same time.
        
        Note:
            This is not really implemented at the moment as it's not giving
            the desired results.
        """
        pg.ViewBox.scaleBy(self.p1.vb, *args, **kwargs)
        self.p2.scaleBy(center=(0,0), y=args[0][0])
        self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
        
        
    def updateViews(self):
        """Setup slots to listen for changes in data on graph.
        """
        self.p2.setGeometry(self.p1.vb.sceneBoundingRect())
        self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)

    
    def _updateGraph(self, log_store, title):
        """Updates the graph with the details a LogSummaryInfo.
        
        Creates flow-in, flow-out, ddv, and mass balance graphs to plot.
        Flow PlotItem's go on the left y-axis and ddv and mb go on the right
        y-axis. They share the same x-axis (time).
        """
        # Clear the current plot items
        self.p1.clear()
        self.p2.clear()
        if not log_store.time_steps:
            return
        self.p1.setTitle(title)
        time = log_store.time_steps
        
        # Add flow in and flow out to the left y axis
        self.p1.plot(time, log_store.flow_in,
                    name='Flow_In', 
                    pen=({'color': 'b', 'width': 1}))

        self.p1.addItem(pg.PlotDataItem(time, log_store.flow_out,
                    name='Flow_Out', 
                    pen=({'color': 'r', 'width': 1})))

        # Add mass balance and ddv to second y axis
        self.p2.addItem(pg.PlotDataItem(time, log_store.ddv,
                    name='ddv', 
                    pen=({'color': 'k', 'width': 1})))
        
        self.p2.addItem(pg.PlotDataItem(time, log_store.mb,
                    name='MB', 
                    pen=({'color': 'g', 'width': 1})))
            
        if min(log_store.ddv) < min(log_store.mb):
            self.mMin = min(log_store.ddv) - 1
        else:
            self.mMin = min(log_store.mb) - 1
        if max(log_store.ddv) < max(log_store.mb):
            self.mMax = max(log_store.mb) + 1
        else:
            self.mMax = max(log_store.ddv) + 1
            
        self.myAutoRange()
        
    
    def getSettingsAttrs(self):
        """Setup the ToolSettings attributes for this widget.
        
        Overrides superclass method.
        
        Return:
            dict - member varibles and initial state for ToolSettings.
        """
        attrs = {'tlf_path': '', 'log_summarys': [], 'show_runform': True}
        return attrs
    

    def saveSettings(self):
        self.settings['show_runform'] = self.showFmpRunCbox.isChecked()
        return self.settings
    
    
    def deactivate(self):
        """Overrides superclass method."""
        self._stopAutoUpdate()
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
        
        self.showFmpRunCbox.setChecked(settings['show_runform'])
        
        # Test first
        files = os.listdir(self.data_dir)
        cache_check = dict(zip(files, [False] * len(files)))
        for i in range(len(self.settings['log_summarys'])-1, -1, -1):
            if not os.path.exists(self.settings['log_summarys'][i].stored_datapath):
                del self.settings['log_summarys'][i]
                logger.warning('cache data for log summary unavailable - will not be loaded.')
            if self.settings['log_summarys'][i].row_values['GUID'] + '.dat' in cache_check.keys():
                cache_check[self.settings['log_summarys'][i].row_values['GUID'] + '.dat'] = True
        
        for key, val in cache_check.iteritems():
            if not val:
                try:
                    os.remove(os.path.join(self.data_dir, key))
                except IOError, err:
                    logger.warning('Unable to delete orphaned cache file: ' + key)
        
        
        # Then setup table
        for i, summary in enumerate(self.settings['log_summarys'], 0):
            self._updateTableVals(summary, i+1)
    
    

class LogSummaryStore(object):
    """Stores the log output values."""
    
    def __init__(self, guid):
        self.guid = guid
        self.time_steps = []
        self.mb = []
        self.ddv = []
        self.flow_in = []
        self.flow_out = []
        self.runform_path = None



class LogSummaryEntry(object):
    """Store the details pertaining to a log summary entry."""
    
    def __init__(self, guid, tlf_name, datapath, tlf_path, status='Unknown', 
                 completion=0, max_mb=0, max_ddv=0):
        
        self.row_values = {
            'GUID': guid,
            'NAME': tlf_name,
            'STATUS': status,
            'COMPLETION': completion,
            'MAX_MB': max_mb,
            'MAX_DDV': max_ddv
        }
        
        # Runform bitmap stuff
        self.runform_path = None
        
        # .tlf stuff
        self.tlf_path = tlf_path
        self.stored_datapath = os.path.join(datapath, self.row_values['GUID'] + '.dat')
        self.start_time = 0
        self.finish_time = 1
        self.cur_time = 0
        self.cur_row = -1
        
        self.finished = False
        self.interrupted = False
        self.error = False
        self.in_results = False
        self.last_recorded_time = -9999

        


