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


 Module:          dbmigrations.py 
 Date:            27/10/2016
 Author:          Duncan Runnacles
 Since-Version:   1.2.0
 
 Summary:
     Logic for updating the database to a new version. The updates undertaken
     are based on the existing version of the database. This means, hopefully,
     that and version of the DB (since 1.0) can be updated to any later version
     by incrementally applying the updates.

 UPDATES:
    

 TODO:
    

###############################################################################
"""
import logging
logger = logging.getLogger(__name__)

import os
import copy

from peewee import *
from playhouse.migrate import *

import peeweeviews as pv
import peeweemodels as pm


migrator = SqliteMigrator(pm.logit_db)

def update21():
    """Run the updates for database version 21.
    
    - Adds the Ied, Run_Ied and Run_SubFile tables.
    - Adds the initial_conditions field to the Run table.
    - Populates the Run_Subfile table with values.
    """
    logger.info("\n*** Running migration 'update21' ***\n")

    logger.info("Creating Ied, Run_Ied and Run_SubFile tables...")
    pm.createTable(pm.Ied)
    pm.createTable(pm.Run_Ied)
    pm.createTable(pm.Run_SubFile)
    
    logger.info("Adding initial_conditions field to Run table...")
    icfield = CharField(default='')
    migrate(migrator.add_column("Run", "initial_conditions", icfield))
    
    logger.info("Creating entries for Run_Subfile table...")
    
    saved_data = []
    for r in pm.Run.select():
        query = (pm.ModelFile_SubFile
                 .select(pm.ModelFile_SubFile, pm.ModelFile, pm.SubFile, pm.Run_ModelFile)
                 .join(pm.SubFile)
                 .switch(pm.ModelFile_SubFile)
                 .join(pm.ModelFile)
                 .join(pm.Run_ModelFile)
                 )
        query = query.where(pm.Run_ModelFile.run_id == r.id)
        
        for q in query:
            saved_data.append({'run_id': r.id, 'sub_file_id': q.sub_file.name})
    
    with pm.logit_db.atomic():
        for data_dict in saved_data:
            pm.Run_SubFile.create(**data_dict)

    
def getRequiredUpdates(db_path):
    """Returns the number of update steps required.
    
    Args:
        db_path(str): the path to the database to update.
    
    Return:
        list - containing functions that should be called, in order, to 
            update the database to the latest version.
    """
    current_version = pm.DATABASE_VERSION_NO
    status, db_version = pv.checkDatabaseVersion(db_path, True)
    
    # If database is from an newer version of logit or the same then there's
    # nothing to be done here
    if status == pm.DATABASE_VERSION_HIGH or status == pm.DATABASE_VERSION_SAME or status == pm.DATABASE_VERSION_OLD:
        return status
    
    required = []
    if db_version < 21:
        required.append(update21)
    
    return required
    
    
    
    
    
    
    
    
    
    