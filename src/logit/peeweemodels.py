"""
###############################################################################
    
 Name: LogIT (Logger for Isis and Tuflow) 
 Author: Duncan Runnacles
 Copyright: (C) 2016 Duncan Runnacles
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


 Module:          peeweemodels.py 
 Date:            09/08/2016
 Author:          Duncan Runnacles
 Since-Version:   1.0.0
 
 Summary:
     All of the peewee database models.

 UPDATES:
    

 TODO:
    

###############################################################################
"""
import  sqlite3
import traceback

import logging
logger = logging.getLogger(__name__)

from peewee import *
from datetime import date as d
from datetime import datetime as dt

logit_db = SqliteDatabase(None)
""" Database object """

DATABASE_VERSION_NO = 21
""" Database version number """

NEW_DB_START = 20
""" Version number that new db setup was introduced.

This is used to check whether the old database is compatible with this one.
"""

'''
 Static variables for returning database version info
'''
DATABASE_VERSION_SAME = 0
DATABASE_VERSION_LOW = 1
DATABASE_VERSION_HIGH = 2
DATABASE_VERSION_OLD = 3


'''
 Database models
'''
class LogitModel(Model):
    class Meta:
        database = logit_db
        

class Dat(LogitModel):
    name = CharField(primary_key=True, index=True)
    amendments = TextField(default='')
    comments = TextField(default='')
    timestamp = DateTimeField(default=dt.now)
    

class Run(LogitModel):
    dat = ForeignKeyField(Dat, null=True)
    run_hash = CharField(unique=True, index=True)
    setup = TextField(default='')
    comments = TextField(default='')
    ief = CharField(default='')
    tcf = CharField(default='')
    initial_conditions = CharField(default='')
    isis_results = CharField(default='')
    tuflow_results = CharField(default='')
    estry_results = CharField(default='')
    event_duration = FloatField(default=-9999.0)
    run_status = CharField(default='')
    mb = FloatField(default=-9999.0)
    modeller = CharField(default='')
    isis_version = CharField(default='')
    tuflow_version = CharField(default='')
    event_name = CharField(default='')
    ief_dir = CharField(default='')
    tcf_dir = CharField(default='')
    log_dir = CharField(default='')
    run_options = CharField(default='')
    timestamp = DateTimeField(default=dt.now)
    

class ModelFile(LogitModel):
    name = CharField(primary_key=True, index=True)
    model_type = CharField()
    comments = TextField(default='')
    timestamp = DateTimeField(default=dt.now)


class SubFile(LogitModel):
    name = CharField(primary_key=True, index=True)
    timestamp = DateTimeField(default=dt.now)
    
    
class Ied(LogitModel):
    name = CharField(primary_key=True, index=True)
    ref = CharField(default='')
    amendments = TextField(default='')
    comments = TextField(default='')
    timestamp = DateTimeField(default=dt.now)

    
class ModelFile_SubFile(LogitModel):
    model_file = ForeignKeyField(ModelFile, index=True)
    sub_file = ForeignKeyField(SubFile, index=True)
    new_file = BooleanField(default=False)
    timestamp = DateTimeField(default=dt.now)

        
class Run_ModelFile(LogitModel):
    run = ForeignKeyField(Run, index=True)
    model_file = ForeignKeyField(ModelFile, index=True)
    new_file = BooleanField(default=False)
    timestamp = DateTimeField(default=dt.now)


class Run_SubFile(LogitModel):
    run = ForeignKeyField(Run, index=True)
    sub_file = ForeignKeyField(SubFile, index=True)
    timestamp = DateTimeField(default=dt.now)


class Run_Ied(LogitModel):
    run = ForeignKeyField(Run, index=True)
    ied = ForeignKeyField(Ied, index=True)
    timestamp = DateTimeField(default=dt.now)



'''
 Functions
'''
def getAllTables():
    return [Run, Dat, Ied, ModelFile, SubFile, Run_ModelFile, ModelFile_SubFile, Run_SubFile, Run_Ied]

def createTable(table, connect_db=True):
    """Create a single table."""
    logit_db.connect()
    logit_db.create_tables([table])
    logit_db.close()


def createTableList(tables, connect_db=True):
    """Create all tables."""
    logit_db.connect()
    logit_db.create_tables(tables)
    logit_db.close()
    

# def updatePragmaUserVersion(db_path):
#     """Sets the pragma version tag to current database value"""
#     
#     conn = None
#     success = True
#     try:
#         conn = sqlite3.connect(dbpath)
#         cur = conn.cursor() 
#         cur.execute("pragma user_version = %s" % DATABASE_VERSION_NO)
#         logger.info("Database user_version updated to: %s" % (DATABASE_VERSION_NO))


def connectDB():
    try:
        logit_db.connect(reuse_if_open=True)
    except InterfaceError:
        logger.warning('Cannot connect to Database, it has not been initialised')
        raise
    
def disconnectDB():
    logit_db.close()


def createNewDb(db_path):
    """Create a new sqlite database and setup version number."""
    
    conn = None
    success = True
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("pragma user_version = %s" % DATABASE_VERSION_NO)
        logger.info('Database successfully Updated - Current DB version = %s' % str(DATABASE_VERSION_NO))

    except sqlite3.Error:
            conn.rollback()
            logger.warning('Cannot query database - Sql Error')
            logger.debug(traceback.format_exc())
            success = False
    except OSError:
        conn.rollback()
        logger.error('Could not connect to database')
        logger.debug(traceback.format_exc())
        success = False
    finally:
        if conn is not None:
            conn.close()
   
    print(success)
    if success != True:
        return False
    
    try:
        logit_db.init(db_path)
    except Exception as err:
        logger.exception(err)
        return False
     
    return True
        
        