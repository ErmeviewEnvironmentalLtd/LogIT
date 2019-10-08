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


TABLE_CHOICE = ['', 'DAT', 'IED', 'TCF', 'ECF', 'TGC', 'TBC', 'BC_DBASE', 'TEF', 'TRD']
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
    pm.connectDB()
    try:
        d, crtd = pm.Dat.create_or_get(name=dat['NAME'], amendments=dat['AMENDMENTS'], comments=dat['COMMENTS'])
    finally:
        pm.disconnectDB()
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
    pm.connectDB()
    
    try:
        if dat is not None:
            r = pm.Run(dat=dat, run_hash=run_hash, setup=run['SETUP'], modeller=run['MODELLER'],
                    ief=run['IEF'], tcf=run['TCF'], initial_conditions=run['INITIAL_CONDITIONS'], 
                    isis_results=run['ISIS_RESULTS'], tuflow_results=run['TUFLOW_RESULTS'],
                    estry_results=run['ESTRY_RESULTS'], event_duration=run['EVENT_DURATION'],
                    comments=run['COMMENTS'], isis_version=run['ISIS_BUILD'], tuflow_version=run['TUFLOW_BUILD'],
                    event_name=run['EVENT_NAME'], ief_dir=ief_dir, tcf_dir=tcf_dir,
                    log_dir=run['LOG_DIR'], run_options=run['RUN_OPTIONS'], 
                    run_status=run['RUN_STATUS'], mb=run['MB'])
        else:
            r = pm.Run(run_hash=run_hash, setup=run['SETUP'], modeller=run['MODELLER'],
                    ief=run['IEF'], tcf=run['TCF'], initial_conditions=run['INITIAL_CONDITIONS'], 
                    isis_results=run['ISIS_RESULTS'], tuflow_results=run['TUFLOW_RESULTS'],
                    estry_results=run['ESTRY_RESULTS'], event_duration=run['EVENT_DURATION'],
                    comments=run['COMMENTS'], isis_version=run['ISIS_BUILD'], tuflow_version=run['TUFLOW_BUILD'],
                    event_name=run['EVENT_NAME'], ief_dir=ief_dir, tcf_dir=tcf_dir,
                    log_dir=run['LOG_DIR'], run_options=run['RUN_OPTIONS'],
                    run_status=run['RUN_STATUS'], mb=run['MB'])
        r.save()
    finally:
        pm.disconnectDB()
    return r


def addAllIed(ieds, run):
    """Add all of the provided Ied files to the database.
    
    Updates the Ied entries and Run_Ied many to many entries.
    
    Will only add a new entry to the Ied table if the name doesn't already
    exist.
    
    Args:
        ieds(list): containing dictionaries with values to update with.
        run(int): the Run.id to use as foreign key in the Run_ModelFile table.
    """
    ied_datasource = []
    ri_datasource = []
    found_ieds = []
    
    for i in ieds:
        if not i['NAME'] in found_ieds and not iedExists(i['NAME']):
            ied_datasource.append({'name': i['NAME'], 'ref': i['REF'], 'amendments': i['AMENDMENTS'], 'comments': i['COMMENTS']})
            found_ieds.append(i['NAME'])
            ri_datasource.append({'run': run, 'ied': i['NAME'], 'new_file': True})
        else:
            ri_datasource.append({'run': run, 'ied': i['NAME'], 'new_file': False})
    
    # Use atomic for create calls - MASSIVE write speed increase.
    if ied_datasource or ri_datasource:
        with pm.logit_db.atomic():
            for data_dict in ied_datasource:
                pm.Ied.create(**data_dict)
            for data_dict in ri_datasource:
                pm.Run_Ied.create(**data_dict)
        

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
    mf_datasource = []      # Modelfile_SubFile
    rm_datasource = []      # Run_ModelFile
    rs_datasource = []      # Run_SubFile
    
    found_models = []
    found_files = []
    found_modelfiles = []
    
    # Loop all of the model files
    for m in mfiles:
        if not m['NAME'] in found_models and not modelExists(m['NAME']): 
            model_datasource.append({'name': m['NAME'], 'model_type': m['TYPE'], 'comments': m['COMMENTS']})
            found_models.append(m['NAME'])
            rm_datasource.append({'run': run, 'model_file': m['NAME'], 'new_file': True})
        else:
            rm_datasource.append({'run': run, 'model_file': m['NAME'], 'new_file': False})
        
        # Loop all of the subfiles
        for f in m['FILES']:
            first_time = False
            
            # Add to Run_SubFile list and check new status
            rs_datasource.append({'run': run, 'sub_file': f})
            if subFileIsNew(m['TYPE'], f):
                first_time = True
            
            # Add to SubFile list
            if not f in found_files and not subfileExists(f):
                files_datasource.append({'name': f})
                found_files.append(f)
            
            # Add to ModelFile_Subfile list
            if not ((m['NAME'] + f) in found_modelfiles) and  not modelSubfileExists(m['NAME'], f):
                mf_datasource.append({'model_file': m['NAME'], 'sub_file': f, 'new_file': first_time})
                found_modelfiles.append(m['NAME'] + f)
            
    # Use atomic for create calls - MASSIVE write speed increase.
    with pm.logit_db.atomic():
        for data_dict in model_datasource:
            pm.ModelFile.create(**data_dict)
        for data_dict in files_datasource:
            pm.SubFile.create(**data_dict)
        for data_dict in mf_datasource:
            pm.ModelFile_SubFile.create(**data_dict)
        for data_dict in rm_datasource:
            pm.Run_ModelFile.create(**data_dict)
        for data_dict in rs_datasource:
            pm.Run_SubFile.create(**data_dict)
            

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

