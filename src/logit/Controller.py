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
        
    def deleteEntries(self, db_manager):
        '''Deletes all of the entries in this object from the database.
        @note: This may raise an error that should be dealt with by the 
               calling code.
        '''
        for name, table in self.tables.iteritems():
            for id in table: #reverse_enumerate(table):
                db_manager.deleteRow(name, id)
                

class RunIds(object):
    '''
    '''
    
    def __init__(self):
        '''
        '''
        self.ids = {'RUN': -1, 'TCF': [], 'ECF': [], 'TGC': [], 'TBC': [], 
                    'DAT': [], 'BC_DBASE': []}
        
    
    def add(self, page_name, id):
        '''
        '''
        if page_name == 'RUN':
            self.ids['RUN'] = id
        else:
            self.ids[page_name].append(id)
    
    
    def convertDict(self):
        '''
        '''
        self.run = self.ids['RUN']
        self.dat = self.ids['DAT']
        self.tgc = self.ids['TGC']
        self.tbc = self.ids['TBC']
        self.bc_dbase = self.ids['BC_DBASE']
        self.ecf = self.ids['ECF']
        self.tcf = self.ids['TCF']
        del self.ids
        
    def convertToDict(self):
        '''
        '''
        self.ids = {'RUN': self.run, 'TCF': self.tcf, 'ECF': self.ecf, 
                    'TGC': self.tgc, 'TBC': self.tbc, 'DAT': self.dat, 
                    'BC_DBASE': self.bc_dbase}
        
    
        

