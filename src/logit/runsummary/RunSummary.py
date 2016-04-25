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


 Module:          ModelExtractor.py 
 Date:            04/03/2016
 Author:          Duncan Runnacles
 Since-Version:   0.4
 
 Summary:
    Copies the model at the path location stored in the log to a new directory.

 UPDATES:
    

 TODO:
    

###############################################################################
"""

import logging
logger = logging.getLogger(__name__)

import os
import uuid
import datetime
import cPickle
import math
from PyQt4 import QtCore, QtGui
import pyqtgraph as pg

from ship.utils.filetools import MyFileDialogs
    
import RunSummary_Widget as summarywidget
logger.debug('RunSummary_Widget import complete')
from app_metrics import utils as applog
import globalsettings as gs


class RunSummary_UI(QtGui.QWidget, summarywidget.Ui_RunSummaryWidget):
    

    def __init__(self, cwd, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QWidget.__init__(self, parent, f)
        
        self.tool_name = 'Run Summary'
        self.settings = ToolSettings()
        self.settings.cur_location = cwd
        if not os.path.exists(os.path.join(cwd, 'data')):
            os.mkdir(os.path.join(cwd, 'data'))
        self.data_dir = os.path.join(cwd, 'data', 'runsummary')
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        
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
        
        self.mMin = -10
        self.mMax = 10
    
    
    def _setupPlot(self):
        """Setups up the main layou and viewboxes for the graph.
        
        Creates three ViewBox's for the cross section, conveyance and mannings.
        All other data series are added to one of these.
        """
        self.p1 = self.simGraphGraphics.plotItem
        self.p1.setLabels(left=('Flow In & Flow Out'), bottom=('Time', 'h'), right='MB & DDV')
        self.p1.vb.menu.triggered.connect(self.myAutoRange)
        self.p1.autoBtn.clicked.connect(self.myAutoRange)
#         self.p1.scene().sigMouseClicked.connect(self._mouseClicked)
        
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
        menu = QtGui.QMenu()
        updateEntryAction = menu.addAction("Update Entry")
        deleteEntryAction = menu.addAction("Remove Entry")
        reloadRunAction = menu.addAction("Reload Run")

        # Find who called us and get the object that the name refers to.
        sender = self.sender()
        sender = str(sender.objectName())
        
        # Get the action and find the associated entry by guid code
        action = menu.exec_(self.runStatusTable.viewport().mapToGlobal(pos))
        row = self.runStatusTable.currentRow()
        guid = str(self.runStatusTable.item(row, 0).text())
        logger.debug('Selected GUID = ' + guid)
        entry = None
        for log in self.settings.log_summarys:
            if log.row_values['GUID'] == guid:
                entry = log
                break
        if entry is None: return
                
        if action == deleteEntryAction:
            self.runStatusTable.removeRow(row) 
            entry_i = -1
            for i, log in enumerate(self.settings.log_summarys):
                if log.row_values['GUID'] == entry.row_values['GUID']: 
                    entry_i = i
                    break
            if not entry_i == -1: del self.settings.log_summarys[entry_i]
            try:
                os.remove(entry.stored_datapath)
            except IOError:
                logger.warning('Unable to find cache file - may not exist or might need deleting manually')
            entry = None
            self.p1.clear()
            self.p2.clear()
        
        if action == reloadRunAction:
            log_store = self._loadLogStoreFromCache(entry.row_values['GUID'])
            details = []
            for i, log in enumerate(self.settings.log_summarys):
                if log.row_values['GUID'] == entry.row_values['GUID']: 
                    details = [log.row_values['GUID'], log.row_values['NAME'],
                              log.tlf_path, i]
                    break

            if details:
                entry = LogSummaryEntry(details[0], details[1], self.data_dir, details[2])
                entry, log_store = self._loadLogContents(entry, details[2])
                self._saveLogStoreToCache(log_store, entry.stored_datapath)
                self._updateTableVals(entry, details[3])
                self._updateGraph(log_store)
                self.settings.log_summarys[details[3]] = entry
                
        if action == updateEntryAction:
            log_store = self._loadLogStoreFromCache(entry.row_values['GUID'])
            if not entry.row_values['STATUS'] == 'Complete' and not entry.row_values['STATUS'] == 'Failed':
                entry, log_store = self._loadLogContents(entry, entry.tlf_path, log_store)
                self._saveLogStoreToCache(log_store, entry.stored_datapath)
            entry_i = -1
            for i, log in enumerate(self.settings.log_summarys):
                if log.row_values['GUID'] == entry.row_values['GUID']: 
                    entry_i = i
                    break
            if not entry_i == -1: self.settings.log_summarys[entry_i] = entry
                
            self._updateTableVals(entry, row)
            self._updateGraph(log_store)
        
  
    def _updateAllStatus(self):
        """
        """
        logger.debug("Updating all status'")
        log_store = None
        for i, log in enumerate(self.settings.log_summarys):
            log_store = self._loadLogStoreFromCache(log.row_values['GUID'])
            if log.row_values['STATUS'] == 'Complete' or log.row_values['STATUS'] == 'Failed':
                entry = log
            else:
                entry, log_store = self._loadLogContents(log, log.tlf_path, log_store)
                self._saveLogStoreToCache(log_store, entry.stored_datapath)
            self._updateTableVals(entry, i)
            self.settings.log_summarys[i] = entry
            
        if not log_store is None: self._updateGraph(log_store)
        
    
    
    def _saveLogStoreToCache(self, log_store, path):
        """
        """
        try:
            with open(path, "wb") as p:
                cPickle.dump(log_store, p)
        except IOError:
            logger.error('Unable to cache log_store with guid - ' + log_store.guid)
            raise
    
    
    def _loadLogStoreFromCache(self, guid):
        """
        """
        try:
            # Load the settings dictionary
            open_path = os.path.join(self.data_dir, guid + '.dat')
            log_store = cPickle.load(open(open_path, "rb"))
            return log_store
        except IOError:
            logger.error('Unable to load log_store from cache with guid - ' + guid)
            raise
    
    
    def _activateRow(self, row, col):
        """
        """
        self.runStatusTable.selectRow(row)
        guid = str(self.runStatusTable.item(row, 0).text())
        log_store = self._loadLogStoreFromCache(guid)
        self._updateGraph(log_store)
    

    def _loadIntoTable(self, tlf_path):
        """
        """
        logger.debug('Load into table clicked')
        if not os.path.exists(tlf_path):
            self.launchQMsgBox('Nonexistant tlf', 'TLF file does not exist at:\n' + tlf_path)
            return
        for log in self.settings.log_summarys:
            if log.tlf_path == tlf_path:
                self.launchQMsgBox('Load Error', ('This log file has already ' +
                                                 'been loaded into the table\n' +
                                                 'Either update the row or ' +
                                                 'remove and re-add it.'))
                return
        
        run_name = os.path.splitext(os.path.split(tlf_path)[1])[0]
        guid = str(uuid.uuid4())
        entry = LogSummaryEntry(guid, run_name, self.data_dir, tlf_path)
        
        entry, log_store = self._loadLogContents(entry, tlf_path)
        self._saveLogStoreToCache(log_store, entry.stored_datapath)
        self.settings.log_summarys.append(entry)
        self._updateTableVals(entry)
        self._updateGraph(log_store)
        
    
    def _updateTableVals(self, summary_obj, row_no=-1):
        """
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
                if finish_time == 0 and summary_obj.start_time == 0:
                    finish_time = 1
                prog.setMaximum(int(finish_time))
                prog.setMinimum(int(summary_obj.start_time))
                prog.setValue(int(val))
                self.runStatusTable.setCellWidget(row_no, col, prog)
            else:
                item = QtGui.QTableWidgetItem(str(val))
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled) 
                if status == 'Failed':
                    item.setBackgroundColor(QtGui.QColor(255, 204, 204)) # Light Red
                    item.setFont(QtGui.QFont('Arial', 9, QtGui.QFont.Bold))
                elif status == 'Complete':
                    item.setBackgroundColor(QtGui.QColor(204, 255, 153)) # Light green
                    
                self.runStatusTable.setItem(row_no, col, item)
        self.runStatusTable.selectRow(row_no)
          
    
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

    
    def _updateGraph(self, log_store):
        """
        """
        # Clear the current plot items
        self.p1.clear()
        self.p2.clear()
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
                    pen=({'color': 'k', 'width': 1})))#, 
        
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
        time = None
        if date_str[1] == ':': date_str = '0' + date_str
        try:
            time = datetime.datetime.strptime(date_str, "%H:%M:%S")
        except ValueError:
            #logger.error('date_str is not in the correct format (HH:MM:SS: ' + date_str)
            raise
        hours_in_mins = float(time.hour) * 60
        hours = (hours_in_mins + float(time.minute)) / 60
        return hours, time
        
        
    def _loadLogContents(self, entry, tlf_path, log_store=None):
        """
        """
        if not log_store is None:
            in_results = True
            own_log = True
        else:
            log_store = LogSummaryStore(entry.row_values['GUID'])
            in_results = False
            own_log = False
        finished = False
        interrupted = False
        error = False
        start_time = -1
        end_time = -1
        cur_row = -1
        try:
            with open(tlf_path, 'rb') as f:
                for line in f:
                    if not log_store is None and cur_row < entry.cur_row:
                        cur_row += 1
                        continue
                    cur_row += 1
                    
                    # Find the start and finish times first
                    if not in_results:
                        if line.startswith('Start Time (h):'):
                            start_time = float(line[22:34].strip())
                        if line.startswith('Finish Time (h):'):
                            end_time = float(line[22:34].strip())

                        elif '.. Running' in line:
                            in_results = True
                
                    # Then load the simulation data
                    else:
                        if 'Writing Output' in line: continue
                        if line.strip() == '': continue
                        if 'Run Finished' in line:
                            finished = True
                            break
                        if 'Run Interrupted' in line:
                            interrupted = True
                            break
                        if 'ERROR' in line:
                            error = True
                            break
                        
                        try:
                            time = line[8:16].strip()
                            hours, t = self.getHoursFromDateStr(time)
                        except (ValueError, IndexError):
                            continue
                        mb = line[61:67].strip('%')
                        if '***' in mb:
                            mb = 99
                        else:
                            mb = float(mb) 
                        Qin = float(line[83:89])
                        Qout = float(line[93:99])
                        ddv = float(line[103:109])
                        
                        if math.fabs(mb) > math.fabs(entry.row_values['MAX_MB']):
                            entry.row_values['MAX_MB'] = mb
                        if math.fabs(ddv) > math.fabs(entry.row_values['MAX_DDV']):
                            entry.row_values['MAX_DDV'] = ddv
                        
                        s = t.second
                        log_store.time_steps.append(hours)
                        log_store.mb.append(mb)
                        log_store.flow_in.append(Qin)
                        log_store.flow_out.append(Qout)
                        log_store.ddv.append(ddv)
                
        except IOError:
            logger.error('Unable to open log file at:\n' + tlf_path)
            entry.row_values['STATUS'] = 'Unfindable'
        
        if finished:
            entry.row_values['COMPLETION'] = end_time
            entry.row_values['STATUS'] = 'Complete'
        elif interrupted or error:
            entry.row_values['COMPLETION'] = log_store.time_steps[-1]
            entry.row_values['STATUS'] = 'Failed'
        else:
            entry.row_values['COMPLETION'] = log_store.time_steps[-1]
            entry.row_values['STATUS'] = 'In Progress'
        
        if own_log:
            entry.start_time = log_store.start_time
            entry.finish_time = log_store.finish_time
        else:
            log_store.start_time = entry.start_time = start_time
            log_store.finish_time = entry.finish_time = end_time
            
        entry.cur_row = cur_row

        return entry, log_store
            
        
    def _loadLogFile(self):
        """
        """
        path = self.settings.cur_location
        if not self.settings.cur_modellog_path== '':
            path = self.settings.cur_modellog_path
        d = MyFileDialogs()
        open_path = d.openFileDialog(path, file_types='Tuflow log file (*.tlf)')
        if open_path == 'False' or open_path == False:
            return
        self.settings.cur_modellog_path = open_path
        self._loadIntoTable(open_path)
        
    
    def loadSettings(self, settings):
        """Load any pre-saved settings provided."""
        
        # Check that this version of the settings has all the necessary
        # attributes, and if not add the missing ones
        temp_set = ToolSettings()
        settings_attrs = [s for s in dir(temp_set) if not s.startswith('__')]
        for s in settings_attrs:
            if not hasattr(settings, s):
                setattr(settings, s, getattr(temp_set, s))
        
        self.settings = settings
        # Test first
        for i in range(len(self.settings.log_summarys)-1, -1, -1):
            if not os.path.exists(self.settings.log_summarys[i].stored_datapath):
                del self.settings.log_summarys[i]
                logger.warning('cache data for log summary unavailable - will not be loaded.')
        
        i = 0
        # Then setup table
        for i, summary in enumerate(self.settings.log_summarys, 0):
            self._updateTableVals(summary, i+1)
    
    
    def saveSettings(self):
        """Return state of settings back to caller."""
        
        return self.settings
    

    def launchQMsgBox(self, title, message, type='warning'):
        """Launch a QMessageBox
        """
        if type == 'warning':
            QtGui.QMessageBox.warning(self, title, message)
        
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
            return answer



class LogSummaryStore(object):
    """"""
    
    def __init__(self, guid):
        self.guid = guid
        self.time_steps = []
        self.mb = []
        self.ddv = []
        self.flow_in = []
        self.flow_out = []
        start_time = 0
        finish_time = 0



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
        self.tlf_path = tlf_path
        self.stored_datapath = os.path.join(datapath, self.row_values['GUID'] + '.dat')
        self.start_time = 0
        self.finish_time = 0
        self.cur_time = 0
        self.cur_row = -1



class ToolSettings(object):
    """Store the settings used by this class."""
    
    def __init__(self):
        
        self.tool_name = 'Run Summary'
        self.cur_location = ''
        self.cur_display_path = ''
        self.cur_modellog_path = ''
        self.log_summarys = []
        


