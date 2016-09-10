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


 Module:          peeweeviews.py 
 Date:            09/08/2016
 Author:          Duncan Runnacles
 Since-Version:   1.0.0
 
 Summary:
     All of the model view for interacting with the peewee database models.

 UPDATES:
    

 TODO:
    

###############################################################################
"""

import logging
logger = logging.getLogger(__name__)

import os
import copy
import traceback
import sqlite3

from peewee import *
from playhouse import shortcuts
import peeweemodels as pm


TABLE_CHOICE = ['', 'DAT', 'TCF', 'ECF', 'TGC', 'TBC', 'BC_DBASE', 'TEF', 'TRD']
QUERY_CHOICE = ['', 'TCF', 'ECF', 'TGC', 'TBC', 'BC_DBASE', 'TEF', 'TRD']
DAT_FIELDS = {'name': pm.Dat.name, 'amendments': pm.Dat.amendments, 'comments': pm.Dat.comments}
MODEL_FIELDS = {'name': pm.ModelFile.name, 'model_type': pm.ModelFile.model_type, 'comments': pm.ModelFile.comments, 'files': None}
FILE_FIELDS = ['name']

'''
 Getters for the different table fields.
 These are here to try and keep referenced to fields etc in one place.
'''
def getTableChoice():
    return copy.deepcopy(TABLE_CHOICE)

def getDatFields():
    return DAT_FIELDS.keys()

def getModelFields(plus_files=False):
    if plus_files:
        return MODEL_FIELDS.keys() + ['files']
    else:
        return MODEL_FIELDS.keys()


def addDat(dat):
    """Add a new record to the Dat table.
    
    Args:
        dat(dict): containing the records to update.
    
    Return:
        peewee.Model - the newly created Dat record.
    """
    pm.logit_db.connect()
    d, crtd = pm.Dat.create_or_get(name=dat['NAME'], amendments=dat['AMENDMENTS'], comments=dat['COMMENTS'])
    pm.logit_db.close()
    return d


def addRun(run, run_hash, ief_dir, tcf_dir, dat=None):
    """Add a new record to the Run table.
    
    Args:
        run(dict): containing the values to update the Run table with.
        run_hash(str): unique hash code for this run.
        ief_dir(str): the ief directory string - can be ''.
        tcf_dir(str): the tcf directory string - can be ''.
        dat=None(peewee.Model): the Dat record to reference against the 
            Run.dat foreign key.
    
    Return:
        peewee.Model - the newly created Run record.
    """
    pm.logit_db.connect()
    # DEBUG
    if dat is not None:
        r = pm.Run(dat=dat, run_hash=run_hash, setup=run['SETUP'], modeller=run['MODELLER'],
                ief=run['IEF'], tcf=run['TCF'], isis_results=run['ISIS_RESULTS'], tuflow_results=run['TUFLOW_RESULTS'],
                estry_results=run['ESTRY_RESULTS'], event_duration=run['EVENT_DURATION'],
                comments=run['COMMENTS'], isis_version=run['ISIS_BUILD'], tuflow_version=run['TUFLOW_BUILD'],
                event_name=run['EVENT_NAME'], ief_dir=ief_dir, tcf_dir=tcf_dir,
                log_dir=run['LOG_DIR'], run_options=run['RUN_OPTIONS'], 
                run_status=run['RUN_STATUS'], mb=run['MB'])
    else:
        r = pm.Run(run_hash=run_hash, setup=run['SETUP'], modeller=run['MODELLER'],
                ief=run['IEF'], tcf=run['TCF'], isis_results=run['ISIS_RESULTS'], tuflow_results=run['TUFLOW_RESULTS'],
                estry_results=run['ESTRY_RESULTS'], event_duration=run['EVENT_DURATION'],
                comments=run['COMMENTS'], isis_version=run['ISIS_BUILD'], tuflow_version=run['TUFLOW_BUILD'],
                event_name=run['EVENT_NAME'], ief_dir=ief_dir, tcf_dir=tcf_dir,
                log_dir=run['LOG_DIR'], run_options=run['RUN_OPTIONS'],
                run_status=run['RUN_STATUS'], mb=run['MB'])
    r.save()
    pm.logit_db.close()
    return r

def addAllModel(mfiles, run):
    """Add all of the provided models to the database.
    
    Updates the ModelFile, SubFile and ModelFile_SubFile tables with the new
    records.
    
    ModelFile table is only updated when the ModelFile.name does not already
    contain mfiles['NAME'], but Run_ModelFile will be.
    
    SubFile table is only updated when the filename is not in SubFile.name,
    but the ModelFile_SubFile table will be.
    
    The checking of existing records is done in a first pass and a set of lists
    if populated with the record data to update. Once this is completed these
    lists are looped seperately 'with atomic' to try and speed things up.
    
    TODO:
        A bit slow and probably not very efficient. I don't think this will
            scale well when the database gets even slightly big. Maybe consider
            whether just adding it all on and then deleting any duplicates might
            be quicker than check files exist on loop?
    
    Args:
        mfiles(list): containing dictionaries with values to update with.
        run(int): the Run.id to use as foreign key in the Run_ModelFile table.
    """    
    model_datasource = []
    files_datasource = []
    mf_datasource = []
    rm_datasource = []
    
    found_models = []
    found_files = []
    found_modelfiles = []
    found_runmodels = []
    for m in mfiles:
        if not m['NAME'] in found_models and not modelExists(m['NAME']): 
            model_datasource.append({'name': m['NAME'], 'model_type': m['TYPE'], 'comments': m['COMMENTS']})
            found_models.append(m['NAME'])
            rm_datasource.append({'run': run, 'model_file': m['NAME'], 'new_file': True})
        else:
            rm_datasource.append({'run': run, 'model_file': m['NAME'], 'new_file': False})
            continue
        
        for f in m['FILES']:
            first_time = False
            if subFileIsNew(m['TYPE'], f):
                first_time = True
            if not f in found_files and not subfileExists(f):
                files_datasource.append({'name': f})
                found_files.append(f)
            if not ((m['NAME'] + f) in found_modelfiles) and  not modelSubfileExists(m['NAME'], f):
                mf_datasource.append({'model_file': m['NAME'], 'sub_file': f, 'new_file': first_time})
                found_modelfiles.append(m['NAME'] + f)
            
        
    with pm.logit_db.atomic():
        for data_dict in model_datasource:
            pm.ModelFile.create(**data_dict)
        for data_dict in files_datasource:
            pm.SubFile.create(**data_dict)
        for data_dict in mf_datasource:
            pm.ModelFile_SubFile.create(**data_dict)
        for data_dict in rm_datasource:
            pm.Run_ModelFile.create(**data_dict)
            

def subFileIsNew(mtype, fname):
    """Test if a SubFile is new.
    
    Checks the ModelFile_SubFile table to see if there are any records 
    containing both the ModelFile.model_type and SubFile.name values. If there
    are it will return False.
    
    Args:
        mtype(str): ModelFile.model_type to query.
        fname(str): SubFile.name to query.
    
    Return:
        True if new or False if not.
    """
    query = (pm.ModelFile_SubFile
            .select(pm.ModelFile_SubFile, pm.ModelFile, pm.SubFile)
            .join(pm.SubFile)
            .switch(pm.ModelFile_SubFile)
            .join(pm.ModelFile)
            .where((pm.ModelFile.model_type == mtype) & (pm.SubFile.name == fname))
            )
    if query.exists():
        return False
    else:
        return True


'''
Start of record exist functions for all tables.
'''
def runExists(name):
    query = pm.Run.select().where(pm.Run.run_hash == name)
    if query.exists():
        return True
    else:
        return False

def datExists(name):
    query = pm.Dat.select().where(pm.Dat.name == name)
    if query.exists():
        return True
    else:
        return False

def allModelsExists(names):
    
    query = pm.ModelFile.select().where(pm.ModelFile.name == name)
    if query.exists():
        return True
    else:
        return False

def modelExists(name):
    query = pm.ModelFile.select().where(pm.ModelFile.name == name)
    if query.exists():
        return True
    else:
        return False

        
def subfileExists(name):
    query = pm.SubFile.select().where(pm.SubFile.name == name)
    if query.exists():
        return True
    else:
        return False

def runModelFileExists(r, m):
    query = pm.Run_ModelFile.select().where((pm.Run_ModelFile.run_file_id == r) & (pm.Run_ModelFile.model_file_id == m))
    if query.exists():
        return True
    else:
        return False

def modelSubfileExists(m, s):
    query = pm.ModelFile_SubFile.select().where((pm.ModelFile_SubFile.model_file_id == m) & (pm.ModelFile_SubFile.sub_file_id == s))
    if query.exists():
        return True
    else:
        return False
'''
End of record exist functions for all tables.
'''


def getRunRow(run_id):
    """Return the Run record associated with the given Run.id.
    
    Args:
        run_id(int): the Run.id to query against.
    
    Return:
        dict - containing {field: value} for the record.
    """    
    pm.logit_db.connect()
    query = pm.Run.get(pm.Run.id == run_id)
    run = shortcuts.model_to_dict(query, recurse=False)
    pm.logit_db.close()
    return run


def deleteRunRow(run_id, delete_recursive=False):
    """Delete a record in the Run table.
    
    Delete's a Run record. If delete_recursive it will delete any associated
    records in the other tables. This is done in a (semi)intelligent way:
    All ModelFile records associated with this run_id in the Run_ModelFile
    table will be deleted IF they are not refernced by another Run.id in the
    Run_ModelFile table. This is also True of the Dat reference.
    
    TODO:
        I don't think this is very well written at the moment and is definitely
            quite slow.
    
    Args:
        run_id(int): the Run.id value to query against.
        delete_recursive=False(bool): if True will delete any foreign key
            associations and remove any associated Dat and ModelFile records.
    """
    pm.logit_db.connect()
    
    mdel = []
    dat = None
    try:
        r = pm.Run.get(pm.Run.id == run_id)
    except Exception, err:
        logger.warning('Could not find entry for run_id = %s' % run_id)
        logger.exception(err)

    if delete_recursive:
        
        # If we have a dat in this run
        if r.dat is not None:
            run_d = pm.Dat.get(name=r.dat)
            
            # If that dat isn't referenced in any other runs
            if pm.Run.select().filter(dat=run_d.name).count() < 2:
                dat = run_d.name

        # Get all modelfile's and a count of how many times there are referenced
        mq = (pm.Run_ModelFile
                .select(pm.Run_ModelFile.run_id, pm.Run_ModelFile.model_file_id, fn.Count(pm.Run_ModelFile.model_file_id).alias('count'))
                .group_by(pm.Run_ModelFile.model_file_id)
             )
        # If they are only referenced by this run add to the delete list
        # TODO: VERY slow. Must try harder
        for m in mq:
            if m.count < 2 and m.run_id == run_id:
                mdel.append(m.model_file_id)

    r.delete_instance(recursive=delete_recursive)
    
    with pm.logit_db.atomic():
        if dat is not None: 
            deleteDatRow(dat)
        for m in mdel:
            deleteModelRow(m, remove_orphans=False)

    pm.logit_db.close()
    

def deleteDatRow(dat_name):
    """Delete a record in the Dat table.
    
    Deletes the specified Dat record.
    
    Args:
        dat_name(str): the Dat.name to query against.
    """
    pm.logit_db.connect()
    d = pm.Dat.get(pm.Dat.name == dat_name)
    d.delete_instance()
    pm.logit_db.close()
    

def deleteModelRow(model_name, remove_orphans=True):
    """Delete a record in the ModelFile table.
    
    Deletes the specified ModelFile record and any foreign key associations.
    
    Args:
        model_name(str): the ModelFile.name to query against.
        remove_orphans=True(bool): if True will call deleteOrphanFiles after.
    """
    pm.logit_db.connect()
    m = pm.ModelFile.get(pm.ModelFile.name == model_name)
    m.delete_instance(recursive=True)
    
    # Delete any orphaned subfiles
    if remove_orphans:
        delete_orphans(execute=True)
    
    pm.logit_db.close()


def deleteOrphanFiles(execute=True):
    """Find any orphaned file references and delete them from the database.
    
    Checks the SubFile table for and SubFile.name values that aren't in the
    ModelFile_SubFile table and deletes them.
    
    Args:
        execute=True(bool): I don't think this does anything? Should probably
            always leave as default until further notice. DEBUG.
    """    
    pm.logit_db.connect()
    # Delete any orphaned subfiles
    subs = pm.ModelFile_SubFile.select(pm.ModelFile_SubFile.sub_file_id)
    q = pm.SubFile.delete().where(~(pm.SubFile.name << subs))
    if execute:
        q.execute()
    
    pm.logit_db.close()
    

def updateNewStatus():
    """Updates the Run_ModelFile.new_file and ModelFile_SubFile.new_file status flags.
    
    Updated the new_file status flag to True for all ModelFile and SubFile
    records that come first when ordering by name and timestamp.
    
    For Run_ModelFile the tables are ordered by ModelFile.name, 
    Run_ModelFile.timestamp and the first one updated to True.
    
    For ModelFile_SubFile the tables are ordered by ModelFile.model_type, 
    ModelFile_SubFile.sub_file_id, ModelFile_SubFile.timestamp and the first 
    one updated to True.
    """    
    pm.logit_db.connect()
    query = (pm.ModelFile_SubFile
                .select(pm.ModelFile_SubFile, pm.ModelFile, pm.SubFile)
                .distinct(pm.ModelFile_SubFile.sub_file_id)
                .join(pm.SubFile)
                .switch(pm.ModelFile_SubFile)
                .join(pm.ModelFile)
                .order_by(
                        pm.ModelFile.model_type, 
                        pm.ModelFile_SubFile.sub_file_id, 
                        pm.ModelFile_SubFile.timestamp)
                )
    
    query.execute()
    
    
    query2 = (pm.Run_ModelFile
                .select(pm.Run_ModelFile, pm.Run, pm.ModelFile)
                .distinct(pm.Run_ModelFile.model_file_id)
                .join(pm.ModelFile)
                .switch(pm.Run_ModelFile)
                .join(pm.Run)
                .order_by(
                        pm.ModelFile.name, 
                        pm.Run_ModelFile.timestamp)
                )
    
    query2.execute()
    
    found_names = []
    with pm.logit_db.atomic():
        for q in query:
            i = q.id
            n = q.sub_file_id
            if not n in found_names:
                found_names.append(n)
                q = pm.ModelFile_SubFile.update(new_file=True).where(pm.ModelFile_SubFile.id == i)
                q.execute()
        
        run_found_names = []
        for q in query2:
            ri = q.id
            rn = q.model_file_id
            if not rn in run_found_names:
                run_found_names.append(rn)
                q = pm.Run_ModelFile.update(new_file=True).where(pm.Run_ModelFile.id == ri)
                q.execute()
    
    pm.logit_db.close()


def updateRunRow(updateDict, run_id):
    """Update values in the Run table.
    
    Args:
        updateDict(dict): containing {fieldname: value} pairs for updating.
        run_id(int): the Run.id value to query.
    """
    pm.logit_db.connect()
    query = pm.Run.update(**updateDict).where(pm.Run.id == run_id)
    query.execute()
    pm.logit_db.close()
    

def updateDatRow(updateDict, dat_name):
    """Update values in the Dat table.
    
    Args:
        updateDict(dict): containing {fieldname: value} pairs for updating.
        dat_name(str): the Dat.name value to query.
    """
    pm.logit_db.connect()
    query = pm.Dat.update(**updateDict).where(pm.Dat.name == dat_name)
    query.execute()
    pm.logit_db.close()
    

def updateModelRow(updateDict, model_name):
    """Update values in the ModelFile table.
    
    Args:
        updateDict(dict): containing {fieldname: value} pairs for updating.
        model_name(str): the ModelFile_name value to query.
    """
    pm.logit_db.connect()
    query = pm.ModelFile.update(**updateDict).where(pm.ModelFile.name == model_name)
    query.execute()
    pm.logit_db.close()


def getRunData():
    """Return records for the Run table.
    
    Return:
        tuple(cols:header strings, rows: list of record data).
    """
    pm.logit_db.connect()
    rquery = pm.Run.select()
    
    cols = [
        'id', 'timestamp', 'run_hash', 'run_options', 'event_name', 
        'setup', 'comments', 'ief', 'tcf', 'isis_results', 'tuflow_results', 
        'estry_results', 'event_duration', 'modeller', 'isis_version',
        'tuflow_version', 'ief_dir', 'tcf_dir', 'log_dir', 'run_status',
        'mb'
    ]
    rows = []
    for r in rquery:
        rows.append(
            [
             r.id, r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.run_hash,
             r.run_options, r.event_name, r.setup, r.comments, r.ief, r.tcf, 
             r.isis_results, r.tuflow_results, r.estry_results, 
             r.event_duration, r.modeller, 
             r.isis_version, r.tuflow_version, r.ief_dir,
             r.tcf_dir, r.log_dir, r.run_status, r.mb
            ]
        )
    pm.logit_db.close()
    
    return cols, rows
 

def getModelData(model):
    """Return records for the ModelFile or Dat tables.
    
    Args:
        model(str): either 'DAT' or 'MODEL'. If anything else will return 'MODEL'.
    
    Return:
        tuple(cols:header strings, rows: list of record data).
    """
    pm.logit_db.connect()
    if model == 'DAT':
        mquery = pm.Dat.select()
        cols = ['timestamp', 'name', 'amendments', 'comments']
        rows = []
        for r in mquery:
            rows.append([r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.name, r.amendments, r.comments])
    
    else:
        mquery = pm.ModelFile.select().where(pm.ModelFile.model_type == model)
        cols = ['timestamp', 'name', 'comments']
        rows = []
        for r in mquery:
            rows.append([r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.name, r.comments])
    pm.logit_db.close()
    
    return cols, rows

def getSimpleQuery(table, value1, with_files, new_sub_only, new_model_only, run_id, value2=''):
    """Get the results of a query from the database.
    
    This is a bit of a beast of a function, but it seems hard to break it down 
    until I find a better/neater way of running the queryies.
    
    Basically returns header columns, row data list, tuple for using. It is a 
    bit of a black box at the moment. It is not possible to state which fields
    will be used, only the values to test them against.
    
    Args:
        table (str): table name in the db.
        value1(str): field value to check.
        with_files(bool): Used with queries on the ModelFile table. States whether
            to return associated SubFiles or not.
        new_sub_only(bool): If True and with_files==True it will return only
            the associated SubFiles that have new_file == True.
        new_model_only(bool): Same as new_sub_only, but for ModelFile.
        run_id(int): the Run.id value to compare. If -1 it will not be used.
        value2=''(str): optional second field value to check.
    """
    
    pm.logit_db.connect()
    cols = []
    rows = []
    if table == 'DAT':
        
        cols = ['Date', 'Name', 'Amendments', 'Comments']
        rows = []
        
        # If run_id given - select all with that id
        if run_id != -1:
            query = (pm.Run
                        .select(pm.Run, pm.Dat)
                        .join(pm.Dat)
                        .where(pm.Run.id == run_id)
                     )
            cols = ['Run ID', 'Date', 'Name', 'Amendments', 'Comments']
            for r in query:
                rows.append([r.id, r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.dat.name, r.dat.amendments, r.dat.comments])
        else:
            query = pm.Dat.select()
            query = checkWildcard(query, pm.Dat.name, value1)
        
            cols = ['Date', 'Name', 'Amendments', 'Comments']
            for r in query:
                rows.append([r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.name, r.amendments, r.comments])
    
    elif table == 'RUN Options' or table == 'RUN Event':

        query = pm.Run.select()
        if table == 'RUN Event':
            query = checkWildcard(query, pm.Run.event_name, value1)
        else:
            query = checkWildcard(query, pm.Run.run_options, value1)
   
        cols = ['Date', 'Event Name', 'Run Options', 'Comments', 'Status', 'MB']
        rows = []
        for r in query:
            rows.append([r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.event_name, r.run_options, r.comments, r.run_status, r.mb])

    
    else:
        # Returning associated SubFile's as well so extra queries for the
        # value2 param will be needed
        if with_files:
           
            # If using a run_id we need to join the Run_ModelFile table too
            if run_id != -1:
                query = (pm.ModelFile_SubFile
                        .select(pm.ModelFile_SubFile, pm.ModelFile, pm.SubFile, pm.Run_ModelFile)
                        .join(pm.SubFile)
                        .switch(pm.ModelFile_SubFile)
                        .join(pm.ModelFile)
                        .join(pm.Run_ModelFile)
                        )
            else:
                query = (pm.ModelFile_SubFile
                        .select(pm.ModelFile_SubFile, pm.ModelFile, pm.SubFile)
                        .join(pm.SubFile)
                        .switch(pm.ModelFile_SubFile)
                        .join(pm.ModelFile)
                        )
            
            if not table == 'All Modelfiles':
                    query = query.where(pm.ModelFile.model_type == table)
            
            query = checkWildcard(query, pm.ModelFile.name, value1)
            query = checkWildcard(query, pm.SubFile.name, value2)
            
            if new_sub_only:
                query = query.where(pm.ModelFile_SubFile.new_file == True)
            

            rows = []
            if run_id != -1:

                if new_model_only:
                    query = query.where(pm.Run_ModelFile.new_file == True)

                query = query.where(pm.Run_ModelFile.run_id == run_id)
                cols = ['Run ID', 'Modelfile Timestamp', 'Model Type', 'Modelfile', 'Modelfile New', 'Comments', 'Subfile', 'Subfile Timestamp', 'Subfile New']
                for r in query:
                    rows.append([r.model_file.run_modelfile.run_id, r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.model_file.model_type, r.model_file.name, r.model_file.run_modelfile.new_file, r.model_file.comments, r.sub_file.name, r.sub_file.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.new_file])
            
            else:
                cols = ['Modelfile Timestamp', 'Model Type', 'Modelfile', 'Comments', 'Subfile', 'Subfile Timestamp', 'Subfile New']
                for r in query:
                    rows.append([r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.model_file.model_type, r.model_file.name, r.model_file.comments, r.sub_file.name, r.sub_file.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.new_file])
        
        # If not with_files then we don't need to join the SubFile and 
        # ModelFile_SubFile tables
        else:
            query = (pm.Run_ModelFile
                        .select(pm.Run_ModelFile, pm.Run, pm.ModelFile)
                        .join(pm.ModelFile)
                        .switch(pm.Run_ModelFile)
                        .join(pm.Run))

            if not table == 'All Modelfiles':
                query = query.where(pm.ModelFile.model_type == table)
            
            query = checkWildcard(query, pm.ModelFile.name, value1)
            
            if new_model_only:
                query = query.where(pm.Run_ModelFile.new_file == True)
            
            if run_id != -1:
                query = query.where(pm.Run.id == run_id)
            
                cols = ['Run ID', 'Modelfile Timestamp', 'Modelfile New', 'Model Type', 'Modelfile', 'Comments']
                rows = []
                for r in query:
                    rows.append([r.run_id, r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.new_file, r.model_file.model_type, r.model_file.name, r.model_file.comments])
            else:
                cols = ['Run ID', 'Modelfile Timestamp', 'Modelfile New', 'Model Type', 'Modelfile', 'Comments']
                rows = []
                for r in query:
                    rows.append([r.run_id, r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.new_file, r.model_file.model_type, r.model_file.name, r.model_file.comments])
                
    
    pm.logit_db.close()
    
    return cols, rows


def checkWildcard(query, tableField, value):
    """Return query with appropriate where clause for wildcard use.
    
    If value == '' the query will be return as provided.
    
    Args:
        query(SelectQuery): an existing query to amend.
        tableField(peewee.Model): to use in the new where clause.
        value(str): to check for wildcard characters.
    
    Return:
        SelectQuery - 'and-ed' with exactly equal or wildcard equal clause.
    """

    if not value.strip() == '':
        if '%' in value:
            query = query.where(tableField ** value)
        else:
            query = query.where(tableField == value)
    
    return query
    


def createModelExport():
    """Get the ModelFile's and SubFile's formatted for writing to file.
    
    This is designed to be used for the Excel export. It returns a dict with
    ModelFile.model_type keys, containing a dict of ModelFile.name, containing
    a dict of values to write out. These are:
     - type: the ModelFile.model_type
     - date: str date formatted to yyyy/mm/dd
     - comments: str
     - files: list of all SubFile's associated to the ModelFile.
     - new_files: same as files, but only where SubFile.new_file == True.
     
     Return:
         dict
    """
    
    query = (pm.ModelFile_SubFile
            .select(pm.ModelFile_SubFile, pm.ModelFile, pm.SubFile)
            .join(pm.SubFile)
            .switch(pm.ModelFile_SubFile)
            .join(pm.ModelFile)
            )
    
    model_out = {}
    for q in query:
        t = q.model_file.model_type
        if not t in model_out.keys():
            model_out[t] = {}
        else:
            
            if not q.model_file.name in model_out[t].keys():
                model_out[t][q.model_file.name] = {'type': q.model_file.model_type, 'comments': q.model_file.comments, 'files': [], 'new_files': [], 'date': q.model_file.timestamp.strftime("%Y-%m-%d")}
                model_out[t][q.model_file.name]['files'].append(q.sub_file.name)
                if q.new_file == True: model_out[t][q.model_file.name]['new_files'].append(q.sub_file.name)
            else:
                model_out[t][q.model_file.name]['files'].append(q.sub_file.name)
                if q.new_file == True: model_out[t][q.model_file.name]['new_files'].append(q.sub_file.name)
    
    return model_out 
    

def createRunDatExport():
    """Get the Run and Dat tables formatted for writing to file.
    
    This is designed to be used for the Excel export. It returns dict for the
    Run and Dat tables with Run.id and Dat.name keys. Each dict entry is a list
    of values pulled out from the table.
    The header values are returned in two seperate lists.
     
     Return:
         tuple(dict:run, list:run headers, dict:dat, list:dat header)
    """
    
    query = (pm.Run_ModelFile
            .select(pm.Run_ModelFile, pm.Run, pm.ModelFile)
            .join(pm.ModelFile)
            .switch(pm.Run_ModelFile)
            .join(pm.Run))
    
    run_header = ['id', 'date', 'dat','setup', 'ief', 'isis_results','tuflow_results', 
                  'estry_results', 'event_duration', 'comments', 'isis_version', 
                  'event_name', 'run_options', 'run_status', 'mb', 'files'
                 ]
    dat_header = ['name', 'date', 'amendments', 'comments']
    run_out = {}
    dat_out = {}
    for q in query:
        r = q.run
        if not r.id in run_out.keys():
            if not r.dat.name in dat_out.keys():
                dat_out[r.dat.name] = [r.dat.name, r.dat.timestamp.strftime("%Y-%m-%d"),
                                       r.dat.amendments, r.dat.comments]
            run_out[r.id] = [r.id, r.timestamp.strftime("%Y-%m-%d"), r.dat.name,
                             r.setup, r.ief, r.isis_results, r.tuflow_results, 
                             r.estry_results, r.event_duration, r.comments, 
                             r.isis_version, r.event_name, r.run_options, 
                             r.run_status, r.mb, []]
        else:
            if not q.model_file.name in run_out[r.id][-1]:
                run_out[r.id][-1].append(q.model_file.name)
            
    return run_out, run_header, dat_out, dat_header
 

def checkDatabaseVersion(db_path):
    """Check the database version number to make sure it is the same as the
    current version of the software. If it's not we return False because the
    user needs to either update the database settings or use an older version.
    
    Args:
        db_path: path to an existing database.
    
    Raises:
        IOError: if db_path does not point to a database or it is not a
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
            if not db_version == pm.DATABASE_VERSION_NO:
                if db_version > pm.DATABASE_VERSION_NO:
                    return pm.DATABASE_VERSION_HIGH
                
                if db_version < pm.DATABASE_VERSION_NO:
                    if db_version < pm.NEW_DB_START:
                        return pm.DATABASE_VERSION_OLD
                    else:
                        return pm.DATABASE_VERSION_LOW
            else:
                return pm.DATABASE_VERSION_SAME       
            
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



    
