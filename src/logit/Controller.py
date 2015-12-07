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
import LogClasses

import logging
logger = logging.getLogger(__name__)


def reverse_enumerate(iterable):
    '''Enumerate over an iterable in reverse order while retaining proper indexes
    '''
    return itertools.izip(reversed(xrange(len(iterable))), reversed(iterable))

    
class AddedRows(object):
    '''Keeps track of any new rows added to the database.
    
    It stores the primary key ID of any rows that are added. This can be used
    for many things I suppose, but at the moment it is used to deal with a
    problem in data entry. If an issue is found and some entries have already
    been made to the database it will re-wind all of the entries stored by
    deleting them from the database.
    '''
    
    def __init__(self):
        self.tables = {}
    
    def _createHolder(self, key):
        '''Creates a new key in the dict if it doesn't exist.
        '''
        if not key in self.tables:
            self.tables[key] = []
            
    def addRows(self, key, new_rows):
        '''Adds a new row to the list under key
        '''
        self._createHolder(key)
        if self._checkIsList(new_rows):
            self.tables[key] = self.tables[key] + new_rows
        else:
            self.tables[key] = self.tables[key] + [new_rows]     
    
    def _checkIsList(self, row_item):
        '''Returns True if a list or False if not.
        Essentially this is testing whether a single value or a list of values
        is being passed.
        '''
        if isinstance(row_item, list):
            return True
        else:
            return False
        
    def deleteEntries(self, conn):
        '''Deletes all of the entries in this object from the database.
        @note: This may raise an error that should be dealt with by the 
               calling code.
        '''
        for name, table in self.tables.iteritems():
            for id in table: #reverse_enumerate(table):
                DatabaseFunctions.deleteRowFromTable(conn, name, id)
        

# class AllLogs(object):
#     '''Container class for all of the SubLog objects.
#     '''
#     
#     SINGLE_FILE = ['RUN', 'DAT']
#     
#     def __init__(self, log_pages):
#         '''Create new SubLog and set multi_file.
#         '''
#         self.log_pages = {}        
#         for key, page in log_pages.iteritems():
#             if key in AllLogs.SINGLE_FILE:
#                 self.log_pages[key] = SubLog(key, page, False)
#             else:
#                 self.log_pages[key] = SubLog(key, page, True)
#     
#     def getLogDictionary(self):
#         '''Return all logs in class as a dictionary.
#         '''
#         out_log = {}
#         for page in self.log_pages.values():
#             # DEBUG - have to convert back from list at the moment
#             if page.name in AllLogs.SINGLE_FILE:
#                 if not len(page.contents) < 1:
#                     page.contents = page.contents[0]
#             out_log[page.name] = page.contents
#         
#         return out_log
#     
#     def getUpdateCheck(self):
#         '''Return dictionary containing update status.
#         Update status is a boolean flag indicating whether a log page should
#         be updated or not.
#         '''
#         out_check = {}
#         for page in self.log_pages.values():
#             out_check[page.name] = page.update_check
#         
#         return out_check
#         
# 
# class SubLog(object):
#     '''Log page objects.
#     E.g. RUN, TGC, etc.
#     '''
#     
#     def __init__(self, name, sub_page, multi_file):
#         '''Set vars and make sure everything is in the format needed.
#         '''
#         self.name = name
#         self.multi_file = multi_file
#         self.has_contents = self._checkHasContents(sub_page)
#         sub_page = self._checkIsList(sub_page)
#         self.contents = sub_page
#         self.update_check = False
#         #self.update_check = self._createUpdateCheck(sub_page)
#         self.subfile_name = None
#         if multi_file: self.subfile_name = name + '_FILES'
#     
#     
# #     def _createUpdateCheck(self, sub_page):
# #         '''
# #         '''
# #         return [False] * len(sub_page)
#     
#     def _checkIsList(self, sub_page):
#         '''Checks if given page is in a list and puts it in one if not.
#         
#         Some pages like RUN and DAT can only have one entry, while the others
#         may have many. Originally the others were put in a list and RUN & DAT
#         weren't. This is a design fault and this method can be removed once 
#         it is dealt with throughout the codebase.
#         '''
#         if not isinstance(sub_page, list):
#             sub_page = [sub_page]
#         return sub_page
#     
#     def _checkHasContents(self, contents):
#         '''Checks the status of the page contents.
#         
#         If the contents are set to a default value this will return False.
#         This should also be possible to clean up by ensuring only a single
#         default value is used throughout the codebase.
#         '''
#         if not self.name == 'RUN':
#             if self.multi_file:
#                 if contents[0] == 'None' or contents[0] == False or contents[0] == None:
#                     return False
#                 elif contents[0][self.name] == 'None':
#                     return False
#             else:
#                 if contents == 'None' or contents == False or contents == None:
#                     return False
#                 elif contents[self.name] == 'None':
#                     return False
# 
#         return True
#     
#     def bracketFiles(self, index, key, files=None):
#         '''Encloses all of the files, under a certain key, in brackets.
#         If not files==None a new key will be created and those files will be
#         enclosed in brackets.
#         '''
#         if not files == None: self.contents[index][key] = files
#         self.contents[index][key] = "[" + ", ".join(self.contents[index][key]) + "]"
#     
#     def deleteItem(self, index):
#         '''Deletes an item (i.e. a row) from the contents.
#         '''
#         del self.contents[index]