def iedExists(name):
    query = pm.Ied.select().where(pm.Ied.name == name)
    if query.exists():
        return True
    else:
        return False

def allModelsExists(name):
    
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

def RunSubfileExists(r, s):
    query = pm.Run_SubFile.select().where((pm.Run_SubFile.run_file_id == r) & (pm.Run_SubFile.sub_file_id == s))
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
    pm.connectDB()
    try:
        query = pm.Run.get(pm.Run.id == run_id)
        run = shortcuts.model_to_dict(query, recurse=False)
    finally:
        pm.disconnectDB()
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
    pm.connectDB()
    
    try:
        model_del = []
        ied_del = []
        dat = None
        r = None
        try:
            r = pm.Run.get(pm.Run.id == run_id)
        except Exception as err:
            logger.warning('Could not find entry for run_id = %s' % run_id)
            logger.exception(err)

        if delete_recursive:
            
            # If we have a dat in this run
            if r.dat is not None:
                run_d = pm.Dat.get(name=r.dat)
                
                # If that dat isn't referenced in any other runs
                if pm.Run.select().filter(dat=run_d.name).count() < 2:
                    dat = run_d.name
            
    #         # Get all the run_subfile's referenced
    #         sq = pm.Run_SubFile.select().where(pm.Run_SubFile.run_id == run_id)

            # Get all modelfile's and a count of how many times there are referenced
            mq = (pm.Run_ModelFile
                    .select(pm.Run_ModelFile.run_id, pm.Run_ModelFile.model_file_id, fn.Count(pm.Run_ModelFile.model_file_id).alias('count'))
                    .group_by(pm.Run_ModelFile.model_file_id)
                 )
            # If they are only referenced by this run add to the delete list
            # TODO: VERY slow. Must try harder
            for m in mq:
                if m.count < 2 and m.run_id == run_id:
                    model_del.append(m.model_file_id)
            
            # Do the same for ied files
            iq = (pm.Run_Ied
                    .select(pm.Run_Ied.run_id, pm.Run_Ied.ied_id, fn.Count(pm.Run_Ied.ied_id).alias('count'))
                    .group_by(pm.Run_Ied.ied_id)
                 )
            for i in iq:
                if i.count < 2 and i.run_id == run_id:
                    ied_del.append(i.ied_id)
            

        r.delete_instance(recursive=delete_recursive)
        
        with pm.logit_db.atomic():
            if dat is not None: 
                deleteDatRow(dat)
            for m in model_del:
                deleteModelRow(m, remove_orphans=False)
            for i in ied_del:
                deleteIedRow(i, remove_orphans=False)

    finally:
        pm.disconnectDB()
    

def deleteDatRow(dat_name):
    """Delete a record in the Dat table.
    
    Deletes the specified Dat record.
    
    Args:
        dat_name(str): the Dat.name to query against.
    """
    pm.connectDB()
    try:
        d = pm.Dat.get(pm.Dat.name == dat_name)
        d.delete_instance()
    finally:
        pm.disconnectDB()
    

def deleteIedRow(ied_name, remove_orphans=True):
    """Delete a record in the Ied table.
    
    Deletes the specified Ied record.
    
    Args:
        ied_name(str): the Ied.name to query against.
    """
    pm.connectDB()
    try:
        i = pm.Ied.get(pm.Ied.name == ied_name)
        i.delete_instance()
    finally:
        pm.disconnectDB()
    

