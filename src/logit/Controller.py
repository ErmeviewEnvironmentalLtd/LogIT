'''
###############################################################################
#    
# Name: LogIT (Logger for Isis and Tuflow) 
# Version: 0.2-Beta
# Author: Duncan Runnacles
# Copyright: (C) 2014 Duncan Runnacles
# email: duncan.runnacles@thomasmackay.co.uk
# License: GPL v2 - Available at: http://www.gnu.org/licenses/gpl-2.0.html
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#
# Module:  Controller.py 
# Date:  16/11/2014
# Author:  Duncan Runnacles
# Version: 1.1
# 
# Summary:
#    Controller functions for the GUI. Code that is not directly responsible 
#    for updating or retrieving from the GUI is included in this module in
#    order to separate it from the application library.
#
# UPDATES:
#    DR (03/12/15) - Moved lots of the MainGui code into functions in here
#                    during extensive refactoring in that class.
#
# TODO:
#    Some heavy refactoring needed in some funtions.
#
###############################################################################
'''
import os
import traceback
import itertools
import sqlite3
import cPickle

from PyQt4 import QtCore, QtGui

from tmac_tools_lib.utils.qtclasses import MyFileDialogs

# Local modules
import DatabaseFunctions
import LogBuilder
import Exporters

import logging
logger = logging.getLogger(__name__)


def updateLog(db_path, log_pages, check_new_entries=False):
    '''
    '''
    # Connect to the database and then update the log entries
    conn = False
    error_found = False
    error_details = {'Success': True}
    update_check = None
    try:
        conn = DatabaseFunctions.loadLogDatabase(db_path)
        log_pages, update_check = logEntryUpdates(conn, log_pages,
                                                  check_new_entries)
    except IOError:
        logger.error('Unable to access database')
        error_found = False
        error_details = {'Success': False, 
            'Status_bar': "Unable to update Database with model: %s" % db_path,
            'Error': 'Database Error', 
            'Message': "Unable to update Database with model: %s" % db_path}
        #error_found = True
    except:
        logger.error('Error updating database -  See log for details')
        error_found = False
        error_details = {'Success': False, 
            'Status_bar': "Unable to update Database with model: %s" % db_path,
            'Error': 'Database Error', 
            'Message': "Unable to update Database with model: %s" % db_path}
        #error_found = True
    finally:
        if not conn == False:
            conn.close()
        return error_details, log_pages, update_check
    
class AddedRows(object):
    
    def __init__(self):
        '''
        '''
        self.tables = {}
    
    def _createHolder(self, key):
        '''
        '''
        if not key in self.tables:
            self.tables[key] = []
            
    def addRows(self, key, new_rows):
        '''
        '''
        self._createHolder(key)
        if self._checkIsList(new_rows):
            self.tables[key] = self.tables[key] + new_rows
        else:
            self.tables[key].append(new_rows)        
    
    def _checkIsList(self, row_item):
        '''
        '''
        if isinstance(row_item, list):
            return True
        else:
            return False
        
    def deleteEntries(self, conn):
        '''
        '''
        for name, table in self.tables.iteritems():
            for id in table:
                DatabaseFunctions.deleteRowFromTable(conn, name, id)
        

class AllLogs(object):
    
    SINGLE_FILE = ['RUN', 'DAT']
    
    def __init__(self, log_pages):
        '''
        '''
        self.log_pages = {}        
        for key, page in log_pages.iteritems():
            if key in AllLogs.SINGLE_FILE:
                self.log_pages[key] = SubLog(key, page, False)
            else:
                self.log_pages[key] = SubLog(key, page, True)
    
    def getLogDictionary(self):
        '''
        '''
        out_log = {}
        for page in self.log_pages.values():
            # DEBUG - have to convert back from list at the moment
            if page.name == 'DAT':
                page.contents = page.contents[0]
            out_log[page.name] = page.contents
        
        return out_log
    
    def getUpdateCheck(self):
        '''
        '''
        out_check = {}
        for page in self.log_pages.values():
            # DEBUG - have to convert back from list at the moment
            #if page.name == 'DAT':
            #    page.update_check = page.update_check[0]
            out_check[page.name] = page.update_check
        
        return out_check
        