def updateLog(db_path, log_pages, errors, check_new_entries=False):
    '''Updates the log database with the current value of log_pages.
    
    This is just an entry function that connects to the database and and then
    call logEntryUpdates to do all of the hard work. It deals with handling
    any errors that might pop up and notifying the caller.
    @param dp_path: the path to the log database on file.
    @param log_pages: log pages dictionary.
    @param check_new_entries=False: Flag identifying whether the values in the
           log_pages entries should be checked against the database before they
           are entered. i.e. make sure they don't alreay exist first. This is
           needed because the check may have already been carries out before
           and it will cost unnecessary processing effort.
    '''
    # Connect to the database and then update the log entries
    conn = False
    update_check = None
    try:
        conn = DatabaseFunctions.loadLogDatabase(db_path)
        log_pages, update_check = logEntryUpdates(conn, log_pages,
                                                  check_new_entries)
    except IOError:
        logger.error('Unable to access database')
        errors.addError(errors.DB_ACCESS, msgbox_error=True, 
                                        msg_add=(':\n%s' % (db_path)))

    except:
        logger.error('Error updating database -  See log for details')
        errors.addError(errors.DB_UPDATE, msgbox_error=True, 
                                        msg_add=':\n%s' % (db_path))

    finally:
        if not conn == False:
            conn.close()
        return errors, log_pages, update_check
 

def logEntryUpdates(conn, log_pages, check_new_entries=False):
    '''Update the database with the current status of the log_pages dictionary.
    
    This creates a callback function and hands it to loopLogPages method,
    which loops through the log pages applying the call back each time.
    
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
    
    '''
    
    added_rows = None    
    
    def insertSubFiles(conn, index, values, page, max_id):
        '''Insert files referenced by one of the log pages into its table.
        
        Looks to see if any of the files it contains aren't already entered. 
        If they aren't it adds them to the files table (e.g. TGC_FILES).
        Then converts to a bracket wrapped string for adding to main log table
        (e.g. TGC).
        '''
        new_files, ids = insertIntoModelFileTable(conn, 
                            page.subfile_name, 'FILES', 
                                values[page.name], values['FILES']) 
    
        #added_rows.addRows(page.subfile_name, ids)
          
        if not new_files == False:
            added_rows.addRows(page.subfile_name, ids)
            page.bracketFiles(index, 'NEW_FILES', new_files)
    
        page.bracketFiles(index, 'FILES')
        page.contents[index]['ID'] = max_id
        
        return page
     
    def insertMainFile(conn, index, page, max_id, check_entry):
        '''Adds the log page data in 'page' to the log page table.
        
        Will check if entry exists first if check_entry==True.
        '''
        try:
            is_in_db = False
            if check_entry:
                is_in_db = DatabaseFunctions.findInDatabase(
                        page.name, conn=conn, col_name=page.name, 
                        db_entry=page.contents[index][page.name])[0]

            if not is_in_db:
                DatabaseFunctions.insertValuesIntoTable(conn, 
                            page.name, page.contents[index])
              
                added_rows.addRows(page.name, max_id)
                page.contents[index]['ID'] = max_id
                page.update_check = True

            else:
                page.deleteItem(index)
                #page.update_check[index] = False
        except:
            logger.debug(traceback.format_exc())
            raise 
        
        return page
    
    def callbackFunc(conn, i, values, page, callback_args):
        '''Insert entries into database and update page values.
        This function is a callback used by the looping function.
        '''
        check_new_entries = callback_args['check_new_entries']
        
        # We need the maximum id so that we can increment by 1 and put it into
        # the output table in the GUI.
        max_id = DatabaseFunctions.getMaxIDFromTable(conn, page.name) + 1
        
        if page.multi_file:
            page = insertSubFiles(conn, i, values, page, max_id)
            
        if page.name == 'RUN':
            page = insertMainFile(conn, 0, page, max_id, False)
        else:
            page = insertMainFile(conn, i, page, max_id, check_new_entries)
        
        return page, callback_args
            
    # Class to hold all the log page objects
    all_logs = AllLogs(log_pages)  

    # Collects all files added to database for resetting
    added_rows = AddedRows()
    check_new_entries = True
    try:
        # Send function as a callback to the log page looping function.
        all_logs, callback_args = loopLogPages(conn, all_logs, callbackFunc, 
                                    {'check_new_entries': check_new_entries})
        
        
        # Get the data from the classes in dictionary format
        log_pages = all_logs.getLogDictionary()
        update_check = all_logs.getUpdateCheck()
        return log_pages, update_check
    
    # This acts as a failsafe incase we hit an error after some of the entries
    # were already added to the database. It tries to roll back the entries by
    # deleting them. The exception is still raised to be dealt with by the GUI.
    except:
        logger.error('Problem updating database: attempting to roll back changes')
        logger.debug(traceback.format_exc())

        try:
            added_rows.deleteEntries(conn)
            logger.warning('Successfully rolled back database')
        except:
            logger.error('Unable to roll back database: CHECK ENTRIES!')
            logger.debug(traceback.format_exc())
            raise 