def deleteModelRow(model_name, remove_orphans=True):
    """Delete a record in the ModelFile table.
    
    Deletes the specified ModelFile record and any foreign key associations.
    
    Args:
        model_name(str): the ModelFile.name to query against.
        remove_orphans=True(bool): if True will call deleteOrphanFiles after.
    """
    pm.connectDB()
    try:
        m = pm.ModelFile.get(pm.ModelFile.name == model_name)
        m.delete_instance(recursive=True)
        
        # Delete any orphaned subfiles
        if remove_orphans:
            deleteOrphanFiles(execute=True)
        
    finally:
        pm.disconnectDB()


def deleteOrphanFiles(run_id=-1, execute=True):
    """Find any orphaned file references and delete them from the database.
    
    Checks the SubFile table for and SubFile.name values that aren't in the
    ModelFile_SubFile table and deletes them.
    
    Args:
        execute=True(bool): I don't think this does anything? Should probably
            always leave as default until further notice. DEBUG.
    """    
    pm.connectDB()

    try:
        # Delete any orphaned subfiles
        subs = pm.ModelFile_SubFile.select(pm.ModelFile_SubFile.sub_file_id)
        q = pm.SubFile.delete().where(~(pm.SubFile.name << subs))
        if execute:
            q.execute()
        # Need to clean up the subfile entries as well
        subs = pm.Run_SubFile.select(pm.Run_SubFile.sub_file_id)
        q = pm.SubFile.delete().where(~(pm.SubFile.name << subs))
        if execute:
            q.execute()
        
        if not run_id == -1:
            # Delete all of the run references subfile (Run_SubFile)
            rsquery = pm.Run_SubFile.delete().where(pm.Run_SubFile.run_id == run_id)
            if execute:
                rsquery.execute()
        
            # Delete all of the run referencd ied files (Run_Ied)
            iquery = pm.Run_Ied.delete().where(pm.Run_Ied.run_id == run_id)
            if execute:
                iquery.execute()
    
    finally:
        pm.disconnectDB()
    

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
    pm.connectDB()
    try:
        query = (pm.ModelFile_SubFile
                    .select(pm.ModelFile_SubFile, pm.ModelFile, pm.SubFile)
                    #.distinct(pm.ModelFile_SubFile.sub_file_id)
                    .join(pm.SubFile)
                    .switch()#pm.ModelFile_SubFile)
                    .join(pm.ModelFile)
                    .order_by(
                            pm.ModelFile.model_type, 
                            pm.ModelFile_SubFile.sub_file_id, 
                            pm.ModelFile_SubFile.timestamp)
                    )
        
        query.execute()
    except:
        pm.disconnectDB()
        raise
    
    
    try:
        query2 = (pm.Run_ModelFile
                    .select(pm.Run_ModelFile, pm.Run, pm.ModelFile)
                    #.distinct(pm.Run_ModelFile.model_file_id)
                    .join(pm.ModelFile)
                    .switch(pm.Run_ModelFile)
                    .join(pm.Run)
                    .order_by(
                            pm.ModelFile.name, 
                            pm.Run_ModelFile.timestamp)
                    )
        
        query2.execute()
    except:
        pm.disconnectDB()
        raise
    
    try:
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
    finally:
        pm.disconnectDB()


def updateRunRow(updateDict, run_id):
    """Update values in the Run table.
    
    Args:
        updateDict(dict): containing {fieldname: value} pairs for updating.
        run_id(int): the Run.id value to query.
    """
    pm.connectDB()
    try:
        query = pm.Run.update(**updateDict).where(pm.Run.id == run_id)
        query.execute()
    finally:
        pm.disconnectDB()
    

def updateDatRow(updateDict, dat_name):
    """Update values in the Dat table.
    
    Args:
        updateDict(dict): containing {fieldname: value} pairs for updating.
        dat_name(str): the Dat.name value to query.
    """
    pm.connectDB()
    try:
        query = pm.Dat.update(**updateDict).where(pm.Dat.name == dat_name)
        query.execute()
    finally:
        pm.disconnectDB()
    

def updateIedRow(updateDict, ied_name):
    """Update values in the Ied table.
    
    Args:
        updateDict(dict): containing {fieldname: value} pairs for updating.
        ied_name(str): the Ied.name value to query.
    """
    pm.connectDB()
    try:
        query = pm.Ied.update(**updateDict).where(pm.Ied.name == ied_name)
        query.execute()
    finally:
        pm.disconnectDB()