class SubLog(object):
    
    def __init__(self, name, sub_page, multi_file):
        '''
        '''
        self.name = name
        self.multi_file = multi_file
        self.has_contents = self._checkHasContents(sub_page)
        sub_page = self._checkIsList(sub_page)
        self.contents = sub_page
        self.update_check = sub_page
        self.subfile_name = None
        if multi_file: self.subfile_name = name + '_FILES'
    
    def _checkIsList(self, sub_page):
        '''
        '''
        if self.name == 'RUN':
            return sub_page
        if not isinstance(sub_page, list):
            sub_page = [sub_page]
        return sub_page
    
    def _checkHasContents(self, contents):
        '''
        '''
        if self.multi_file:
            if contents[0] == 'None' or contents[0] == False or contents[0] == None:
                return False
        else:
            if contents == 'None' or contents == False or contents == None:
                return False

        return True
    
    def bracketFiles(self, index, key, files=None):
        '''
        '''
        if not files == None: self.contents[index][key] = files
        self.contents[index][key] = "[" + ", ".join(self.contents[index][key]) + "]"
    
    def deleteItem(self, index):
        '''
        '''
        del self.contents[index]
    

def logEntryUpdates(conn, log_pages, check_new_entries=False):
    '''Update the database with the current status of the log_pages dictionary.
    TODO: Re-Write these comments.
    If there's an issue inserting any of the data into any of the tables it
    will attempt to roll back the changes to all of the tables to 'hopefully'
    avoid any corruption. This will be logged so the user is aware.
    
    @param conn: an open database connection.
    @param log_pages: dictionary containing the the data to enter into the 
           database under the database table names.
    @param check_new_entries=False: new entry status may be checked before 
           getting to this stage and we don't want to do it twice.
    @raise IOError: If there's any issue connecting to the database.
    @raise Exception: if anything else goes wrong. 
    
    TODO:
        This is getting a bit of a mess and needs a lot of refactoring. Some
        of which may involve changing the way that LogIT.py uses it.
    '''
    def reverse_enumerate(iterable):
        '''Enumerate over an iterable in reverse order while retaining proper indexes
        '''
        return itertools.izip(reversed(xrange(len(iterable))), reversed(iterable))
    
    
    added_rows = {}
    
    
    all_logs = AllLogs(log_pages)
    added_rows = AddedRows()
    
    # DEBUG
    check_new_entries = True
    
    try:
        
        #for u in update_check:
        for page in all_logs.log_pages.values():
            
            if not page.has_contents: 
                page.update_check = False
                continue
            
            #if page.multi_file:
            if not page.name == 'RUN':
                
                for i, values in reverse_enumerate(page.contents):
                      
                    # We need the maximum id so that we can increment by 1 and put it into
                    # the output table in the GUI.
                    max_id = DatabaseFunctions.getMaxIDFromTable(conn, page.name) + 1
     
                    if page.multi_file:
                        # The FILES entry is a dictionary that uses the file
                        # name as a key. We need to get the new files from the files
                        # entry to enter into the database.
                        # Files lists then get converted to a single string.
                        new_files, ids = insertIntoModelFileTable(conn, 
                                            page.subfile_name, 'FILES', 
                                                values[page.name], values['FILES']) 
    
                        added_rows.addRows(page.subfile_name, ids)
                          
                        if not new_files == False:
                            page.bracketFiles(i, 'NEW_FILES', new_files)
    
                        page.bracketFiles(i, 'FILES')
    
                        page.contents[i]['ID'] = max_id
                    try:
                        is_in_db = False
                        if check_new_entries:
                            is_in_db = DatabaseFunctions.findInDatabase(
                                    page.name, conn=conn, col_name=page.name, 
                                    db_entry=page.contents[i][page.name])[0]

                        if not is_in_db:
                            DatabaseFunctions.insertValuesIntoTable(conn, 
                                        page.name, page.contents[i])
                          
                            added_rows.addRows(page.name, max_id)
                            page.update_check = True

                        else:
                            page.deleteItem(i)
                            page.updateCheck[i] = False
                    except:
                        logger.debug(traceback.format_exc())
                        raise 
 
        # Always put an entry in the Run entry table
        page = all_logs.log_pages['RUN']
        max_id = DatabaseFunctions.getMaxIDFromTable(conn, page.name) + 1
        page.contents['ID'] = max_id
        try:
            DatabaseFunctions.insertValuesIntoTable(conn, page.name, 
                                                    page.contents)
             
            added_rows.addRows(page.name, max_id)
             
        except:
            logger.debug(traceback.format_exc())
            raise 
        
        log_pages = all_logs.getLogDictionary()
        update_check = all_logs.getUpdateCheck()
        return log_pages, update_check
    
    # This acts as a failsafe incase we hit an error after some of the entries
    # were already added to the database. It try's to roll back the entries by
    # deleting them. The exception is still raised to be dealt with by the GUI.
    # TODO:
    #    This could probably be managed better with more constructive use of the
    #    database calls and how the connection.rollback() in sqlite3 is implemented.
    except:
        logger.error('Problem updating database: attempting to roll back changes')
        logger.debug(traceback.format_exc())

        try:
            added_rows.deleteEntries(conn)
            logger.warning('Successfully rolled back database')
            #raise
        except:
            logger.error('Unable to roll back database: CHECK ENTRIES!')
            logger.debug(traceback.format_exc())
            raise 