def loopLogPages(conn, all_logs, callback, callback_args):
    '''Loop all the pages in the log applying the given callback function.
    
    The callback function expects to get back a copy of the all_logs object
    and the call_back_args as (all_logs, callback_args). If it doesn't it will
    raise an exeption when trying to return at the end.
    @note: list is iterated in reverse so any deletions will be sane.
    
    @param conn: an open database connection.
    @param all_logs: an instance of the AllLogs class.
    @param callback: a callback function to execute in the loop.
    @param callback_args: a dictionary of arguments for the callback function.
    @return: all_logs, callback_args (tuple). Updated by whatever happens in
             the callback function.
    '''
    
    def reverse_enumerate(iterable):
        '''Enumerate over an iterable in reverse order while retaining proper indexes
        '''
        return itertools.izip(reversed(xrange(len(iterable))), reversed(iterable))
    
    for page in all_logs.log_pages.values():
            
        if not page.has_contents: 
            #page.update_check[0] = False
            continue
        
        for i, values in reverse_enumerate(page.contents):
        
            page, callback_args = callback(conn, i, values, page, callback_args)
    
    return all_logs, callback_args
    

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
        log_pages, entries = findNewLogEntries(conn, log_pages, table_list)
        
        return entries
            
    except IOError:
        logger.error('IOError - Unable to access database')
    except:
        logger.error('SQLError - Could not query database')
    finally:
        if not conn == False:
            conn.close()


def findNewLogEntries(conn, log_pages, table_list):
    '''Checks entries against database to see if they're new or already exist.
    '''
    def callbackFunc(conn, i, values, page, callback_args):
        '''
        This function is a callback used by the looping function.
        '''
        if page.name == 'RUN':
            return page, callback_args
         
        is_new_entry = DatabaseFunctions.findNewEntries(
                                        conn, page.name, page.contents[i])
    
        table_dict = callback_args['table_dict']
           
        # Append the contents row, ui table name, row no., and whether it 
        # should be added to the table or not to the display_data list.
        # If it'a already in the database then we remove it from the log
        # dictionary to avoid entering it again. (see debug comment below)
        if not is_new_entry:
            callback_args['display_data'].append([page.contents[i], 
                                            table_dict[page.name], i, False])
            #DEBUG - I don't think this is necessary as it's dealt with by the
            #        False flag in the 'display_data'.
            #del log_pages[log_name][i]
        else:
            callback_args['display_data'].append([page.contents[i], 
                                            table_dict[page.name], i, True])
        
        return page, callback_args
    
    display_data = []
    
    # DEBUG - Deal with this earlier as it should be unnecessary here.
    table_keys, table_names = zip(*table_list)
    combo = zip(table_keys,table_names)
    table_dict = dict(combo)
    
    # Get the logs in object format
    all_logs = AllLogs(log_pages)
    callback_args = {'table_dict': table_dict, 'display_data': []}
    
    # Call the looping function, handing it our callback
    all_logs, callback_args = loopLogPages(conn, all_logs, callbackFunc, 
                                                            callback_args)
    log_pages = all_logs.getLogDictionary()
    display_data = callback_args['display_data']
    return log_pages, display_data
    

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
    '''Tests database to see if it's the right version.
    '''
    conn = False
    if not db_path == '' and not db_path == False:

        try:
            title = 'Load Error'
            # Need to check that the database is aligned with the current version
            version_check = DatabaseFunctions.checkDatabaseVersion(db_path)
            if version_check == DatabaseFunctions.DATABASE_VERSION_LOW:
#                 errors.DB_ACCESS, msgbox_error=True, 
#                                         msg_add=(':\n%s' % (db_path))
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
        
    except:
        msg = "Unable to load model log from file at: %s." % (db_path)
        logger.error('Unable to load model log from file at: \n%s' % (db_path))
        return entries, False, title, msg
    finally:
        conn.close()
 

def fetchAndCheckModel(db_path, open_path, log_type, errors, launch_error=True):
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
    
    # Load the model at the chosen path.
    log_pages = LogBuilder.loadModel(open_path, log_type)
    if log_pages == False:
        logger.error('Unable to load model file:\n%s' % (open_path))
        error.addError(errors.MODEL_LOAD, msg_add=('at:\n%s' % (open_path)))
        return errors, log_pages
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
                        logger.error('Model results alreads exist for :\n%s' % (main_ief))
                        errors.addError(errors.RESULTS_EXIST, 
                                        msg_add=('in:\n%s' % (main_ief)))
                        return errors, log_pages
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
                logger.error('Log entry already exists for :\n%s' % (open_path))
                errors.addError(errors.LOG_EXISTS, 
                                        msg_add=(':\nfile = %s' % (open_path)))
                return errors, log_pages
            else:
                return errors, log_pages
                    
        except IOError:
            logger.error('Cannot load file:\n%s' % (open_path))
            errors.addError(errors.IO_ERROR, 
                                        msg_add=('at:\n%s' % (open_path)))
            return errors, log_pages
        except:
            logger.error('Cannot load file:\n%s' % (open_path))
            errors.addError(errors.IO_ERROR, 
                                        msg_add=('at:\n%s' % (open_path)))
            return errors, log_pages
        

def updateDatabaseVersion(db_path, errors):
    '''Try to update database to latest version.
    @param db_path: path to the database to update.
    @return: None if user cancels or error_details otherwise. These can be:
             error_details['Success'] = True if all good or False otherwise.
             If False then other dict items contain details.
    '''
    try:
        DatabaseFunctions.updateDatabaseVersion(db_path)
        return errors
    except:
        logger.error('Failed to update database scheme: See log for details')
        errors.addError(errors.DB_SCHEMA, msgbox_error=True)
        return errors
    
    
def loadSetup(cur_settings_path, cur_log_path, errors):
    '''Load LogIT setup from file.
    '''
    d = MyFileDialogs()
    open_path = d.openFileDialog(path=os.path.split(cur_log_path)[0], 
                        file_types='Log Settings (*.logset)')
    
    cur_settings = None
    if open_path == False:
        return cur_settings, errors
    try:
        # Load the settings dictionary
        open_path = str(open_path)
        cur_settings = cPickle.load(open(open_path, "rb"))
        cur_settings.cur_settings_path = cur_settings_path
        return cur_settings, errors
    except:
        errors.addError(errors.SETTINGS_LOAD, msg_add='from:\n%s' % (open_path),
                                                            msgbox_error=True)
        logger.error('Could not load settings file')
        return cur_settings, errors
    
    
def exportToExcel(db_path, export_tables, save_path, errors):
    '''Export database to Excel (.xls) format at user chosen location.
    @param cur_log_path: the current log database file path.
    @param export_tables: list with order to create worksheet.
    @return dictionary containing error_details (or success details if
            error_details['Success'] is True.
    @note: launches file dialog.
    '''
    try:
        Exporters.exportToExcel(db_path, export_tables, save_path)
    except:
        logger.error('Could not export log to Excel')
        errors.addError(errors.EXPORT_EXCEL, msgbox_error=True)
        return errors
   
    logger.info('Database exported to Excel at:\n%s' % (save_path))
    return errors


    