def updateLog(db_path, all_logs, errors, check_new_entries=False):
    '''Updates the log database with the current value of all_logs.
    
    This is just an entry function that connects to the database and and then
    call logEntryUpdates to do all of the hard work. It deals with handling
    any errors that might pop up and notifying the caller.
    @param dp_path: the path to the log database on file.
    @param all_logs: AllLogs object.
    @param check_new_entries=False: Flag identifying whether the values in the
           all_logs entries should be checked against the database before they
           are entered. i.e. make sure they don't alreay exist first. This is
           needed because the check may have already been carries out before
           and it will cost unnecessary processing effort.
    '''
    # Connect to the database and then update the log entries
    update_check = None
    try:
        db_manager = DatabaseFunctions.DatabaseManager(db_path)
        all_logs, update_check = logEntryUpdates(db_manager, all_logs,
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
        return errors, all_logs, update_check
 

def logEntryUpdates(db_manager, all_logs, check_new_entries=False):
    '''Update the database with the current status of the all_logs object.
    
    This creates a callback function and hands it to loopLogPages method,
    which loops through the log pages applying the call back each time.
    
    If there's an issue inserting any of the data into any of the tables it
    will attempt to roll back the changes to all of the tables to 'hopefully'
    avoid any corruption. This will be logged so the user is aware.
    
    @param conn: an open database connection.
    @param all_logs: AllLogs object containing the the data to enter into the 
           database under the database table names.
    @param check_new_entries=False: new entry status may be checked before 
           getting to this stage and we don't want to do it twice.
    @raise IOError: If there's any issue connecting to the database.
    @raise Exception: if anything else goes wrong. 
    
    '''
    
    added_rows = None    
    run_ids = None
    
    def insertSubFiles(db_manager, index, values, page, max_id):
        '''Insert files referenced by one of the log pages into its table.
        
        Looks to see if any of the files it contains aren't already entered. 
        If they aren't it adds them to the files table (e.g. TGC_FILES).
        Then converts to a bracket wrapped string for adding to main log table
        (e.g. TGC).
        '''
    
        new_files, ids = insertIntoModelFileTable(db_manager, 
                            page.subfile_name, page.name, 
                                values[page.name], values['FILES']) 
        #added_rows.addRows(page.subfile_name, ids)
          
        if not new_files == False:
            added_rows.addRows(page.subfile_name, ids)
            page.bracketFiles(index, 'NEW_FILES', new_files)
    
        page.bracketFiles(index, 'FILES')
        page.contents[index]['ID'] = max_id
        
        return page
     
    def insertMainFile(db_manager, index, page, max_id, check_entry, 
                                                        run_id=None):
        '''Adds the log page data in 'page' to the log page table.
        
        Will check if entry exists first if check_entry==True.
        '''
        try:
            result = None
            has_entry = False
            
            # Every entry gets put into the RUN_ID table. Unless it's RUN
            if not run_id == None:
                db_manager.insertValues('RUN_ID', 
                                    {'RUN_ID': run_id, 
                                     'FILE': page.contents[index][page.name],
                                     'TYPE': page.name
                                     })
            
            if check_entry:
                result = db_manager.findEntry(page.name, page.name,
                            page.contents[index][page.name], return_rows=True)
                has_entry = result[0]

            if not has_entry:

                db_manager.insertValues(page.name, page.contents[index])
                run_ids.add(page.name, max_id)
                added_rows.addRows(page.name, max_id)
                page.contents[index]['ID'] = max_id
                page.update_check = True

            else:
                id = result[2][0]['ID']
                run_ids.add(page.name, id)
                page.deleteItem(index)
                #page.update_check[index] = False
        except:
            logger.debug(traceback.format_exc())
            raise 
        
        return page
    
    def callbackFunc(db_manager, i, values, page, callback_args):
        '''Insert entries into database and update page values.
        This function is a callback used by the looping function.
        '''
        check_new_entries = callback_args['check_new_entries']
        run_id = callback_args['run_id']
        
        # We need the maximum id so that we can increment by 1 and put it into
        # the output table in the GUI.
        max_id = db_manager.getMaxId(page.name) + 1
        
        if page.multi_file:
            page = insertSubFiles(db_manager, i, values, page, max_id)
            
        if page.name == 'RUN':
            page = insertMainFile(db_manager, 0, page, max_id, False)
        else:
            page = insertMainFile(db_manager, i, page, max_id, 
                                  check_new_entries, run_id)
        
        return page, callback_args
    

    # Collects all files added to database for resetting
    run_ids = RunIds()
    added_rows = AddedRows()
    check_new_entries = True
    max_run_id = db_manager.getMaxId('RUN') + 1
    try:
        # Send function as a callback to the log page looping function.
        all_logs, callback_args = loopLogPages(db_manager, all_logs, callbackFunc, 
                                    {'check_new_entries': check_new_entries,
                                     'run_id': max_run_id})
        
        
        # Get the data from the classes in dictionary format
        update_check = all_logs.getUpdateCheck()
        return all_logs, update_check
    
    # This acts as a failsafe incase we hit an error after some of the entries
    # were already added to the database. It tries to roll back the entries by
    # deleting them. The exception is still raised to be dealt with by the GUI.
    except:
        logger.error('Problem updating database: attempting to roll back changes')
        logger.debug(traceback.format_exc())

        try:
            added_rows.deleteEntries(db_manager)
            logger.warning('Successfully rolled back database')
        except:
            logger.error('Unable to roll back database: CHECK ENTRIES!')
            logger.debug(traceback.format_exc())
            raise 


def loopLogPages(db_manager, all_logs, callback, callback_args):
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
        
            page, callback_args = callback(db_manager, i, values, page, callback_args)
    
    return all_logs, callback_args
    

def loadEntrysWithStatus(db_path, all_logs, table_list, errors):
    '''Loads the database and checks if the new entries exist.
    
    Builds a new list that stores the SubLog entry for each row as well as
    some info on the key to that table in the gui, whether the entry already
    exists or not adn the row count.
    Uses the findNewLogEntries function to fo the hard work.
    
    @param db_path: path to a database on file.
    @param all_logs: the all_logs object containing loaded model variables.
    @param table_list: a list of all of the keys for accessing thetables in the 
           'New log Entry' page of the GUI and the associated db tables.
    @return: list containing sub-lists of all of the rows to be displayed on
             the New log entry page tables.
    '''
     # We need to find if the TGC and TBC files have been registered with the
    # database before. If they have then we don't need to register them 
    # again.
    db_manager = DatabaseFunctions.DatabaseManager(db_path)
    try:
        entries = []
        all_logs, entries = findNewLogEntries(db_manager, all_logs, table_list)
        
    except IOError:
        logger.error('IOError - Unable to access database')
        errors.addError(errors.DB_ACCESS, msgbox_error=True, 
                                        msg_add=(':\n%s' % (db_path)))
    except:
        logger.error('SQLError - Could not query database')
        errors.addError(errors.DB_ACCESS, msgbox_error=True, 
                                        msg_add=(':\n%s' % (db_path)))
    finally:
        return entries, errors


def findNewLogEntries(db_manager, all_logs, table_list):
    '''Checks entries against database to see if they're new or already exist.
    '''
    def callbackFunc(db_manager, i, values, page, callback_args):
        '''
        This function is a callback used by the looping function.
        '''
        if page.name == 'RUN':
            return page, callback_args
         
        has_entry = db_manager.findEntry(page.name, page.name, 
                                                page.contents[i][page.name])
    
        table_dict = callback_args['table_dict']
           
        # Append the contents row, ui table name, row no., and whether it 
        # should be added to the table or not to the display_data list.
        # If it'a already in the database then we remove it from the log
        # dictionary to avoid entering it again. (see debug comment below)
        if has_entry:
            callback_args['display_data'].append([page.contents[i], 
                                            table_dict[page.name], i, False])
            #DEBUG - I don't think this is necessary as it's dealt with by the
            #        False flag in the 'display_data'. NOTE: currently not
            #        updated to use the AllLogs object.
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
    callback_args = {'table_dict': table_dict, 'display_data': []}
    
    # Call the looping function, handing it our callback
    all_logs, callback_args = loopLogPages(db_manager, all_logs, callbackFunc, 
                                                            callback_args)
    display_data = callback_args['display_data']
    return all_logs, display_data
    

def insertIntoModelFileTable(db_manager, table_name, col_name, model_file, 
                                                    files_list):
    '''Insert file references into the model file table if they are not
    already there.
    
    @param conn: the current database connection.
    @param table_name: the name of the column to insert the file name into.
    @param files_list: the list of files to check against the database.
    '''
    new_files = []
    added_count = 1
    ids = []
    for f in files_list:
        
        # Check if we have any matched to the file name.            
        results = db_manager.findEntry(table_name, col_name, f, 
                                                        return_rows=True) 
        
        # If we didn't find any matches we can put the file into the
        # files database under col_name and add it to the list so that we
        # can put it in the new files col of the main table.
        if results[0] == False:
            row_data = {col_name: model_file, 'FILES': f}
            db_manager.insertValues(table_name, row_data)
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


def deleteDatabaseRow(db_path, table_name, id, all_entry=False):
    '''Deletes the database row with the given id
    @param db_path: the path to the database on file.
    @param table_name: the name of the table.
    @param id: the unique id of the row to delete.
    @return: True if successful, false otherwise.
    '''
    db_manager = DatabaseFunctions.DatabaseManager(db_path)
    try:
        if all_entry:
            # Delete all associated rows
            _deleteAssociatedEntries(db_manager, id)

        # Delete the row from the database this will remove the run row if
        # all_entry == True
        db_manager.deleteRow(table_name, id)
        
    except IOError:
        logger.error('Unable to access database - see log for details')
        return False
    except Exception:
        logger.error('Unable to access database - see log for details')
        return False
    
    return True


def _deleteAssociatedEntries(db_manager, run_id):
    '''Delete all of the log page entries associated with the run_id
    '''
    # Get all of the table names in the database
    names = db_manager.getTableNames()
    
    # I think this is superflous now that wer've got rid of the need to do 
    # the pickling and storing of id's in an object in the database.
#     run_results = db_manager.findEntry('RUN', 'ID', run_id, return_rows=True)
#     run_id = run_results[2][0]['ID']
    
    # Get all the entries made with this run_id and then delete them
    file_results = db_manager.findEntry('RUN_ID', 'RUN_ID', run_id, return_rows=True)
    db_manager.deleteClause('RUN_ID', 'RUN_ID', run_id)

    # Search the RUN_ID table to see if there are any file name matches with
    # the ones we just deleted. If there is then we can't delete the associated
    # rows in the page tables.
    del_list = []
    for file in file_results[2]:
        result = db_manager.findEntry('RUN_ID', 'FILE', file['FILE'], return_rows=True)
        if not result[0]:
            del_list.append([file['TYPE'], file['FILE']])
    
    # Delete any TGC, TBC etc entries that are no longer needed.
    for item in del_list:
        db_manager.deleteClause(item[0], item[0], item[1])
        
        if not item[0] == 'DAT':
            files_name = item[0] + '_FILES'
            db_manager.deleteClause(files_name, item[0], item[1])
        

    
def checkDatabaseVersion(db_path, errors):
    '''Tests database to see if it's the right version.
    '''
    if not db_path == '' and not db_path == False:

        try:
            db_manager = DatabaseFunctions.DatabaseManager(db_path)
            # Need to check that the database is aligned with the current version
            version_check = db_manager.checkVersion()
            if version_check == DatabaseFunctions.DATABASE_VERSION_LOW:
                logger.error('Database version is old - please update database')
                errors.addError(errors.DB_OLD, msgbox_error=True, 
                                        msg_add=':\n%s' % (db_path)) 
                return errors
                
            elif version_check == DatabaseFunctions.DATABASE_VERSION_HIGH:
                logger.error('Database version in new - please update LogIT')
                errors.addError(errors.DB_NEW, msgbox_error=True, 
                                        msg_add=':\n%s' % (db_path)) 
                return errors
            
            # Just to check it works
            db_manager.cur.execute("Select * from RUN")
              
            return errors
        except:
            errors.addError(errors.DB_ACCESS, msgbox_error=True, 
                                        msg_add=':\n%s' % (db_path)) 
            return errors
    

def fetchTableValues(db_path, table_list, errors):
    '''Fetches all rows from the given table name.
    @param db_path: path to a database on file.
    @param table_name: name of the table to fetch rows from.
    @return: tuple (boolean success flag, row count, row data) or an error
             with (False, error title, message)
    '''
    entries = []
    try:
        db_manager = DatabaseFunctions.DatabaseManager(db_path)
                
        for table in table_list:
            # If there's nothing in the table it will fail, but we don't care
            # so just pass the error.
            try:
                results = db_manager.findAll(table[0], return_rows=True)
                 
                entries.append([table[0], table[1], results[0], results[1], results[2]])
            except:
                pass           
        
        return entries, errors
        
    except:
        errors.addError(errors.MODEL_LOAD_ERROR, msgbox_error=True,
                        msg_add=':\n%s' % (db_path))
        return entries, errors
 

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
    @return: tuple containing AllLogs (which could be the loaded log
             pages or False if the load failed and a dictionary containing
             the load status and messages for status bars and errors.
    '''   
    
    # Load the model at the chosen path.
    all_logs = LogBuilder.loadModel(open_path, log_type)
    if all_logs == False:
        logger.error('Unable to load model file:\n%s' % (open_path))
        errors.addError(errors.MODEL_LOAD, msg_add=('at:\n%s' % (open_path)), 
                                                        msgbox_error=True)
        return errors, all_logs
    else:
        # Make sure that this ief or tcf do not already exist in the
        # database. You need new ones for each run so this isn't
        # allowed.
        main_ief = all_logs.getLogEntryContents('RUN', 0)['IEF'] 
        main_tcf = all_logs.getLogEntryContents('RUN', 0)['TCF'] 
        tcf_results = all_logs.getLogEntryContents('RUN', 0)['RESULTS_LOCATION_2D'] 
        
        indb = False
        found_path = ''
        
        try:
            db_manager = DatabaseFunctions.DatabaseManager(db_path)
            # If we have an ief get the ief name to see if we already
            # recorded a run using that model
            if not main_ief == 'None':
                indb = db_manager.findEntry('RUN', 'IEF', main_ief,
                                                    column_only=True)
                
                # Then check if we've already used the results locations
                # location for a previous run and return error if it has.
                if indb:
                    indb = db_manager.findEntry('RUN', 'RESULTS_LOCATION_1D', 
                                            tcf_results,column_only=True)
                    
                    if exists[0]:
                        logger.error('Model results alreads exist for :\n%s' % (main_ief))
                        errors.addError(errors.RESULTS_EXIST, 
                                        msg_add=('in:\n%s' % (main_ief)), 
                                                        msgbox_error=True)
                        return errors, all_logs
                    
                found_path = main_ief
            
            # Do the whole lot again for the tuflow run
            if not main_tcf == 'None':
                if not indb:
                    indb = db_manager.findEntry('RUN', 'TCF', 
                                            main_tcf,column_only=True)
                    found_path = main_tcf
            
            if indb:
                logger.error('Log entry already exists for :\n%s' % (open_path))
                errors.addError(errors.LOG_EXISTS, 
                                        msg_add=(':\nfile = %s' % (open_path)),
                                                            msgbox_error=True)
                return errors, all_logs
            else:
                return errors, all_logs
                    
        except IOError:
            logger.error('Cannot load file:\n%s' % (open_path))
            errors.addError(errors.IO_ERROR, 
                                        msg_add=('at:\n%s' % (open_path)),
                                                            msgbox_error=True)
            return errors, all_logs
        except:
            logger.error('Cannot load file:\n%s' % (open_path))
            errors.addError(errors.IO_ERROR, 
                                        msg_add=('at:\n%s' % (open_path)),
                                                            msgbox_error=True)
            return errors, all_logs
        

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


    