def insertIntoModelFileTable(conn, table_name, col_name, model_file, files_list):
    '''Insert file references into the model file table if they are not
    already there.
    
    @param conn: the current database connection.
    @param table_name: the name of the column to insert the file name into.
    @param file_list: the list of files to check against the database.
    '''
    new_files = []
    added_count = 1
    ids = []
    for f in files_list:
        
        # Check if we have any matched to the file name.            
        results = DatabaseFunctions.findInDatabase(table_name, conn=conn, 
                    col_name=col_name, db_entry=f, return_rows=True, 
                            only_col_name=False)
        
        # If we didn't find any matches we can put the file into the
        # files database under col_name and add it to the list so that we
        # can put it in the new files col of the main table.
        if results[0] == False:
            row_data = {col_name: model_file, 'FILES': f}
            DatabaseFunctions.insertValuesIntoTable(conn, table_name, row_data)
            new_files.append(f)
            ids.append(added_count)
            added_count += 1
    
    if len(new_files) < 1:
        return False, False
    else:
        return new_files, ids
    
    
def createQtTableItem(name, is_editable=False):
    '''Create a QTableWidgetItem and return
    @param is_editable=False: Set editable flag.
    @return: QTableWidgetItem
    '''
    item = QtGui.QTableWidgetItem(str(name))
    
    if is_editable:
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
    else:
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        
    return item


def deleteDatabaseRow(db_path, table_name, id):
    '''Deletes the database row with the given id
    @param db_path: the path to the database on file.
    @param table_name: the name of the table.
    @param id: the unique id of the row to delete.
    @return: True if successful, false otherwise.
    '''
    conn = None
    try:
        # Delete the row from the database
        conn = DatabaseFunctions.loadLogDatabase(db_path)
        DatabaseFunctions.deleteRowFromTable(conn, table_name, id)
        
    except IOError:
        logger.error('Unable to access database - see log for details')
        return False
    except Exception:
        logger.error('Unable to access database - see log for details')
        return False
    finally:
        if not conn == None:
            conn.close()
    
    return True
    
    
def checkDatabaseVersion(db_path):
    '''
    '''
    conn = False
    if not db_path == '' and not db_path == False:

        try:
            title = 'Load Error'
            # Need to check that the database is aligned with the current version
            version_check = DatabaseFunctions.checkDatabaseVersion(db_path)
            if version_check == DatabaseFunctions.DATABASE_VERSION_LOW:
                logger.error('Database version is old - please update database')
                msg = ("Unable to load model log from file at: %s\nDatabase" 
                       " needs updating to latest version.\nUse Settings >"
                       " Tools > Update Database Schema. See Help for details." 
                       % (db_path))
                return title, msg
                
            elif version_check == DatabaseFunctions.DATABASE_VERSION_HIGH:
                logger.error('Database version in new - please update LogIT')
                msg = ("Unable to load model log from file at: %s" 
                    "\nDatabase was produced with newer version of LogIT.\n"
                    "Update to latest version of LogIT to use database."
                    % (db_path))
                return title, msg
            
            conn = DatabaseFunctions.loadLogDatabase(db_path)
            cur = conn.cursor()
            cur.execute("select * from RUN")
            return None, None
        except:
            msg = "Unable to load model log from file at: %s." % (db_path)
            logger.error('Unable to load model log from file at: \n' % (db_path))
            return title, message
        finally:
            conn.close()
    

