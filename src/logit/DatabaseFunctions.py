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


 Module:           DatabaseFunctions.py
 Date:             16/11/2014
 Author:           Duncan Runnacles
 Since-Version:    0.1
 
 Summary:
    Contains all of the functions that communicate with the database. These
    included generic select and update queries, as well as specific actions
    and workflows required by the software.
    There is a class that should be used to do all of this, called 
    DatabaseManager. It will create a connection and provided methods for 
    reading and writing from the database.

 UPDATES:
    DR - 19/11/2014
        Added functionality to update an existing database if there are 
        changes to the way that the software uses the log database. This means
        that existing databases can be converted to the format used in new 
        releases without losing data/starting again.
    DR - 13/12/2015:
        Added DatabaseManager class and put most of the functionality into 
        that class. This is what should be used by almost all calling code now.
        The original module methods have been deleted, except for the 
        database creation, update and delete functionality.
    DR - 22/03/2016:
        Updated database version to 6.
    DR - 28/04/2016:
        Updated database to version 7. Includes RUN_STATUS, MB and LOG_DIR in
        the RUN table.

 TODO:
    The functions almost entirely use string replacement to create the
    queries. This is not good practice (although probably fairly safe from
    problems while the software is used locally). This should be changed to
    use placeholders. The problem with placeholders is that you can't use them
    for table names, so need to find a way around this.