def updateModelRow(updateDict, model_name):
    """Update values in the ModelFile table.
    
    Args:
        updateDict(dict): containing {fieldname: value} pairs for updating.
        model_name(str): the ModelFile_name value to query.
    """
    pm.connectDB()
    try:
        query = pm.ModelFile.update(**updateDict).where(pm.ModelFile.name == model_name)
        query.execute()
    finally:
        pm.disconnectDB()


def getRunData():
    """Return records for the Run table.
    
    Return:
        tuple(cols:header strings, rows: list of record data).
    """
    pm.connectDB()
    cols = [
        'id', 'timestamp', 'run_hash', 'run_options', 'event_name', 
        'setup', 'comments', 'ief', 'tcf', 'initial_conditions', 'isis_results', 
        'tuflow_results', 'estry_results', 'event_duration', 'modeller', 
        'isis_version', 'tuflow_version', 'ief_dir', 'tcf_dir', 'log_dir', 
        'run_status', 'mb'
    ]
    rows = []
    try:
        rquery = pm.Run.select()
        rows = []
        for r in rquery:
            rows.append(
                [
                 r.id, r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.run_hash,
                 r.run_options, r.event_name, r.setup, r.comments, r.ief, r.tcf, 
                 r.initial_conditions, r.isis_results, r.tuflow_results, r.estry_results, 
                 r.event_duration, r.modeller, 
                 r.isis_version, r.tuflow_version, r.ief_dir,
                 r.tcf_dir, r.log_dir, r.run_status, r.mb
                ]
            )
    finally:
        pm.disconnectDB()
    
    return cols, rows


def getModelData(model):
    """Return records for the ModelFile or Dat tables.
    
    Args:
        model(str): either 'DAT' or 'MODEL'. If anything else will return 'MODEL'.
    
    Return:
        tuple(cols:header strings, rows: list of record data).
    """
    pm.connectDB()
    cols = []
    rows = []
    try:
        if model == 'DAT':
            mquery = pm.Dat.select()
            cols = ['timestamp', 'name', 'amendments', 'comments']
            for r in mquery:
                rows.append([r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.name, r.amendments, r.comments])
        
        elif model == 'IED':
            mquery = pm.Ied.select()
            cols = ['timestamp', 'name', 'ref', 'amendments', 'comments']
            for r in mquery:
                rows.append([r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.name, r.ref, r.amendments, r.comments])
        
        else:
            mquery = pm.ModelFile.select().where(pm.ModelFile.model_type == model)
            cols = ['timestamp', 'name', 'comments']
            for r in mquery:
                rows.append([r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.name, r.comments])
    finally:
        pm.disconnectDB()
    
    return cols, rows