def fetchTableValues(db_path, table_list):
    '''Fetches all rows from the given table name.
    @param db_path: path to a database on file.
    @param table_name: name of the table to fetch rows from.
    @return: tuple (boolean success flag, row count, row data) or an error
             with (False, error title, message)
    '''
    conn = False
    title = 'Load Error'
    entries = []
    try:
        conn = DatabaseFunctions.loadLogDatabase(db_path)
        conn.row_factory = sqlite3.Row
                
        for table in table_list:
            # If there's nothing in the table it will fail, but we don't care
            # so just pass the error.
            try:
                results = DatabaseFunctions.findInDatabase(table[0], 
                                    db_path=False, conn=conn, return_rows=True)
                 
                entries.append([table[0], table[1], results[0], results[1], results[2]])
            except:
                pass           
        
        return entries, True
        
#         results = DatabaseFunctions.findInDatabase(table_name, db_path=False, 
#                                                 conn=conn, return_rows=True)
#         return results[0], results[1], results[2]
    except:
        msg = "Unable to load model log from file at: %s." % (db_path)
        logger.error('Unable to load model log from file at: \n%s' % (db_path))
        return entries, False, title, msg
    finally:
        conn.close()
 

def loadEntrysWithStatus(db_path, log_pages, table_list):
    '''Loads the database and checks if the new entries exist.
    
    Builds a new list that stores the log_pages entry for each row as well as
    some info on the key to that table in the gui, whether the entry already
    exists or not adn the row count.
    Uses the findNewLogEntries function to fo the hard work.
    
    @param db_path: path to a database on file.
    @param log_pages: the log_pages dictionary with loaded model variables.
    @param table_list: a list of all of the keys for accessing thetables in the 
           'New log Entry' page of the GUI and the associated db tables.
    @return: list containing sub-lists of all of the rows to be displayed on
             the New log entry page tables.
    '''
     # We need to find if the TGC and TBC files have been registered with the
    # database before. If they have then we don't need to register them 
    # again.
    conn = False
    try:
        conn = DatabaseFunctions.loadLogDatabase(db_path)
        entries = []
        
        # Find log entries and populate tables for the model files
        for item in table_list:
            name = item[0]
            key = item[1]
            if name == 'RUN':
                continue
            
            if name == 'DAT':
                if log_pages['DAT']['DAT'] == 'None':   
                    log_pages['DAT'] = None
                else:
                    log_pages, new_entries = findNewLogEntries(
                                        conn, log_pages, 'DAT', key, False)
            else:
                log_pages, new_entries = findNewLogEntries(
                                            conn, log_pages, name, key)
            entries = entries + new_entries
        
        
            
        return entries
            
    except IOError:
        logger.error('IOError - Unable to access database')
    except Error:
        logger.error('SQLError - Could not query database')
    finally:
        if not conn == False:
            conn.close()