###############################################################################
"""

import os
import sqlite3
from _sqlite3 import OperationalError, Error
import shutil
import traceback

import logging
logger = logging.getLogger(__name__)

DATABASE_VERSION_NO = 7
DATABASE_VERSION_SAME = 0
DATABASE_VERSION_LOW = 1
DATABASE_VERSION_HIGH = 2


class DatabaseManager(object):
    """Database class
    
    :note: This should not be subclassed as it relies on __del__ to close the
           connection. If you need to subclass it you will have to use the
           weakref module. Just don't do it.
    """
    
    def __init__(self, db):
        """Initiate the log by loading it.
        :raise exception: if there's an issue.
        """
        self.conn = loadLogDatabase(db)
        self.cur = self.conn.cursor()


    def __del__(self):
        """Destructor to ensure the connection gets closed.
        """
        self.conn.close()
        

    def getMaxId(self, table_name):
        """Return the highest id value in given table_name
        """
        query = 'SELECT max(id) FROM %s' % (table_name)
        self.readQuery(query)
        max_id = self.cur.fetchone()[0]
        if max_id == None:
            return 0
        else:
            return max_id


    def deleteRow(self, table_name, row_id):
        """Delete the row at the provided index in the provided table_name
        """
        query = "delete from %s where ID='%s'" % (table_name, row_id)
        self.writeQuery(query)
        
        
    def deleteClause(self, table_name, col_name, entry):
        """Deletes rows from the database that meet the given query.
        All rows where col_name == entry will be deleted.
        :param entry: the entry to test.
        """
        query = "delete from %s where %s='%s'" % (table_name, col_name, entry)
        self.writeQuery(query)
    
    
    def insertQueue(self, queue_obj):
        """Inserts all of the items in the DbQueue object into the database.
        :param queue_obj: the DbQueue object that contains all the query data.
        """
        while not queue_obj.isEmpty():
            entry = queue_obj.dequeue()
            table_name = entry[0]
            row_data = entry[1]
            columns = ', '.join(row_data.keys())
            placeholders = ", ".join('?' * len(row_data))
            query = 'insert into ' + table_name + ' ({}) values ({})'.format(columns, placeholders)
            self.writeQuery(query, row_data, False)
        
        self.conn.commit()
        

    def insertValues(self, table_name, row_data):   
        """Inserts a dictionary of values into the given table_name
        :param table_name: the name of the table to update.
        :param row_data: a dictionary containing keys that match the schema of
               the table and values to insert.
        """
        
        columns = ', '.join(row_data.keys())
        placeholders = ", ".join('?' * len(row_data))
        query = 'insert into ' + table_name + ' ({}) values ({})'.format(columns, placeholders)
        self.writeQuery(query, row_data)


    def updateRowValue(self, table_name, column, value, id):
        """Updates the values of a row in the given table.
        :param table_name: the name of the table to update.
        :param column: name of the column to update.
        :param value: the value to insert.
        :param id: the row index to insert the value into.
        """
        query = "update %s set %s='%s' where ID=%s" % (table_name, column, value, id)
        self.writeQuery(query)
    
    
    def updateRow(self, table_name, column, row_data, id):
        """Updates all of the values in the given columns according to row index.
        """
        columns = ' = ?, '.join(row_data.keys())
        columns += ' = ?'
        query = "update " + table_name + " set " + columns + " where ID='" + id + "'"
        self.writeQuery(query, row_data)


    def findEntry(self, table_name, col_name, entry, column_only=False, 
                                                    return_rows=False):
        """Searches for a specific entry in the database.
        :param table_name: the name of the table to search.
        :param col_name: the name of the column to search.
        :param entry: the value to search for.
        :param column_only=True: if any returned values should only be from the
               given col_name.
        :param return_rows=False: if True a tuple will be return containing:
              - True.
              - Number of rows found.
              - The values in the rows containing entry.
              If False then only a boolean will be returned stating whether
              the entry exists in the column or not.
        :return: Boolean flag for entry exists or tuple (see above) if 
                 return_rows is set to True.
        """
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
    
    
    def findMultipleEntry(self, table_name, entry_data, return_rows=False, 
                                                                AND=True):
        """Searches for entries in the given table_name.
        These must meet the AND/OR criteria provided.
        :param table_name: the name of the table to search.
        :param entry_data: dict containing the {column: value} pairs.
        :param return_rows=False: if True a tuple will be return containing:
              - True.
              - Number of rows found.
              - The values in the rows containing entry.
              If False then only a boolean will be returned stating whether
              the entry exists in the column or not.
        :param AND=True: If equality should be check with AND. Set to False
               if OR should be used instead.
        :return: Boolean flag for entry exists or tuple (see above) if 
                 return_rows is set to True.
        """
        if AND:
            columns = '=? AND '.join(entry_data.keys())
        else:
            columns = '=? OR '.join(entry_data.keys())
        columns += '=?'
        query = "SELECT * FROM " + table_name + " WHERE " + columns
        
        self.readQuery(query, entry_data)
        result = self._getEntriesFromCursor()
        if return_rows:
            return result
        else:
            return result[0]
    

    def findAll(self, table_name, col_name=False, return_rows=False):
        """Returns all values in the given table or column.
        :param table_name: the table to return values from.
        :param col_name=False: the column to return values from if set to True.
               If set to False (default) all values in the table will be
               returned.
        :param return_rows=False: if True a tuple will be return containing:
              - True.
              - Number of rows found.
              - The values in the rows containing entry.
              If False then only a boolean will be returned stating whether
              the entry exists in the column or not.
        :return: Boolean flag for entry exists or tuple (see above) if 
                 return_rows is set to True.
        """
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
        

    def checkVersion(self):
        """Checks the version of the loaded database against the module value.
        :return: a constant representing the state of the database loaded into
                 this class:
                 - DATABASE_VERSION_SAME = 0: Same as currently used by LogIT
                 - DATABASE_VERSION_HIGH = 1: Newer than currently used.
                 - DATABASE_VERSION_LOW = 2: Older than currently used.
        """
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
        
    
    def getTableNames(self):
        """Get a list of all of the table names in the database.
        :return: list containing the table names.
        """
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        self.cur.execute(query)
        result = self._getEntriesFromCursor()
        return result[2]
        
    
    def insertBlob(self, table_name, col_name, pdata, row_id):
        """Inserts data into a blob entry.
        """
        query = "update " + table_name + " set " + col_name + "=:blobData where id = " + str(row_id)
        self.cur.execute (query, [sqlite3.Binary(pdata)],) 
        self.conn.commit()
    
    
#     def selectBlob(self):
#         """
#         """
#         self.cur.execute("select data from table limit 1")
#         for row in curr:
#             data = cPickle.loads(str(row['data']))
    

    def readQuery(self, query, row_data=None):
        """Used to read in a query from the database.
        This is only used to read from the database and doesn't commit
        anything. If that is needed use writeQuery function.
        :param query: the sql query to evaluate.
        :return: self.cur containing the output of the query.
        """
        try:
            if row_data == None:
                self.cur.execute(query)
            else:
                self.cur.execute(query, row_data.values())
            return self.cur
        except self.conn.Error:
            logger.error('Problem querying database')
            logger.debug(traceback.format_exc())
            raise ValueError


    def writeQuery(self, query, row_data=None, commit=True):
        """Used to write a query to the database.
        Will commit once the query has been evaluated.
        :param query: the query to evaluate.
        :param row_data=None: if additional data is needed to evaluate the
              query it should be included in this. It should be a dictionary
              of values and the query should contain column names and 
              placeholders for converting the values.
        :return: self.cur containing the output of the query.
        :raise ValueError: if there's a problem entering the data into the
               database.
        """
        try:
            if row_data == None:
                self.cur.execute(query)
            else:
                self.cur.execute(query, row_data.values())

            if commit:
                self.conn.commit()
            return self.cur

        except self.conn.Error:
            self.conn.rollback()
            logger.debug(traceback.format_exc())
            logger.error('SQL exception when trying to perform\n' +
                         'sql: %s' % (query))
            raise ValueError
            
        
    def _getEntriesFromCursor(self):
        """Converts the outputs of the cursor query into a list.
        Call self._convertRowToDictionary to do this.
        :return: a tuple containing:
                 - Boolean flag stating if any results were found.
                 - integer count of number of results.
                 - A list containing dictionaries for each row. 
        """
        found_rows = []
        result = self.cur.fetchall()
        if not result == None:
            
            count = len(result)
            if count > 0:
                # Convert the row factory to a dictionary of the row variables
                for row in result:
                    found_rows.append(self._convertRowToDictionary(row))
                    
                # Return here if we found stuff and return_rows is True
                return (True, count, found_rows)
        
        return (False, 0, [])


    def _convertRowToDictionary(self, row):
        """Converts a sqlite3 row_factory into a dictionary
        
        :param row: the row_factory object from sqlite3 cursor.
        :return: dictionary containing the values in the given row with keys
                 set as the column names.
        """
        d = {}
        for idx, col in enumerate(self.cur.description):
            d[col[0]] = row[idx]
        return d
    
    

