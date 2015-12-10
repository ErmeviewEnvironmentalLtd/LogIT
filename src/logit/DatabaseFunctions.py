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
# Module:  DatabaseFunctions.py
# Date:  16/11/2014
# Author:  Duncan Runnacles
# Version:  1.1
# 
# Summary:
#    Contains all of the functions that communicate with the database. These
#    included generic select and update queries, as well as specific actions
#    and workflows required by the software.
#
# UPDATES:
#    DR - 19/11/2014
#        Added functionality to update an existing database if there are 
#        changes to the way that the software uses the log database. This means
#        that existing databases can be converted to the format used in new 
#        releases without losing data/starting again.
#
# TODO:
#    The functions almost entirely use string replacement to create the
#    queries. This is not good practice (although probably fairly safe from
#    problems while the software is used locally). This should be changed to
#    use placeholders. The problem with placeholders is that you can't use them
#    for table names, so need to find a way around this.
#
###############################################################################
'''

import os
import sqlite3
from _sqlite3 import OperationalError, Error
import shutil
import traceback

import logging
logger = logging.getLogger(__name__)

DATABASE_VERSION_NO = 3
DATABASE_VERSION_SAME = 0
DATABASE_VERSION_LOW = 1
DATABASE_VERSION_HIGH = 2


class DatabaseManager(object):
    '''Database class
    
    :note: This should not be subclassed as it relies on __del__ to close the
           connection. If you need to subclass it you will have to use the
           weakref module. Just don't do it.
    '''
    
    def __init__(self, db):
        '''Initiate the log by loading it.
        :raise exception: if there's an issue.
        '''
        self.conn = loadLogDatabase(db)
        self.cur = self.conn.cursor()
#         version = self.checkVersion()
#         if not version == DATABASE_VERSION_SAME:
#             if report_version:
#                 return version
#             else:
#                 raise sqlite3.DatabaseError
        
        #self.conn.execute('pragma foreign_keys = on')
        #self.conn.commit()
#         if report_version:
#             return version


    def __del__(self):
        self.conn.close()
        

    def getMaxId(self, table_name):
        '''Return the highest id value in given table_name
        '''
        query = 'SELECT max(id) FROM %s' % (table_name)
        self.readQuery(query)
        max_id = self.cur.fetchone()[0]
        if max_id == None:
            return 0
        else:
            return max_id

    # deleteRowFromTable
    def deleteRow(self, table_name, row_id):
        '''
        '''
        query = "delete from %s where ID='%s'" % (table_name, row_id)
        self.writeQuery(query)
        
    # insertValuesIntoTable
    def insertValues(self, table_name, row_data):   
        
        columns = ', '.join(row_data.keys())
        placeholders = ", ".join('?' * len(row_data))
        query = 'insert into ' + table_name + ' ({}) values ({})'.format(columns, placeholders)
        self.writeQuery(query, row_data)

    # saveViewChangesToDatabase
    def updateRow(self, table_name, key, values, id):
        '''
        '''
        query = "update %s set %s='%s' where ID=%s" % (table_name, key, value, id)
        self.writeQuery(query)

    # findInDatabase
    def findEntry(self, table_name, col_name, entry, column_only=False, 
                                                    return_rows=False):
        '''
        '''
        if not column_only:
            query = "select * from %s where %s='%s'" % (table_name, col_name, entry)
        else:
            query = "select %s from %s where %s='%s'" % (col_name, table_name, col_name, entry)
        
        self.cur.execute(query)
        result = self._getEntriesFromCursor()
        if return_rows:
            return result
        else:
            return result[0]
    
    # findInDatabase
    def findAll(self, table_name, col_name=False, return_rows=False):
        '''
        '''
        if col_name == False:
            query = "select * from %s" % (table_name)
        else:
            query = "select %s from %s" % (col_name, table_name)
        
        self.cur.execute(query)
        result = self._getEntriesFromCursor()
        if return_rows:
            return result
        else:
            return result[0]
            
    # checkDatabaseVersion
    def checkVersion(self):
        '''
        '''
        self.cur.execute("pragma user_version")
        db_version = self.cur.fetchone()[0]
         
        # If the VERSION_NO doesn't match the current one.
        if not db_version == DATABASE_VERSION_NO:
            if db_version > DATABASE_VERSION_NO:
                return DATABASE_VERSION_HIGH
            
            if db_version < DATABASE_VERSION_NO:
                return DATABASE_VERSION_LOW
        else:
            return DATABASE_VERSION_SAME       
    

    def readQuery(self, query):
        try:
            self.cur.execute(query)
            return self.cur
        except self.conn.Error:
            logger.error('Problem querying database')
            logger.debug(traceback.format_exc())
            raise ValueError


    def writeQuery(self, query, row_data=None):
        try:
            if row_data == None:
                self.cur.execute(query)
            else:
                self.cur.execute(query, row_data.values())

            self.conn.commit()
            return self.cur

        except self.conn.Error:
            conn.rollback()
            logger.debug(traceback.format_exc())
            logger.error('SQL exception when trying to perform\n' +
                         'sql: %s' % (query))
            raise ValueError
            
        
    def _getEntriesFromCursor(self):
        '''
        '''
        #found_it = False
        found_rows = []
        result = self.cur.fetchall()
        if not result == None:
            
            count = len(result)
            if count > 0:
                #found_it = True
                # Convert the row factory to a dictionary of the row variables
                for row in result:
                    found_rows.append(self._convertRowToDictionary(row))
                    
                # Return here if we found stuff and return_rows is True
                return (True, count, found_rows)
        
        return (False, 0, [])


    def _convertRowToDictionary(self, row):
        '''Converts a sqlite3 row_factory into a dictionary
        
        @param row: the row_factory object from sqlite3 cursor.
        @return: dictionary containing the values in the given row with keys
                 set as the column names.
        '''
        d = {}
        for idx, col in enumerate(self.cur.description):
            d[col[0]] = row[idx]
        return d



'''
##############################################################################
    Below here is all of the module wide functionality for doing the creation,
    updating, deleting, etc of the database.
    
    It's done quite rarely so it doesn't need to be in class functionality I
    don't think. It will just make the class messy and hard to follow.