def findNewLogEntries(conn, log_pages, log_name, table_key=None, 
                                                    multiple_files=True):
    '''Checks entries against database to see if they're new of already exist.
    
    TODO:
        This is still a bit messy at the moment. Need to clean it up and make
        it a bit easier to read and less nested.
    '''
    logger.debug('Find Entry: log_name=%s, table_key=%s' % (log_name, table_key))
        
    data_to_display = []
    
    # Most files are multiple but the DAT file entry isn't so has to be 
    # dealt with seperately as it doesn't need looping through
    if multiple_files:
        if not log_pages[log_name] == None:
            mod_length = len(log_pages[log_name])
            
            # We have to loop backwards here because we might delete entries
            for i in range(mod_length-1, -1, -1):
                
                if log_pages[log_name][i][log_name] == 'None':
                    log_pages[log_name][i] = None
                else:
                
                    is_new_entry = DatabaseFunctions.findNewEntries(
                                        conn, log_name, log_pages[log_name][i])
    
                    # If we're adding them to the editable tables we do it
                    # Otherwise just get rid of those we don't want
                    if not table_key == None:
                        
                        # If it'a already in the database then we remove it from the log
                        # dictionary to avoid entering it again.
                        if not is_new_entry:
                            data_to_display = [[log_pages[log_name][i], table_key, i, False]]
                            del log_pages[log_name][i]
                        else:
                            data_to_display = [[log_pages[log_name][i], table_key, i, True]]
                    else:
                        if not is_new_entry:
                            del log_pages[log_name][i]
    else:
        if not table_key == None:
            if not DatabaseFunctions.findNewEntries(conn, log_name, log_pages[log_name]):
                data_to_display = [[log_pages[log_name], table_key, 0, False]]
                log_pages[log_name] = None
            else:
                data_to_display = [[log_pages[log_name], table_key, 0, True]]
        else:
            log_pages[log_name] = None
    
    return log_pages, data_to_display


def fetchAndCheckModel(db_path, open_path, log_type, launch_error=True):
    '''Loads a model and makes a few conditional checks on it.
    Loads model from the given .tcf/.ief file and checks that the .ief, 
    .tcf and ISIS results don't already exist in the DB and then returns
    a success or fail status.
    
    @param db_path: path to the database on file.
    @param open_path: the .ief or .tcf file path.
    @param log_type: the model type to load (tuflow or ISIS only).
    @param lauch_error=True: whether to launch message boxes if an error is
           found or not. We don't want to if we're loading multiple files.
    @return: tuple containing log_pages (which could be the loaded log
             pages or False if the load failed and a dictionary containing
             the load status and messages for status bars and errors.
    '''
    
    error_details = {'Success': True}
    # Load the model at the chosen path.
    log_pages = LogBuilder.loadModel(open_path, log_type)
    if log_pages == False:
        error_details = {'Success': False, 
                    'Status_bar': "Unable to load model at: %s" % open_path,
                     'Error': 'LoadError', 
                    'Message': 'Selected file could not be loaded - file: %s.' % open_path}
        return error_details, log_pages
    else:
        # Make sure that this ief or tcf do not already exist in the
        # database. You need new ones for each run so this isn't
        # allowed.
        main_ief = log_pages['RUN']['IEF']
        main_tcf = log_pages['RUN']['TCF']
        tcf_results = log_pages['RUN']['RESULTS_LOCATION_2D']
        indb = (False,)
        found_path = ''
        
        try:
            # If we have an ief get the ief name to see if we already
            # recorded a run using that model
            if not main_ief == 'None':
                indb = DatabaseFunctions.findInDatabase(
                         'RUN', db_path=db_path, 
                         db_entry=main_ief, col_name='IEF', 
                         only_col_name=True)
                
                # Then check if we've already used the results locations
                # location for a previous run and return error if it has.
                if indb[0]:
                    exists = DatabaseFunctions.findInDatabase(
                             'RUN', db_path=db_path, 
                             db_entry=tcf_results, col_name='RESULTS_LOCATION_1D', 
                             only_col_name=True)
                    
                    if exists[0]:
                        error_details = {'Success': False, 
                        'Status_bar': "ISIS/FMP results file already exists in %s" % (main_ief),
                         'Error': 'Results Location Exists', 
                        'Message': 'ISIS/FMP results file already exists in %s' % (main_ief)}
                        return error_details, log_pages
    #                     button = QtGui.QMessageBox.question(self, 
    #                             "ISIS/FMP Results Folder Already Exists",
    #                             "Results folder location found in previous " +
    #                             "entry\nDo you want to Continue?",
    #                             QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
    #                     
    #                     if button == QtGui.QMessageBox.No:
    #                         return
                    
                found_path = main_ief
            
            # Do the whole lot again for the tuflow run
            if not main_tcf == 'None':
                if not indb[0]:
                    indb = DatabaseFunctions.findInDatabase(
                             'RUN', db_path=db_path, 
                             db_entry=main_tcf, col_name='TCF', 
                             only_col_name=True)
                    found_path = main_tcf
            
            if indb[0]:
                error_details =  {'Success': False, 
                    'Status_bar': "Unable to load model at: %s" % open_path,
                     'Error': 'LoadError', 
                    'Message': 'Selected file already exists in database - file: %s.' % found_path}
                return error_details, log_pages
            else:
                error_details = {'Success': True, 
                    'Status_bar': "Loaded model at: %s" % open_path,
                     'Error': None, 
                    'Message': None}
                return error_details, log_pages
                    
        except IOError:
            error_details = {'Success': False, 
                    'Status_bar': "Unable to update Database with model: %s" % open_path,
                     'Error': 'IO Error', 
                    'Message': "Unable to load model from file at: %s" % open_path}
            return error_details, log_pages
        except:
            error_details = {'Success': False, 
                'Status_bar': "Unable to update Database with model: %s" % open_path,
                'Error': 'IO Error', 
                'Message': "Unable to load model from file at: %s" % open_path}
            return error_details, log_pages
        