"""
##############################################################################
    Below here is all of the module wide functionality for doing the creation,
    updating, deleting, etc of the database.
    
    It's done quite rarely so it doesn't need to be in class functionality I
    don't think. It will just make the class messy and hard to follow.

##############################################################################
"""

def loadLogDatabase(db_path):
    """Load a log database from file
    
    :param db_path: path to the sqlite database to load
    """
    con = False
    
    try:
        con = sqlite3.connect(db_path)
        logger.debug('Loaded log database at: ' + db_path)
    except:
        logger.error('Could not load log database at: ' + db_path)
        logger.debug(traceback.format_exc())
    
    return con


def createNewLogDatabase(db_path):
    """Creates a new SqLite database and sets up the tables for adding the
    log entries into.
    
    :param db_path: path to use to create the database.
    """
    conn = None
    
    if os.path.exists(db_path):
        logger.warning('Database already exists - Resetting to new')
        dropAllTables(db_path)
        
    try:
        conn = sqlite3.connect(db_path)
        
        logger.debug('New log database created at: ' + db_path)
        
        logger.info('Start building database ...')
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
        
        createRunIdTable(cur)
        logger.info('Run id table created')
        
        cur.execute("pragma user_version = %s" % DATABASE_VERSION_NO)
        
        conn.commit()
        logger.info('Build database complete.')

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
    """Create the run table
    
    :param cur: a cursor to an open database connection
    """
    cur.execute("""CREATE TABLE RUN
                 (ID                      INTEGER    PRIMARY KEY    NOT NULL,
                  DATE                    TEXT                      NOT NULL,
                  MODELLER                TEXT,
                  RESULTS_LOCATION_2D     TEXT,
                  RESULTS_LOCATION_1D     TEXT,
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
                  EVENT_NAME              TEXT,
                  RUN_OPTIONS             TEXT,
                  TCF_DIR                 TEXT,
                  IEF_DIR                 TEXT,
                  LOG_DIR                 TEXT,
                  MB                      TEXT,
                  RUN_STATUS              TEXT);
                 """)
    