##############################################################################
'''

def createNewLogDatabase(db_path):
    '''Creates a new SqLite database and sets up the tables for adding the
    log entries into.
    
    @param db_path: path to use to create the database.
    '''
    conn = None
    
    if os.path.exists(db_path):
        logger.warning('Database already exists - Resetting to new')
        dropAllTables(db_path)
        
    try:
        conn = sqlite3.connect(db_path)
        
        logger.debug('New log database created at: ' + db_path)
        cur = conn.cursor()
        
        createRunTable(cur)
        logger.info('Run table created')
        
        createTgcTable(cur)
        logger.info('Tgc table created')
    
        createTbcTable(cur)
        logger.info('Tbc table created')
    
        createDatTable(cur) 
        logger.info('Dat table created')
        
        createEcfTable(cur)
        logger.info('Ecf table created')
        
        createTcfTable(cur)
        logger.info('Tcf table created')

        createBcTable(cur)
        logger.info('BC Database table created')
        
        createTgcFilesTable(cur)
        logger.info('Tgc Files table created')
    
        createTbcFilesTable(cur)
        logger.info('Tbc Files table created')
    
        createBcFilesTable(cur)
        logger.info('BC Database Files table created')
        
        createEcfFilesTable(cur)
        logger.info('Ecf Files table created')
        
        createTcfFilesTable(cur)
        logger.info('Tcf Files table created')
        
        cur.execute("pragma user_version = %s" % DATABASE_VERSION_NO)
        
        conn.commit()

    except OperationalError:
        conn.rollback()
        logger.error('Error creating log database - OperationalError')
        logger.debug(traceback.format_exc())
    except IOError:
        logger.error('Error creating log database - IOError')
        logger.debug(traceback.format_exc())
    finally:
        if not conn == None:
            conn.close()


def createRunTable(cur):
    '''Create the run table
    
    @param cur: a cursor to an open database connection
    '''
    cur.execute('''CREATE TABLE RUN
                 (ID                      INTEGER    PRIMARY KEY    NOT NULL,
                  DATE                    TEXT                      NOT NULL,
                  MODELLER                TEXT,
                  RESULTS_LOCATION_2D     TEXT,
                  RESULTS_LOCATION_1D   TEXT,
                  EVENT_DURATION          TEXT,
                  DESCRIPTION             TEXT,
                  COMMENTS                TEXT,
                  SETUP                   TEXT,
                  ISIS_BUILD              TEXT,
                  IEF                     TEXT,
                  DAT                     TEXT,
                  TUFLOW_BUILD            TEXT,
                  TCF                     TEXT,
                  TGC                     TEXT,
                  TBC                     TEXT,
                  BC_DBASE                TEXT,
                  ECF                     TEXT,
                  EVENT_NAME              TEXT);
                 ''')
    
    
def createTgcTable(cur):
    '''Create the tgc table
    
    @param cur: a cursor to an open database connection
    '''
    cur.execute('''CREATE TABLE TGC
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    DATE           TEXT                       NOT NULL,
                    TGC            TEXT,
                    FILES          TEXT,
                    NEW_FILES      TEXT,
                    COMMENTS       TEXT);
                    ''')
    

def createTbcTable(cur):
    '''Create the tbc table
    
    @param cur: a cursor to an open database connection
    '''
    cur.execute('''CREATE TABLE TBC
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    DATE           TEXT                       NOT NULL,
                    TBC            TEXT,
                    FILES          TEXT,
                    NEW_FILES      TEXT,
                    COMMENTS       TEXT);
                    ''')
    
    
def createDatTable(cur):
    '''Create the dat table
    
    @param cur: a cursor to an open database connection
    '''
    cur.execute('''CREATE TABLE DAT
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    DATE           TEXT                       NOT NULL,
                    DAT            TEXT,
                    AMENDMENTS     TEXT,
                    COMMENTS       TEXT);
                    ''')


def createBcTable(cur):
    '''Create the bc_dbase table
    
    @param cur: a cursor to an open database connection
    '''
    cur.execute('''CREATE TABLE BC_DBASE
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    DATE           TEXT                       NOT NULL,
                    BC_DBASE       TEXT,
                    FILES          TEXT,
                    NEW_FILES      TEXT,
                    COMMENTS       TEXT);
                    ''')
    

def createEcfTable(cur):
    '''Create the ecf table
    
    @param cur: a cursor to an open database connection
    '''
    cur.execute('''CREATE TABLE ECF
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    DATE           TEXT                       NOT NULL,
                    ECF            TEXT,
                    FILES          TEXT,
                    NEW_FILES      TEXT,
                    COMMENTS       TEXT);
                    ''')
    

def createTcfTable(cur):
    '''Create the tcf table
    
    @param cur: a cursor to an open database connection
    '''
    cur.execute('''CREATE TABLE TCF
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    DATE           TEXT                       NOT NULL,
                    TCF            TEXT,
                    FILES          TEXT,
                    NEW_FILES      TEXT,
                    COMMENTS       TEXT);
                    ''')
    

def createTgcFilesTable(cur):
    '''Create the tgc_files table
    
    @param cur: a cursor to an open database connection
    '''
    cur.execute('''CREATE TABLE TGC_FILES
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    TGC            TEXT,
                    FILES          TEXT);
                    ''')
    

def createTbcFilesTable(cur):
    '''Create the tbc_files table
    
    @param cur: a cursor to an open database connection
    '''
    cur.execute('''CREATE TABLE TBC_FILES
                    (ID                INTEGER     PRIMARY KEY    NOT NULL,
                    TBC                TEXT,
                    FILES              TEXT);
                    ''')
    
    
def createBcFilesTable(cur):
    '''Create the bc_dbase_files table
    
    @param cur: a cursor to an open database connection
    '''
    cur.execute('''CREATE TABLE BC_DBASE_FILES 
                    (ID                INTEGER     PRIMARY KEY    NOT NULL,
                    BC_DBASE           TEXT,
                    FILES              TEXT);
                    ''')
    

def createEcfFilesTable(cur):
    '''Create the ecf_files table
    
    @param cur: a cursor to an open database connection
    '''
    cur.execute('''CREATE TABLE ECF_FILES 
                    (ID                INTEGER     PRIMARY KEY    NOT NULL,
                    ECF                TEXT,
                    FILES              TEXT);
                    ''')


def createTcfFilesTable(cur):
    '''Create the tcf_files table
    
    @param cur: a cursor to an open database connection
    '''
    cur.execute('''CREATE TABLE TCF_FILES 
                    (ID                INTEGER     PRIMARY KEY    NOT NULL,
                    TCF                TEXT,
                    FILES              TEXT);
                    ''')

        
def dropAllTables(db_path):
    '''Drops all of the tables in the database at the given path.
    
    @param db_path: the path to the sqlite3 database.
    '''
    con = None
    try:
        con = sqlite3.connect(db_path)
        con.isolation_level = None
        try:
            cur = con.cursor()
            cur.execute('''DROP TABLE IF EXISTS RUN''')
            cur.execute('''DROP TABLE IF EXISTS TGC''')
            cur.execute('''DROP TABLE IF EXISTS TBC''')
            cur.execute('''DROP TABLE IF EXISTS DAT''')
            cur.execute('''DROP TABLE IF EXISTS BC_DBASE''')
            cur.execute('''DROP TABLE IF EXISTS ECF''')
            cur.execute('''DROP TABLE IF EXISTS TCF''')
            cur.execute('''DROP TABLE IF EXISTS TGC_FILES''')
            cur.execute('''DROP TABLE IF EXISTS TBC_FILES''')
            cur.execute('''DROP TABLE IF EXISTS BC_DBASE_FILES''')
            cur.execute('''DROP TABLE IF EXISTS ECF_FILES''')
            cur.execute('''DROP TABLE IF EXISTS TCF_FILES''')
            con.commit()
        except con.Error:
            con.rollback()
            logger.warning('Cannot drop tables - Sql Error')
            logger.debug(traceback.format_exc())
    except IOError:
        logger.error('Could not connect to database')
        logger.debug(traceback.format_exc())
        if not con == None:
            con.close()
            

# Setup for this version of the database
run = ['ID', 'DATE', 'MODELLER', 'RESULTS_LOCATION_2D', 'RESULTS_LOCATION_1D', 
       'EVENT_DURATION', 'DESCRIPTION', 'COMMENTS', 'SETUP', 'ISIS_BUILD', 
       'IEF', 'DAT', 'TUFLOW_BUILD', 'TCF', 'TGC', 'TBC', 'BC_DBASE', 'ECF',
       'EVENT_NAME'] 
tgc = ['ID', 'DATE', 'TGC', 'FILES', 'NEW_FILES', 'COMMENTS']
tbc = ['ID', 'DATE', 'TBC', 'FILES', 'NEW_FILES', 'COMMENTS']
dat = ['ID', 'DATE', 'DAT', 'AMENDMENTS', 'COMMENTS']
bc_dbase = ['ID', 'BC_DBASE', 'FILES', 'NEW_FILES', 'COMMENTS']
ecf = ['ID', 'ECF', 'FILES', 'NEW_FILES', 'COMMENTS']
tcf = ['ID', 'TCF', 'FILES', 'NEW_FILES', 'COMMENTS']
tgc_files = ['ID', 'TGC', 'FILES']
tbc_files = ['ID', 'TBC', 'FILES']
bc_dbase_files = ['ID', 'BC_DBASE', 'FILES']
ecf_files = ['ID', 'ECF', 'FILES']
tcf_files = ['ID', 'TCF', 'FILES']

cur_tables = {'RUN': run, 'TGC': tgc, 'TBC': tbc, 'DAT': dat, 'ECF': ecf, 'TCF': tcf,
              'BC_DBASE': bc_dbase, 'TGC_FILES': tgc_files, 
              'TBC_FILES': tbc_files, 'BC_DBASE_FILES': bc_dbase_files,
              'ECF_FILES': ecf_files, 'TCF_FILES': tcf_files
             }

def buildTableFromName(table_type, cur):
    '''Builds the table based on the name
    
    @param table_type: the type of table to build.
    '''
    try:
        table_types = {'RUN': createRunTable, 'TGC': createTgcTable, 
                        'TBC': createTbcTable, 'DAT': createDatTable, 
                        'BC_DBASE': createBcTable, 'ECF': createEcfTable,
                        'TCF': createTcfTable,
                        'TGC_FILES': createTgcFilesTable, 
                        'TBC_FILES': createTbcFilesTable, 
                        'BC_DBASE_FILES': createBcFilesTable,
                        'ECF_FILES': createEcfFilesTable,
                        'TCF_FILES': createTcfFilesTable
                       }
        
        table_types[table_type](cur)
    except:
        logger.debug(traceback.format_exc())
        raise Exception
    

def updateDatabaseVersion(db_path):
    '''Update an existing version of the database to the latest version of
    the software.
    
    @param db_path: the path to the sqlite3 database.
    '''
    version_check = checkDatabaseVersion(db_path)
    if version_check == DATABASE_VERSION_SAME:
        logger.error('Database version is up to date')
        return True
    elif version_check == DATABASE_VERSION_HIGH:
        logger.error('Database version is newer than LogIT - please update LogIT') 
        return False
    
    conn = None
    try:
        # Make a backup of the database
        if os.path.exists(db_path):
            db_dir, fname = os.path.split(db_path)
            fname = os.path.splitext(fname)[0]
            shutil.copyfile(db_path, os.path.join(db_dir, fname + '_backup.logdb'))
            
        conn = sqlite3.connect(db_path)
        
        # Check if the database needs updating and update it if it does.
        success = testDatabaseCompatibility(conn, True)
        if success:
            cur = conn.cursor()
            cur.execute("pragma user_version = %s" % DATABASE_VERSION_NO)
            logger.info('Database successfully Updated - Current DB version = %s' % str(DATABASE_VERSION_NO))

    except sqlite3.Error:
            conn.rollback()
            logger.warning('Cannot query database - Sql Error')
            logger.debug(traceback.format_exc())
            return False
    except IOError:
        conn.rollback()
        logger.error('Could not connect to database')
        logger.debug(traceback.format_exc())
        return False
    finally:
        if not conn == None:
            conn.close()
    

def testDatabaseCompatibility(conn, add_update=False):
    '''Test the database at the given path to see if it is compatible with this
    version of LogIT.
    
    @param db_path: the path to the sqlite3 database.
    '''
    try:
        cur = conn.cursor()
        for tab in cur_tables:

            # Check if the table name exists in the master table schema
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % (tab)
            cur.execute(query)
            
            result = cur.fetchone()
            if result == None or result[0] < 1:
                if add_update:
                    buildTableFromName(tab, cur)
                else:
                    conn.close()
                    return False
            
            # Get the table information for the given table name and check
            # that it contains all the columns we expect
            cur.execute("pragma table_info(%s)" % tab)
            data = cur.fetchall()
            
            data_names = []
            for d in data:
                data_names.append(d[1])
             
            # Check if most recent column names are in the database table
            update_cols = []
            for col in cur_tables[tab]:
                
                if not col in data_names:
                    
                    # If we are updating store it.
                    if add_update:
                        update_cols.append(col)
                    else:
                        conn.close()
                        return False
            
            # If we're updating then add the missing columns
            if add_update and not len(update_cols) < 1:
                for col in update_cols:
                    query = "alter table %s add column '%s' 'TEXT'" % (tab, col)
                    cur.execute(query)
        
        if add_update:
            conn.commit()
                 
    except conn.Error:
        conn.rollback()
        logger.warning('Cannot query database - Sql Error')
        logger.debug(traceback.format_exc())
        return False

    
    return True

# def getMaxIDFromTable(conn, table_name):
#     '''Returns the highest id value in the given table.
#     
#     @param conn: open sqlite3 database connection.
#     @param table_name: the name of the table to query.
#     @return: int of the maximum id number in the table.
#     '''
#     try:
#         cur = conn.cursor()
#         query = 'SELECT max(id) FROM %s' % (table_name)
#         cur.execute(query)
#         max_id = cur.fetchone()[0]
#         if max_id == None:
#             return 0
#         else:
#             return max_id
#     
#     except conn.Error:
#         logger.error('Problem querying database')
#         logger.debug(traceback.format_exc())
#         raise Exception
#     except Exception:
#         logger.error('Problem querying database')
#         logger.debug(traceback.format_exc())
#         raise Exception
#     
#     
# def deleteRowFromTable(conn, table_name, row_id):
#     '''Delete the row from the given table referenced by the given ID value.
#     
#     @param conn: an open database connection.
#     @param table_name: the name of the table to query.
#     @param row_id: the 'ID' key of the row to be deleted.
#     '''
#     try:
#         cur = conn.cursor()
#         query = "delete from %s where ID='%s'" % (table_name, row_id)
#         cur.execute(query)
#         
#         conn.commit()
#         
#     except conn.Error:
#         conn.rollback()
#         logger.debug(traceback.format_exc())
#         logger.error('SQL error when trying to delete\n' +
#                       'row: %s\n' +
#                       'table: %s' % (row_id, table_name))
#     except Exception:
#         conn.rollback()
#         logger.debug(traceback.format_exc())
#         logger.error('Unknown exception when trying to delete\n' +
#                       'row: %s\n' +
#                       'table: %s' % (row_id, table_name))
#     
# 
# def insertValuesIntoTable(conn, table_name, row_data):        
#     '''Put the values from the model run record into the database at the
#     table defined by the name.
#     
#     If values if left to default the table_name parameter will be used to
#     get the values from the log_pages dictionary. Otherwise the values
#     list provided will be used. It must match the number of columns in the
#     table or an error will be thrown.
#     
#     @param conn: the database connection.
#     @param cursor: cursor for the database connection.
#     @param table_name: the name of the table to update.
#     @param row_data=None: Dictionary containing the values to be put into 
#            the columns.
#     '''        
#     try:
#         cur = conn.cursor()
#         columns = ', '.join(row_data.keys())
#         placeholders = ", ".join('?' * len(row_data))
#             
#         query = 'insert into ' + table_name + ' ({}) values ({})'.format(columns, placeholders)
#         cur.execute(query, row_data.values())
#             
#         conn.commit()
#     
#     except conn.Error:
#         conn.rollback()
#         logger.debug(traceback.format_exc())
#         logger.error('Failed to insert row_data into %s table' % (table_name))
#         raise Error
#     
# 
# def saveViewChangesToDatabase(table_name, save_dict, id_key, db_path):
#     '''Saves the edits made to the row in the View Log table to the database
#     based on the id value in the row that was clicked to launch the context
#     menu.
#     
#     @param table_widget: the table in the user form to takes  updates from.
#     @param table_name: the name of the database table to update.
#     '''
#     conn = None
#     error_text = False
#     
#     try:
#         # Connect to the database
#         conn = loadLogDatabase(db_path)
#         try:
#             cur = conn.cursor()
#             
#             for key, value in save_dict.iteritems():
#                 query = "update %s set %s='%s' where ID=%s" % (table_name, key, value, id_key)
#                 cur.execute(query)
#             
#             conn.commit()
#             #cur.execute('commit')
#         except conn.Error:
#             conn.rollback()
#             logger.debug(traceback.format_exc())
#             logger.error('Unable to update database') 
#             error_text = 'SQLError'
#      
#     except IOError:
#         logger.debug(traceback.format_exc())
#         logger.error('Cannot connect to database at: %s' % db_path)
#         error_text = 'IOError'
#     finally:
#         if not conn == None:
#             conn.close()
#     
#     return error_text
# 
# 
# def findInDatabase(table_name, db_path=False, conn=False, col_name=False, 
#                    db_entry=False, return_rows=False, only_col_name=False):
#     '''Check if the given db_entry exists in the given database.
#     
#     Can be called using either a path to an existing database or an open
#     database connection.
#     
#     @param table_name: the name of the table to search in the database.
#     @param col_name: the name of the column to search.
#     @param db_entry: the value to look up and check for existence in the databse.
#     @param db_path=None: a path variable to an existing database.
#     @param conn=False: an open database connection.
#     @param return_ids=False: if set to True it will return a tuple containing
#            the row id's of every entry found.
#     @return: True if db_entry is found or False otherwise. Will return a tuple
#              containing the boolean and a tuple of row id's if return_ids is
#              set to True.
#     @raise IOError: if a connection to the database at the givn db_path cannot
#            be established.
#     @raise Error: if there is any problem with querying the database, such as
#            the table_name does not exist etc causing OperationalError or
#            sqlite3.Error it will be logged and this Error will be raised. 
#            
#     TODO:
#         Update comments
#     '''
#     found_it = False
#     found_rows = []
#     try:
#         if conn == False and not db_path == False: 
#             conn = loadLogDatabase(db_path)
#             conn.row_factory = sqlite3.Row
#         elif conn == False and db_path == False:
#             logger.error('No connection of database path provided')
#             raise Error
#             
#         try:
#             # Perform the search based on the variables provided
#             cur = conn.cursor()
#             if not col_name == False and db_entry == False and not only_col_name == False:
#                 query = "select %s from %s" % (col_name, table_name)
#                 
#             elif not col_name == False and not db_entry == False and only_col_name == True:
#                 query = "select %s from %s where %s='%s'" % (col_name, 
#                                             table_name, col_name, db_entry)
#             
#             elif not col_name == False and not db_entry == False and only_col_name == False:
#                 query = "select * from %s where %s='%s'" % (table_name, 
#                                                         col_name, db_entry)
#             else:
#                 query = "select * from %s" % (table_name)
#                 
#             cur.execute(query)
#             result = cur.fetchall()
#             if not result == None:
#                 
#                 count = len(result)
#                 if count > 0:
#                     found_it = True
#                     
#                     # Convert the row factory to a dictionary of the row variables
#                     if return_rows:
#                         for row in result:
#                             found_rows.append(convertRowToDictionary(cur, row))
#                         
#                         # Return here if we found stuff and return_rows is True
#                         return (True, count, found_rows)
#             
#         except conn.Error():
#             conn.rollback()
#             logger.debug(traceback.format_exc())
#             logger.error('Failed to query database')
#             raise Error
#     
#     except IOError:
#         logger.debug(traceback.format_exc())
#         logger.error('Cannot load the database')
#         raise Error
#     except:
#         logger.debug(traceback.format_exc())
#         logger.error('Cannot load the database')
#         raise Error
#     finally:
#         # If we were given a connection (as shown but not having a db_path then
#         # we probably shouldn't close it.
#         if not db_path == False:
#             if not conn == False:
#                 conn.close()
#     
#     return (found_it,)
# 
# 
# def findNewEntries(conn, t_name, model_entry):
#     '''Find if the given model entry already exists in the database or not.
#     '''
#     try:
#         cur = conn.cursor()
#         is_new = False
#         query = "select * from %s where %s='%s'" % (t_name, t_name, model_entry[t_name])
#         cur.execute(query)
#         if cur.fetchone() == None:
#             is_new = True
#             logger.info('%s file does not yet exist in database' % (t_name))
#         conn.commit()
# 
#     except conn.Error:
#         conn.rollback()
#         logger.error('SQLError - Unable to complete query')
#         logger.debug(traceback.format_exc())
#         raise Error
#     
#     return is_new