def updateDatabaseVersion(db_path):
    '''Try to update database to latest version.
    @param db_path: path to the database to update.
    @return: None if user cancels or error_details otherwise. These can be:
             error_details['Success'] = True if all good or False otherwise.
             If False then other dict items contain details.
    '''
    error_details = {'Success': True}
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
    
    try:
        DatabaseFunctions.updateDatabaseVersion(open_path)
        return error_details
    except:
        logger.error('Failed to update database scheme: See log for details')
        error_details = {'Success': False, 
                'Status_bar': "Database Update Failed",
                'Error': 'Database Error', 
                'Message': "Failed to update database scheme: See log for details"}
        return error_details
                        
        
def loadSetup(cur_settings_path, cur_log_path):
    '''Load LogIT setup from file.
    '''
    d = MyFileDialogs()
    open_path = d.openFileDialog(path=os.path.split(cur_log_path)[0], 
                        file_types='Log Settings (*.logset)')
    
    if open_path == False:
        return False, None, None
    try:
        # Load the settings dictionary
        open_path = str(open_path)
        cur_settings = cPickle.load(open(open_path, "rb"))
        cur_settings.cur_settings_path = cur_settings_path
        return cur_settings, None, None
    except:
        msg = "Unable to load user settings from: %s" % (open_path)
        logging.info(msg)
        logger.error('Could not load settings file')
        title = "Load Failed"
        return False, title, msg
    
    
def exportToExcel(cur_log_path, export_tables):
    '''Export database to Excel (.xls) format at user chosen location.
    @param cur_log_path: the current log database file path.
    @param export_tables: list with order to create worksheet.
    @return dictionary containing error_details (or success details if
            error_details['Success'] is True.
    @note: launches file dialog.
    '''
    error_details = {'Success': True}
    d = MyFileDialogs()
    save_path = d.saveFileDialog(path=os.path.split(cur_log_path)[0], 
                                 file_types='Excel File (*.xls)')
    save_path = str(save_path)
    
    if not save_path == False:
        try:
            Exporters.exportToExcel(cur_log_path, export_tables, save_path)
        except:
            logger.error('Could not export log to Excel')
            error_details = {'Success': False, 
                'Status_bar': "Export to Excel Failed",
                'Error': "Export Failed", 
                'Message': "Unable to export database to Excel - Is the file open?"}
            return error_details
       
        logger.info('Database exported to Excel at:\n%s' % (save_path))
        error_details = {'Success': True, 
                'Status_bar': "Database exported to Excel at: %s." % save_path,
                'Error': "Export Failed", 
                'Message': "Database exported to Excel at: %s." % save_path}
        return error_details


def getModelFileLocation(multi_paths, last_model_directory,
                                        cur_log_path, cur_settings_path):
    '''Launch dialog for user to choose model to load.
    @param param: 
    '''
    # Create a file dialog with an initial path based on the availability
    # of path variables.
    d = MyFileDialogs()
    if not last_model_directory == '' and \
                    not last_model_directory == False:
        chosen_path = last_model_directory
    elif not cur_log_path == ''  and not self.settings.cur_log_path == False:
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
    
    
    