def getFileSummaryQuery(ids):
    """
    """
    cols = ['ID', 'RUN OPTIONS', 'IEF', 'TCF', 'ECF', 'TGC', 'TBC', 'BC_DBASE',
            'TEF', 'TRD']

    query = (pm.Run_ModelFile
            .select(pm.Run_ModelFile, pm.Run, pm.ModelFile)
            .join(pm.ModelFile)
            .switch(pm.Run_ModelFile)
            .join(pm.Run)
            .where(pm.Run.id << ids)
            )
    found_runs = {}
    output = []
    for q in query:
        if not q.run_id in found_runs.keys():
            cur_index = len(output) 
            found_runs[q.run_id] = cur_index
            output.append({'id': q.run_id, 'run_options': q.run.run_options,
                           'ief': q.run.ief, 'TCF': [], 'ECF': [], 'TGC': [],
                           'TBC': [], 'BC_DBASE': [], 'TEF': [], 'TRD': [],
                           'NEW_TCF': False, 'NEW_ECF': False, 'NEW_TGC': False,
                           'NEW_TBC': False, 'NEW_BC_DBASE': False, 'NEW_TEF': False,
                           'NEW_TRD': False})
        else:
            cur_index = found_runs[q.run_id]
        
        if not q.model_file.name in output[cur_index][q.model_file.model_type]:
            output[cur_index][q.model_file.model_type].append(q.model_file.name)
        if q.new_file == True:
            output[cur_index]['NEW_' + q.model_file.model_type] = True
    
    new_output = []
    new_status = []
    for o in output:
        new_output.append([o['id'], o['run_options'], o['ief'],
                          ', '.join(o['TCF']),
                          ', '.join(o['ECF']),
                          ', '.join(o['TGC']),
                          ', '.join(o['TBC']),
                          ', '.join(o['BC_DBASE']),
                          ', '.join(o['TEF']),
                          ', '.join(o['TRD']),
                          ])
        new_status.append([False, False, False, o['NEW_TCF'], o['NEW_ECF'], 
                          o['NEW_TGC'], o['NEW_TBC'], o['NEW_BC_DBASE'],
                          o['NEW_TEF'], o['NEW_TRD']])
    
    return cols, new_output, new_status
    

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
    
    pm.connectDB()
    cols = []
    rows = []
    try:
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
        
        elif table == 'IED':
            rows = []
            
            # If using a run_id we need to join the Run_ModelFile table too
            if run_id != -1:
                query = (pm.Run_Ied
                        .select(pm.Run_Ied, pm.Ied)
                        .join(pm.Ied)
                        .switch(pm.Run_Ied)
                        .where(pm.Run_Ied.run_id == run_id)
                        )
                cols = ['Run ID', 'Date', 'Name', 'Ref', 'Amendments', 'Comments']
                for r in query:
                    rows.append([r.run_id, r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.ied.name, r.ied.ref, r.ied.amendments, r.ied.comments])
            else:
                query = pm.Ied.select()
                cols = ['Date', 'Name', 'Ref', 'Amendments', 'Comments']
                for r in query:
                    rows.append([r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.name, r.ref, r.amendments, r.comments])
        
        elif table == 'RUN Options' or table == 'RUN Event':

            query = pm.Run.select()
            if table == 'RUN Event':
                query = checkWildcard(query, pm.Run.event_name, value1)
            else:
                query = checkWildcard(query, pm.Run.run_options, value1)
       
            cols = ['Run ID', 'Date', 'Event Name', 'Run Options', 'Comments', 'Status', 'MB']
            rows = []
            for r in query:
                rows.append([str(r.id), r.timestamp.strftime("%Y-%m-%d %H:%M:%S"), r.event_name, r.run_options, r.comments, r.run_status, r.mb])

        
        else:
            # Returning associated SubFile's as well so extra queries for the
            # value2 param will be needed
            if with_files:
               
                # If using a run_id we need to join the Run_ModelFile and Run_Subfile 
                # tables too
                if run_id != -1:
                    query = (pm.ModelFile_SubFile
                            .select(pm.ModelFile_SubFile, pm.ModelFile, pm.SubFile, pm.Run_ModelFile, pm.Run_SubFile)
                            .join(pm.SubFile)
                            .switch(pm.ModelFile_SubFile)
                            .join(pm.ModelFile)
                            .join(pm.Run_ModelFile)
                            .switch(pm.SubFile)
                            .join(pm.Run_SubFile)
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
                    
                    # Filter model files by run id
                    query = query.where(pm.Run_ModelFile.run_id == run_id)
                    # Filter subfiles by run id
                    query = query .where(pm.Run_SubFile.run_id == run_id)
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
                    
    finally: 
        pm.disconnectDB()
    
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
            .order_by(pm.ModelFile.model_type.asc(), pm.ModelFile.timestamp.asc(), pm.ModelFile.name.asc())
            )
    
    model_out = {}
    found_models = {}
    for q in query:
        
        if not q.model_file.model_type in model_out.keys():
            model_out[q.model_file.model_type] = []
            
        if not q.model_file.name in found_models.keys():
            model_out[q.model_file.model_type].append({'name': q.model_file.name, 'type': q.model_file.model_type, 'comments': q.model_file.comments, 'date': q.model_file.timestamp.strftime("%Y-%m-%d"), 'files': [], 'new_files': []})
            cur_index = len(model_out[q.model_file.model_type]) - 1
            found_models[q.model_file.name] = {'type': q.model_file.model_type, 'index': cur_index}
        else:
            cur_index = found_models[q.model_file.name]['index']
        
        model_out[q.model_file.model_type][cur_index]['files'].append(q.sub_file.name)
        if q.new_file == True: model_out[q.model_file.model_type][cur_index]['new_files'].append(q.sub_file.name)
    
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
    
    run_header = ['id', 'date', 'modeller', 'event_name', 'setup', 'ief', 'dat', 
                  'initial_conditions', 'isis_results', 'tuflow_results', 
                  'estry_results', 'event_duration', 'comments', 'isis_version', 
                  'tuflow_version', 'run_options', 'run_status', 'mb', 'files'
                 ]
    dat_header = ['name', 'date', 'amendments', 'comments']
    run_out = {}
    dat_out = []
    found_dats = []
    for q in query:
        r = q.run
        if not r.id in run_out.keys():
            if r.dat and not r.dat.name in found_dats:
                dat_out.append([r.dat.name, r.dat.timestamp.strftime("%Y-%m-%d"),
                                       r.dat.amendments, r.dat.comments])
                found_dats.append(r.dat.name)
                dat_name = r.dat.name
            else:
                dat_name = 'None'

            run_out[r.id] = [r.id, r.timestamp.strftime("%Y-%m-%d"), r.modeller, 
                             r.event_name, r.setup, r.ief,  dat_name, 
                             r.initial_conditions, r.isis_results, r.tuflow_results, 
                             r.estry_results, r.event_duration, r.comments, 
                             r.isis_version, r.tuflow_version, r.run_options, 
                             r.run_status, r.mb, []]
        else:
            if not q.model_file.name in run_out[r.id][-1]:
                run_out[r.id][-1].append(q.model_file.name)
            
    return run_out, run_header, dat_out, dat_header