# def convertRowToDictionary(cursor, row):
#     '''Converts a sqlite3 row_factory into a dictionary
#     
#     @param cursor: the cursor from the database connection.
#     @param row: the row_factory object from sqlite3 cursor.
#     @return: dictionary containing the values in the given row with keys
#              set as the column names.
#     '''
#     d = {}
#     for idx,col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d


def loadLogDatabase(db_path):
    '''Load a log database from file
    
    @param db_path: path to the sqlite database to load
    '''
    con = False
    
    try:
        con = sqlite3.connect(db_path)
        logger.debug('Loaded log database at: ' + db_path)
    except:
        logger.error('Could not load log database at: ' + db_path)
        logger.debug(traceback.format_exc())
    
    return con


def checkDatabaseVersion(db_path):
    '''Check the database version number to make sure it is the same as the
    current version of the software. If it's not we return False because the
    user needs to either update the database settings or use an older version.
    
    @param db_path: path to an existing database.
    @param version_no: the database version used by this version of LogIT.
    @raise IOError: if db_path does not point to a database or it is not a
           LogIT database file.
    '''
    if not os.path.exists(db_path):
        raise IOError
    if not os.path.splitext(os.path.split(db_path)[1])[1] == '.logdb':
        raise IOError
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()
            cur.execute("pragma user_version")
            db_version = cur.fetchone()[0]
             
            # If the VERSION_NO doesn't match the current one.
            if not db_version == DATABASE_VERSION_NO:
                if db_version > DATABASE_VERSION_NO:
                    return DATABASE_VERSION_HIGH
                
                if db_version < DATABASE_VERSION_NO:
                    return DATABASE_VERSION_LOW
            else:
                return DATABASE_VERSION_SAME       
            
        except conn.error:
            logger.error('Sql query error')
            logger.debug(traceback.format_exc())
        
    except IOError:
        logger.error('Unable to access database')
        logger.debug(traceback.format_exc())
    except Exception:
        logger.error('Unable to access database')
        logger.debug(traceback.format_exc())
    finally:
        if not conn == None:
            conn.close()
    
    return True
     