def createRunIdTable(cur):
    """Create the run table
    
    :param cur: a cursor to an open database connection
    """
    cur.execute("""CREATE TABLE RUN_ID
                 (ID            INTEGER    PRIMARY KEY       NOT NULL,
                  RUN_ID        INTEGER,
                  FILE          TEXT,
                  TYPE          TEXT);
                 """)
    
    
def createTgcTable(cur):
    """Create the tgc table
    
    :param cur: a cursor to an open database connection
    """
    cur.execute("""CREATE TABLE TGC
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    DATE           TEXT                       NOT NULL,
                    TGC            TEXT,
                    FILES          TEXT,
                    NEW_FILES      TEXT,
                    COMMENTS       TEXT);
                    """)
    

def createTbcTable(cur):
    """Create the tbc table
    
    :param cur: a cursor to an open database connection
    """
    cur.execute("""CREATE TABLE TBC
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    DATE           TEXT                       NOT NULL,
                    TBC            TEXT,
                    FILES          TEXT,
                    NEW_FILES      TEXT,
                    COMMENTS       TEXT);
                    """)
    
    
def createDatTable(cur):
    """Create the dat table
    
    :param cur: a cursor to an open database connection
    """
    cur.execute("""CREATE TABLE DAT
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    DATE           TEXT                       NOT NULL,
                    DAT            TEXT,
                    AMENDMENTS     TEXT,
                    COMMENTS       TEXT);
                    """)


def createBcTable(cur):
    """Create the bc_dbase table
    
    :param cur: a cursor to an open database connection
    """
    cur.execute("""CREATE TABLE BC_DBASE
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    DATE           TEXT                       NOT NULL,
                    BC_DBASE       TEXT,
                    FILES          TEXT,
                    NEW_FILES      TEXT,
                    COMMENTS       TEXT);
                    """)
    

def createEcfTable(cur):
    """Create the ecf table
    
    :param cur: a cursor to an open database connection
    """
    cur.execute("""CREATE TABLE ECF
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    DATE           TEXT                       NOT NULL,
                    ECF            TEXT,
                    FILES          TEXT,
                    NEW_FILES      TEXT,
                    COMMENTS       TEXT);
                    """)
    

def createTcfTable(cur):
    """Create the tcf table
    
    :param cur: a cursor to an open database connection
    """
    cur.execute("""CREATE TABLE TCF
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    DATE           TEXT                       NOT NULL,
                    TCF            TEXT,
                    FILES          TEXT,
                    NEW_FILES      TEXT,
                    COMMENTS       TEXT);
                    """)
    

def createTgcFilesTable(cur):
    """Create the tgc_files table
    
    :param cur: a cursor to an open database connection
    """
    cur.execute("""CREATE TABLE TGC_FILES
                    (ID            INTEGER     PRIMARY KEY    NOT NULL,
                    TGC            TEXT,
                    FILES          TEXT);
                    """)
    

def createTbcFilesTable(cur):
    """Create the tbc_files table
    
    :param cur: a cursor to an open database connection
    """
    cur.execute("""CREATE TABLE TBC_FILES
                    (ID                INTEGER     PRIMARY KEY    NOT NULL,
                    TBC                TEXT,
                    FILES              TEXT);
                    """)
    
    
def createBcFilesTable(cur):
    """Create the bc_dbase_files table
    
    :param cur: a cursor to an open database connection
    """
    cur.execute("""CREATE TABLE BC_DBASE_FILES 
                    (ID                INTEGER     PRIMARY KEY    NOT NULL,
                    BC_DBASE           TEXT,
                    FILES              TEXT);
                    """)
    

def createEcfFilesTable(cur):
    """Create the ecf_files table
    
    :param cur: a cursor to an open database connection
    """
    cur.execute("""CREATE TABLE ECF_FILES 
                    (ID                INTEGER     PRIMARY KEY    NOT NULL,
                    ECF                TEXT,
                    FILES              TEXT);
                    """)