def createIedExport():
    """Get the Ied data table formatted for writing to file.
    
    Used for collecting all of the data into a list for exporting to another
    medium, such as a the Excel exporting funcationality.
    
    Return:
    
    """
    ied_header = ['name', 'date', 'ammendments', 'comments']
    query = pm.Ied.select()
    ied_out = []
    for q in query:
        ied_out.append([q.name, q.timestamp.strftime("%Y-%m-%d"),
                        q.amendments, q.comments])
    
    return ied_out, ied_header
        
 
def complexQuery(db_path, raw_query):
    
    upper_raw = raw_query.upper()
    if 'DELETE' in upper_raw or 'DROP' in upper_raw or 'INSERT' in upper_raw or \
                        'TRUNCATE' in upper_raw or 'UPDATE' in upper_raw or \
                        'ALTER' in upper_raw or 'CASCADE' in upper_raw or \
                        'COMMIT' in upper_raw or 'DESTROY' in upper_raw or \
                        'EXECUTE' in upper_raw or 'MODIFY' in upper_raw or \
                        'PURGE' in upper_raw or 'REPLACE' in upper_raw or \
                        'RESTORE' in upper_raw or 'ROLLBACK' in upper_raw or \
                        'SAVE' in upper_raw or 'WRITE' in upper_raw or \
                        'CREATE' in upper_raw or 'CLONE' in upper_raw:
        return None, None, 'Queries to update tables are not allowed.'
    
    query = ' '.join(raw_query.split())
    
    conn = None
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(query)
        
        cols = [i[0] for i in cur.description]
        rows = []
        for row in cur:
            rows.append(row)
            i=0 
    except sqlite3.OperationalError as err:
#         logger.exception(err)
        return None, None, str(err)
    except sqlite3.DatabaseError as err:
        logger.exception(err)
        return None, None, str(err)
    except IOError as err:
        logger.exception(err)
        return None, None, str(err)
    except Exception as err:
        logger.exception(err)
        return None, None, str(err)
    
    finally:
        if not conn is None:
            conn.close()
    
    return cols, rows, ''


def checkDatabaseVersion(db_path, return_version=False):
    """Check the database version number to make sure it is the same as the
    current version of the software. If it's not we return False because the
    user needs to either update the database settings or use an older version.
    
    Args:
        db_path: path to an existing database.
        return_version=False: if True will return a tuple of (status, version)
    
    Return:
        int - of database comparison status using the peeweemodels constants
            of DATABASE_VERSION_HIGH, LOW, SAME.
            If return_version==True it will return a tuple containing the 
            status and the actual version number.
            
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
                    if return_version:
                        return pm.DATABASE_VERSION_HIGH, db_version
                    else:
                        return pm.DATABASE_VERSION_HIGH
                
                if db_version < pm.DATABASE_VERSION_NO:
                    if db_version < pm.NEW_DB_START:
                        if return_version:
                            return pm.DATABASE_VERSION_OLD, db_version
                        else:
                            return pm.DATABASE_VERSION_OLD
                    else:
                        if return_version:
                            return pm.DATABASE_VERSION_LOW, db_version
                        else:
                            return pm.DATABASE_VERSION_LOW
            else:
                if return_version:
                    return pm.DATABASE_VERSION_SAME, db_version
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



    