# def createNewLogDatabase(db_path):
#     '''Creates a new SqLite database and sets up the tables for adding the
#     log entries into.
#     
#     @param db_path: path to use to create the database.
#     '''
#     conn = None
#     
#     if os.path.exists(db_path):
#         logger.warning('Database already exists - Resetting to new')
#         dropAllTables(db_path)
#         
#     try:
#         conn = sqlite3.connect(db_path)
#         
#         logger.debug('New log database created at: ' + db_path)
#         cur = conn.cursor()
#         
#         createRunTable(cur)
#         logger.info('Run table created')
#         
#         createTgcTable(cur)
#         logger.info('Tgc table created')
#     
#         createTbcTable(cur)
#         logger.info('Tbc table created')
#     
#         createDatTable(cur) 
#         logger.info('Dat table created')
#         
#         createEcfTable(cur)
#         logger.info('Ecf table created')
#         
#         createTcfTable(cur)
#         logger.info('Tcf table created')
# 
#         createBcTable(cur)
#         logger.info('BC Database table created')
#         
#         createTgcFilesTable(cur)
#         logger.info('Tgc Files table created')
#     
#         createTbcFilesTable(cur)
#         logger.info('Tbc Files table created')
#     
#         createBcFilesTable(cur)
#         logger.info('BC Database Files table created')
#         
#         createEcfFilesTable(cur)
#         logger.info('Ecf Files table created')
#         
#         createTcfFilesTable(cur)
#         logger.info('Tcf Files table created')
#         
#         cur.execute("pragma user_version = %s" % DATABASE_VERSION_NO)
#         
#         conn.commit()
# 
#     except OperationalError:
#         conn.rollback()
#         logger.error('Error creating log database - OperationalError')
#         logger.debug(traceback.format_exc())
#     except IOError:
#         logger.error('Error creating log database - IOError')
#         logger.debug(traceback.format_exc())
#     finally:
#         if not conn == None:
#             conn.close()
# 
# 
# def createRunTable(cur):
#     '''Create the run table
#     
#     @param cur: a cursor to an open database connection
#     '''
#     cur.execute('''CREATE TABLE RUN
#                  (ID                      INTEGER    PRIMARY KEY    NOT NULL,
#                   DATE                    TEXT                      NOT NULL,
#                   MODELLER                TEXT,
#                   RESULTS_LOCATION_2D     TEXT,
#                   RESULTS_LOCATION_1D   TEXT,
#                   EVENT_DURATION          TEXT,
#                   DESCRIPTION             TEXT,
#                   COMMENTS                TEXT,
#                   SETUP                   TEXT,
#                   ISIS_BUILD              TEXT,
#                   IEF                     TEXT,
#                   DAT                     TEXT,
#                   TUFLOW_BUILD            TEXT,
#                   TCF                     TEXT,
#                   TGC                     TEXT,
#                   TBC                     TEXT,
#                   BC_DBASE                TEXT,
#                   ECF                     TEXT,
#                   EVENT_NAME              TEXT);
#                  ''')
#     
#     
# def createTgcTable(cur):
#     '''Create the tgc table
#     
#     @param cur: a cursor to an open database connection
#     '''
#     cur.execute('''CREATE TABLE TGC
#                     (ID            INTEGER     PRIMARY KEY    NOT NULL,
#                     DATE           TEXT                       NOT NULL,
#                     TGC            TEXT,
#                     FILES          TEXT,
#                     NEW_FILES      TEXT,
#                     COMMENTS       TEXT);
#                     ''')
#     
# 
# def createTbcTable(cur):
#     '''Create the tbc table
#     
#     @param cur: a cursor to an open database connection
#     '''
#     cur.execute('''CREATE TABLE TBC
#                     (ID            INTEGER     PRIMARY KEY    NOT NULL,
#                     DATE           TEXT                       NOT NULL,
#                     TBC            TEXT,
#                     FILES          TEXT,
#                     NEW_FILES      TEXT,
#                     COMMENTS       TEXT);
#                     ''')
#     
#     
# def createDatTable(cur):
#     '''Create the dat table
#     
#     @param cur: a cursor to an open database connection
#     '''
#     cur.execute('''CREATE TABLE DAT
#                     (ID            INTEGER     PRIMARY KEY    NOT NULL,
#                     DATE           TEXT                       NOT NULL,
#                     DAT            TEXT,
#                     AMENDMENTS     TEXT,
#                     COMMENTS       TEXT);
#                     ''')
# 
# 
# def createBcTable(cur):
#     '''Create the bc_dbase table
#     
#     @param cur: a cursor to an open database connection
#     '''
#     cur.execute('''CREATE TABLE BC_DBASE
#                     (ID            INTEGER     PRIMARY KEY    NOT NULL,
#                     DATE           TEXT                       NOT NULL,
#                     BC_DBASE       TEXT,
#                     FILES          TEXT,
#                     NEW_FILES      TEXT,
#                     COMMENTS       TEXT);
#                     ''')
#     
# 
# def createEcfTable(cur):
#     '''Create the ecf table
#     
#     @param cur: a cursor to an open database connection
#     '''
#     cur.execute('''CREATE TABLE ECF
#                     (ID            INTEGER     PRIMARY KEY    NOT NULL,
#                     DATE           TEXT                       NOT NULL,
#                     ECF            TEXT,
#                     FILES          TEXT,
#                     NEW_FILES      TEXT,
#                     COMMENTS       TEXT);
#                     ''')
#     
# 
# def createTcfTable(cur):
#     '''Create the tcf table
#     
#     @param cur: a cursor to an open database connection
#     '''
#     cur.execute('''CREATE TABLE TCF
#                     (ID            INTEGER     PRIMARY KEY    NOT NULL,
#                     DATE           TEXT                       NOT NULL,
#                     TCF            TEXT,
#                     FILES          TEXT,
#                     NEW_FILES      TEXT,
#                     COMMENTS       TEXT);
#                     ''')
#     
# 
# def createTgcFilesTable(cur):
#     '''Create the tgc_files table
#     
#     @param cur: a cursor to an open database connection
#     '''
#     cur.execute('''CREATE TABLE TGC_FILES
#                     (ID            INTEGER     PRIMARY KEY    NOT NULL,
#                     TGC            TEXT,
#                     FILES          TEXT);
#                     ''')
#     
# 
# def createTbcFilesTable(cur):
#     '''Create the tbc_files table
#     
#     @param cur: a cursor to an open database connection
#     '''
#     cur.execute('''CREATE TABLE TBC_FILES
#                     (ID                INTEGER     PRIMARY KEY    NOT NULL,
#                     TBC                TEXT,
#                     FILES              TEXT);
#                     ''')
#     
#     
# def createBcFilesTable(cur):
#     '''Create the bc_dbase_files table
#     
#     @param cur: a cursor to an open database connection
#     '''
#     cur.execute('''CREATE TABLE BC_DBASE_FILES 
#                     (ID                INTEGER     PRIMARY KEY    NOT NULL,
#                     BC_DBASE           TEXT,
#                     FILES              TEXT);
#                     ''')
#     
# 
# def createEcfFilesTable(cur):
#     '''Create the ecf_files table
#     
#     @param cur: a cursor to an open database connection
#     '''
#     cur.execute('''CREATE TABLE ECF_FILES 
#                     (ID                INTEGER     PRIMARY KEY    NOT NULL,
#                     ECF                TEXT,
#                     FILES              TEXT);
#                     ''')
# 
# 
# def createTcfFilesTable(cur):
#     '''Create the tcf_files table
#     
#     @param cur: a cursor to an open database connection
#     '''
#     cur.execute('''CREATE TABLE TCF_FILES 
#                     (ID                INTEGER     PRIMARY KEY    NOT NULL,
#                     TCF                TEXT,
#                     FILES              TEXT);
#                     ''')
# 
#         
# def dropAllTables(db_path):
#     '''Drops all of the tables in the database at the given path.
#     
#     @param db_path: the path to the sqlite3 database.
#     '''
#     con = None
#     try:
#         con = sqlite3.connect(db_path)
#         con.isolation_level = None
#         try:
#             cur = con.cursor()
#             cur.execute('''DROP TABLE IF EXISTS RUN''')
#             cur.execute('''DROP TABLE IF EXISTS TGC''')
#             cur.execute('''DROP TABLE IF EXISTS TBC''')
#             cur.execute('''DROP TABLE IF EXISTS DAT''')
#             cur.execute('''DROP TABLE IF EXISTS BC_DBASE''')
#             cur.execute('''DROP TABLE IF EXISTS ECF''')
#             cur.execute('''DROP TABLE IF EXISTS TCF''')
#             cur.execute('''DROP TABLE IF EXISTS TGC_FILES''')
#             cur.execute('''DROP TABLE IF EXISTS TBC_FILES''')
#             cur.execute('''DROP TABLE IF EXISTS BC_DBASE_FILES''')
#             cur.execute('''DROP TABLE IF EXISTS ECF_FILES''')
#             cur.execute('''DROP TABLE IF EXISTS TCF_FILES''')
#             con.commit()
#         except con.Error:
#             con.rollback()
#             logger.warning('Cannot drop tables - Sql Error')
#             logger.debug(traceback.format_exc())
#     except IOError:
#         logger.error('Could not connect to database')
#         logger.debug(traceback.format_exc())
#         if not con == None:
#             con.close()
#             
# 
# # Setup for this version of the database
# run = ['ID', 'DATE', 'MODELLER', 'RESULTS_LOCATION_2D', 'RESULTS_LOCATION_1D', 
#        'EVENT_DURATION', 'DESCRIPTION', 'COMMENTS', 'SETUP', 'ISIS_BUILD', 
#        'IEF', 'DAT', 'TUFLOW_BUILD', 'TCF', 'TGC', 'TBC', 'BC_DBASE', 'ECF',
#        'EVENT_NAME'] 
# tgc = ['ID', 'DATE', 'TGC', 'FILES', 'NEW_FILES', 'COMMENTS']
# tbc = ['ID', 'DATE', 'TBC', 'FILES', 'NEW_FILES', 'COMMENTS']
# dat = ['ID', 'DATE', 'DAT', 'AMENDMENTS', 'COMMENTS']
# bc_dbase = ['ID', 'BC_DBASE', 'FILES', 'NEW_FILES', 'COMMENTS']
# ecf = ['ID', 'ECF', 'FILES', 'NEW_FILES', 'COMMENTS']
# tcf = ['ID', 'TCF', 'FILES', 'NEW_FILES', 'COMMENTS']
# tgc_files = ['ID', 'TGC', 'FILES']
# tbc_files = ['ID', 'TBC', 'FILES']
# bc_dbase_files = ['ID', 'BC_DBASE', 'FILES']
# ecf_files = ['ID', 'ECF', 'FILES']
# tcf_files = ['ID', 'TCF', 'FILES']
# 
# cur_tables = {'RUN': run, 'TGC': tgc, 'TBC': tbc, 'DAT': dat, 'ECF': ecf, 'TCF': tcf,
#               'BC_DBASE': bc_dbase, 'TGC_FILES': tgc_files, 
#               'TBC_FILES': tbc_files, 'BC_DBASE_FILES': bc_dbase_files,
#               'ECF_FILES': ecf_files, 'TCF_FILES': tcf_files
#              }
# 
# def buildTableFromName(table_type, cur):
#     '''Builds the table based on the name
#     
#     @param table_type: the type of table to build.
#     '''
#     try:
#         table_types = {'RUN': createRunTable, 'TGC': createTgcTable, 
#                         'TBC': createTbcTable, 'DAT': createDatTable, 
#                         'BC_DBASE': createBcTable, 'ECF': createEcfTable,
#                         'TCF': createTcfTable,
#                         'TGC_FILES': createTgcFilesTable, 
#                         'TBC_FILES': createTbcFilesTable, 
#                         'BC_DBASE_FILES': createBcFilesTable,
#                         'ECF_FILES': createEcfFilesTable,
#                         'TCF_FILES': createTcfFilesTable
#                        }
#         
#         table_types[table_type](cur)
#     except:
#         logger.debug(traceback.format_exc())
#         raise Exception
#     
# 
# def updateDatabaseVersion(db_path):
#     '''Update an existing version of the database to the latest version of
#     the software.
#     
#     @param db_path: the path to the sqlite3 database.
#     '''
#     version_check = checkDatabaseVersion(db_path)
#     if version_check == DATABASE_VERSION_SAME:
#         logger.error('Database version is up to date')
#         return True
#     elif version_check == DATABASE_VERSION_HIGH:
#         logger.error('Database version is newer than LogIT - please update LogIT') 
#         return False
#     
#     conn = None
#     try:
#         # Make a backup of the database
#         if os.path.exists(db_path):
#             db_dir, fname = os.path.split(db_path)
#             fname = os.path.splitext(fname)[0]
#             shutil.copyfile(db_path, os.path.join(db_dir, fname + '_backup.logdb'))
#             
#         conn = sqlite3.connect(db_path)
#         
#         # Check if the database needs updating and update it if it does.
#         success = testDatabaseCompatibility(conn, True)
#         if success:
#             cur = conn.cursor()
#             cur.execute("pragma user_version = %s" % DATABASE_VERSION_NO)
#             logger.info('Database successfully Updated - Current DB version = %s' % str(DATABASE_VERSION_NO))
# 
#     except sqlite3.Error:
#             conn.rollback()
#             logger.warning('Cannot query database - Sql Error')
#             logger.debug(traceback.format_exc())
#             return False
#     except IOError:
#         conn.rollback()
#         logger.error('Could not connect to database')
#         logger.debug(traceback.format_exc())
#         return False
#     finally:
#         if not conn == None:
#             conn.close()
#     
# 
# def testDatabaseCompatibility(conn, add_update=False):
#     '''Test the database at the given path to see if it is compatible with this
#     version of LogIT.
#     
#     @param db_path: the path to the sqlite3 database.
#     '''
#     try:
#         cur = conn.cursor()
#         for tab in cur_tables:
# 
#             # Check if the table name exists in the master table schema
#             query = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % (tab)
#             cur.execute(query)
#             
#             result = cur.fetchone()
#             if result == None or result[0] < 1:
#                 if add_update:
#                     buildTableFromName(tab, cur)
#                 else:
#                     conn.close()
#                     return False
#             
#             # Get the table information for the given table name and check
#             # that it contains all the columns we expect
#             cur.execute("pragma table_info(%s)" % tab)
#             data = cur.fetchall()
#             
#             data_names = []
#             for d in data:
#                 data_names.append(d[1])
#              
#             # Check if most recent column names are in the database table
#             update_cols = []
#             for col in cur_tables[tab]:
#                 
#                 if not col in data_names:
#                     
#                     # If we are updating store it.
#                     if add_update:
#                         update_cols.append(col)
#                     else:
#                         conn.close()
#                         return False
#             
#             # If we're updating then add the missing columns
#             if add_update and not len(update_cols) < 1:
#                 for col in update_cols:
#                     query = "alter table %s add column '%s' 'TEXT'" % (tab, col)
#                     cur.execute(query)
#         
#         if add_update:
#             conn.commit()
#                  
#     except conn.Error:
#         conn.rollback()
#         logger.warning('Cannot query database - Sql Error')
#         logger.debug(traceback.format_exc())
#         return False
# 
#     
#     return True
#     
#     
#     