def createTcfFilesTable(cur):
    """Create the tcf_files table
    
    :param cur: a cursor to an open database connection
    """
    cur.execute("""CREATE TABLE TCF_FILES 
                    (ID                INTEGER     PRIMARY KEY    NOT NULL,
                    TCF                TEXT,
                    FILES              TEXT);
                    """)

        
def dropAllTables(db_path):
    """Drops all of the tables in the database at the given path.
    
    :param db_path: the path to the sqlite3 database.
    """
    con = None
    try:
        con = sqlite3.connect(db_path)
        con.isolation_level = None
        try:
            cur = con.cursor()
            cur.execute("""DROP TABLE IF EXISTS RUN""")
            cur.execute("""DROP TABLE IF EXISTS TGC""")
            cur.execute("""DROP TABLE IF EXISTS TBC""")
            cur.execute("""DROP TABLE IF EXISTS DAT""")
            cur.execute("""DROP TABLE IF EXISTS BC_DBASE""")
            cur.execute("""DROP TABLE IF EXISTS ECF""")
            cur.execute("""DROP TABLE IF EXISTS TCF""")
            cur.execute("""DROP TABLE IF EXISTS TGC_FILES""")
            cur.execute("""DROP TABLE IF EXISTS TBC_FILES""")
            cur.execute("""DROP TABLE IF EXISTS BC_DBASE_FILES""")
            cur.execute("""DROP TABLE IF EXISTS ECF_FILES""")
            cur.execute("""DROP TABLE IF EXISTS TCF_FILES""")
            cur.execute("""DROP TABLE IF EXISTS RUN_ID""")
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
       'EVENT_NAME', 'RUN_OPTIONS', 'TCF_DIR', 'IEF_DIR', 'LOG_DIR', 'MB',
       'RUN_STATUS'] 
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
run_id = ['ID', 'RUN_ID', 'FILE']

cur_tables = {'RUN': run, 'TGC': tgc, 'TBC': tbc, 'DAT': dat, 'ECF': ecf, 'TCF': tcf,
              'BC_DBASE': bc_dbase, 'TGC_FILES': tgc_files, 
              'TBC_FILES': tbc_files, 'BC_DBASE_FILES': bc_dbase_files,
              'ECF_FILES': ecf_files, 'TCF_FILES': tcf_files,
              'RUN_ID': run_id
              }

def buildTableFromName(table_type, cur):
    """Builds the table based on the name
    
    :param table_type: the type of table to build.
    """
    try:
        table_types = {'RUN': createRunTable, 'TGC': createTgcTable, 
                        'TBC': createTbcTable, 'DAT': createDatTable, 
                        'BC_DBASE': createBcTable, 'ECF': createEcfTable,
                        'TCF': createTcfTable,
                        'TGC_FILES': createTgcFilesTable, 
                        'TBC_FILES': createTbcFilesTable, 
                        'BC_DBASE_FILES': createBcFilesTable,
                        'ECF_FILES': createEcfFilesTable,
                        'TCF_FILES': createTcfFilesTable,
                        'RUN_ID': createRunIdTable,
                       }
        
        table_types[table_type](cur)
    except:
        logger.debug(traceback.format_exc())
        raise Exception
    

def updateDatabaseVersion(db_path):
    """Update an existing version of the database to the latest version of
    the software.
    
    :param db_path: the path to the sqlite3 database.
    """
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
        try:
            if os.path.exists(db_path):
                db_dir, fname = os.path.split(db_path)
                fname = os.path.splitext(fname)[0]
                shutil.copyfile(db_path, os.path.join(db_dir, fname + '_backup.logdb'))
        except:
            logger.error('Unable to create backup of database - STOPPING NOW.')
            return False
            
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
    """Test the database at the given path to see if it is compatible with this
    version of LogIT.
    
    :param db_path: the path to the sqlite3 database.
    """
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




def checkDatabaseVersion(db_path):
    """Check the database version number to make sure it is the same as the
    current version of the software. If it's not we return False because the
    user needs to either update the database settings or use an older version.
    
    :param db_path: path to an existing database.
    :param version_no: the database version used by this version of LogIT.
    :raise IOError: if db_path does not point to a database or it is not a
           LogIT database file.
    """
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
     
