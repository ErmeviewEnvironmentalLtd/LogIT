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
# Module:  LogBuilder.py
# Date:  16/11/2014
# Author:  Duncan Runnacles
# Version:  1.1
# 
# Summary:
#    Created the initial log_pages dictionary that is used by the application
#    to update the GUI and the database.
#    Uses the tmac_tools_lib package to read the ief and tuflow files and
#    retrieve all the necessary data from the files. This data is then used to
#    populate the different pages of the log. The log is split into pages 
#    according to the required outputs (Run, Tgc, Tbc, Dat, BC DBase).
#
# UPDATES:
#    DR - 19/11/2014
#        Added ability to log ISIS only runs.
#
# TODO:
#    Currently no support for .ecf files and therefore no support for
#    BC DBase files either. Can't do anything about this until the 
#    tmac_tools_lib implements this capability.
#
###############################################################################
'''

# Import python standard modules
import os
import datetime
from operator import attrgetter

import logging
logger = logging.getLogger(__name__)

# Import tmac_tools_lib modules
try:
    from tmac_tools_lib.utils.fileloaders.TuflowLoader import TuflowLoader
    from tmac_tools_lib.utils.fileloaders.IefLoader import IefLoader
    from tmac_tools_lib.utils import UniversalUtilityFunctions as ufunc
    from tmac_tools_lib.tuflow.MainTuflowModelFiles import Tcf, Tgc, Tbc
    from tmac_tools_lib.tuflow.tuflowfileparts.SomeFile import SomeFile
    from tmac_tools_lib.utils import FileTools
except:
    logger.error('Cannot load tmac_tools_lib: Is it installed?')

TYPE_TUFLOW = 0
TYPE_ISIS = 1
TYPE_ESTRY = 2

def loadModel(file_path, log_type):
    '''Load the model at the given file path.
    The path given can be for either an .ief file or a .tcf file. It will use
    the tmac_tools_lib to load the model file references and collect them into
    dictionaries for the different pages of the log file.
    
    @param file_path: the path to either an .ief or .tcf file.
    @param log_type: the type of model to load (tuflow/isis only/estry only)
    @return: dictionary containing dictionaries of log data retrieved from the
             model files.
    '''
    # Check that the path actually exists before we start.
    if not os.path.exists(file_path):
        return False
    
    # Find out which type of model is being loaded.
    # TODO:
    #    Loading .ecf files is not currently supported.
    logger.info('loading model at filepath: ' + file_path)
    file_type = None
    if ufunc.checkFileType(file_path, ext=['.ief', '.IEF']):
        file_type = 'ief'
        
    elif ufunc.checkFileType(file_path, ext=['.tcf', '.TCF']):
        file_type = 'tcf'
        
    elif ufunc.checkFileType(file_path, ext=['.ecf', '.ECF']):
        file_type = 'ecf'
        logger.error('File: ' + file_path + '\n.ecf files are not currently supported')
        
    else:
        logger.error('File: ' + file_path + '\nis not ief or tcf format')
        return False

    tuflow_model = None
    ief_file = None
    tcf_path = None
    
    # If we have an .ief file; load it first.
    if file_type == 'ief' and not log_type == TYPE_ESTRY:
        loader = IefLoader()
        ief_file = loader.loadIefFile(file_path)
        
        if ief_file == False:
            logger.error('Unable to load Isis .ief file at: ' + file_path)
            return False
        
        # Get the ief filepaths (this returns a tuple of main paths, ied paths 
        # and snapshot paths, but we only want the main ones)
        ief_paths = ief_file.getFilePaths()[0]
        tcf_path = ief_paths['twodfile']
        
        # If the path that the ief uses to reach the tcf file doesn't exist it
        # means that the ief paths havn't been updated on the local machine, so
        # we return False and log the error.
        if log_type == TYPE_TUFLOW:
            if tcf_path == False or not os.path.exists(tcf_path):
                logger.error('Tcf file referenced by ief does not exist at: ' +
                              str(tcf_path))
                return False
        
    # Then load the tuflow model if we are looking for one.
    if log_type == TYPE_TUFLOW:
        # If there's no Tuflow model we return false because this is a tuflow model
        # log and without one carrying on is pointless.
        loader = TuflowLoader()
        if tcf_path == None and file_type == 'tcf':
            
            tuflow_model = loader.loadTuflowModel(file_path)
        
        elif not tcf_path == None and ufunc.checkFileType(tcf_path, ext=['.tcf', '.TCF']):
            try:
                tuflow_model = loader.loadTuflowModel(tcf_path)
            except IOError:
                logger.error('Unable to load Tuflow .tcf file at: ' + tcf_path)
                return False
        else:
            return False
    
    # Get the current date
    date_now = datetime.datetime.now()
    cur_date = date_now.strftime('%d/%m/%Y')
    
    # Load the data needed for the log into the log pages dictionary.
    log_pages = {}
    log_pages['RUN'] = buildRunRowFromModel(cur_date, ief_file, tuflow_model, log_type)
    
    if log_type == TYPE_ISIS:
        log_pages['TGC'] = None
        log_pages['TBC'] = None
        log_pages['BC_DBASE'] = None
    else:
        log_pages['TGC'] = buildTgcRowFromModel(cur_date, tuflow_model)
        log_pages['TBC'] = buildTbcRowFromModel(cur_date, tuflow_model)
        log_pages['BC_DBASE'] = None

    if log_type == TYPE_ESTRY:
        log_pages['DAT'] = None
    else:
        log_pages['DAT'] = buildDatRowFromModel(cur_date, log_pages['RUN'])
    
    return log_pages


def buildRunRowFromModel(cur_date, ief_file, tuflow_model, log_type):
    '''Creates the row for the 'run' model log entry based on the contents
    of the loaded ief file and tuflow model.
    
    TODO:
        At the moment the event duration is only found if there is an .ief file.
        This is because the tmac_tools_lib doesn't currently try and find the
        event duration from the .tcf file. When it does this will be supported.
    
    @param ief_file: the Ief object loaded from file.
    @param tuflow_model: the TuflowModel object loaded from file.
    @param log_type: the type of run being logged. I.e. Tulfow run/isis only
           run/estry only run.
    '''
    run_cols = {'DATE': str(cur_date), 'MODELLER': 'None', 
                'RESULTS_LOCATION_2D': 'None', 'RESULTS_LOCATION_1D': 'None', 
                'EVENT_DURATION': 'None', 'DESCRIPTION': 'None', 
                'COMMENTS': 'None', 'SETUP': 'None', 'ISIS_BUILD': 'None', 
                'IEF': 'None', 'DAT': 'None', 'TUFLOW_BUILD': 'None', 
                'TCF': 'None', 'TGC': 'None', 'TBC': 'None', 'BC_DBASE': 'None', 
                'EVENT_NAME': 'None'}
    
    if not log_type == TYPE_ESTRY and not ief_file == None:
        run_cols = buildIsisRun(ief_file, run_cols)
    
    if log_type == TYPE_TUFLOW:
        run_cols = buildTuflowRun(ief_file, tuflow_model, run_cols)
        
    return run_cols


def buildIsisRun(ief_file, run_cols):
    '''Get all of the required log data from the ief file.
    
    @param ief_file: the Ief object.
    @param run_cols: the log data dictionary to fill.
    @return: the updated log_files dictionary.
    '''    
    ief_paths = ief_file.getFilePaths()[0]
    run_cols['IEF'] = ief_file.path_holder.getFileNameAndExtension()
    run_cols['DAT'] = FileTools.getFileName(ief_paths['datafile'], True)
    run_cols['RESULTS_LOCATION_1D'] = ief_paths['results']
    
    if ief_file.event_details.has_key('Finish'):    
        start = ief_file.event_details['Start']
        end = ief_file.event_details['Finish']
        run_cols['EVENT_DURATION'] = str(float(end) - float(start))
    else:
        run_cols['EVENT_DURATION'] = 'None'
    
    return run_cols

def buildEstryRun():
    '''Build the necessaries for an Estry only run.
    '''
    raise NotImplementedError
        

def buildTuflowRun(has_ief_file, tuflow_model, run_cols):
    '''Get all of the required log data for a tuflow run.
    
    @param has_ief_file: True is log entry has an ief file.
    @param tuflow_model: the TuflowModel object.
    @param run_cols: the log data dictionary to fill.
    @return: the updated log_files dictionary.
    '''    
    # Fetch the main tcf file and the list of .trd files referenced by it.
    tcf = tuflow_model.getModelObject('main_tcf')
    tcf_trds = tuflow_model.getModelObject(Tcf.TYPE)

    if not has_ief_file:
        # If we don't have an ief we should try and get the run duration 
        # variables from the tcf files instead
        # Go through the list of tcf's and associated trd files to get all
        # references to start and end times.
        tcf_list = tcf_trds
        tcf_list.append(tcf)
        tcf_start_times = []
        tcf_end_times = []
        for t in tcf_list:
            variables = t.getModelValues(Tcf.VARIABLES)
            for v in variables:
                if v.command == 'Start Time':
                    tcf_start_times.append(v)
                if v.command == 'End Time':
                    tcf_end_times.append(v)
                    
        # If we found any references
        if len(tcf_start_times) > 0 and len(tcf_end_times) > 0:
            # Use the the global_order variable of all TuflowFilePart objects to find
            # which duration setting lines are called last and use it to set the log
            # output location.
            start = end = None
            last_read_start = max(tcf_start_times, key=attrgetter('global_order'))
            start = last_read_start.raw_var
            last_read_end = max(tcf_end_times, key=attrgetter('global_order'))
            end = last_read_end.raw_var
                    
            if not (start == None or end == None):
                try:
                    run_cols['EVENT_DURATION'] = str(float(end) - float(start))
                except:
                    pass
        
    # The rest is in the tuflow model
    run_cols['TCF'] = tcf.somefileRef.getFileNameAndExtension()
    
    # Get the tgc and tbc file details.
    tgc_paths = []
    tbc_paths = []
    tgcs = tuflow_model.getModelObject(Tgc.TYPE)
    tbcs = tuflow_model.getModelObject(Tbc.TYPE)
    
    # Add all .tgc file and .tbc file paths to a list and join them up into a
    # single string
    for g in tgcs:
        tgc_paths.append(g.somefileRef.getFileNameAndExtension())
    for b in tbcs:
        tbc_paths.append(b.somefileRef.getFileNameAndExtension())
    run_cols['TGC'] = "[" + ", ".join(tgc_paths) + "]"
    run_cols['TBC'] = "[" + ", ".join(tbc_paths) + "]"
    
    # Go through the list of tcf's and associated trd files to get all
    # references to results file locations.
    tcf_list = tcf_trds
    tcf_list.append(tcf)
    tcf_results = []
    for t in tcf_list:
        results_files = t.getModelValues(Tcf.RESULTS_FILES)
        for r in results_files:
            if r.command == 'Output Folder':
                tcf_results.append(r)
                
    # Use the global_order variable same as for the duration calls
    last_read_r = max(tcf_results, key=attrgetter('global_order'))
    run_cols['RESULTS_LOCATION_2D'] = last_read_r.path_as_read
    
    return run_cols
                
                
def buildTgcRowFromModel(cur_date, tuflow_model):
    '''Create a new row for the TGC file page
    @var tulfow_model: The TuflowModel object loaded from file
    @attention: See superclass for more details 
    '''
    tgc_cols = {'DATE': str(cur_date), 'TGC': 'None', 'FILES': 'None', 
                'COMMENTS': 'None'}
    tgc_list = []
    cur_date = str(cur_date)
    tgc_files = []
    tgc_path = 'None'
    
    # If there are any .tgc files in the TuflowModel; grab them all and join up
    # the filenames (as done in the run page) and append files to the list if
    # they aren't already in it.
    tgcs = tuflow_model.getModelObject(Tgc.TYPE)
    if len(tgcs) > 0:

        for g in tgcs:
            tgc_path = g.somefileRef.getFileNameAndExtension()
            paths = g.getFilePaths(SomeFile.NAME_AND_EXTENSION)
            for p in paths:
                if not p in tgc_files:
                    tgc_files.append(p)

            tgc_list.append({'DATE': cur_date, 'TGC': tgc_path, 
                             'FILES': tgc_files, 'COMMENTS': 'None'})

    else:
        tgc_list.append(tgc_cols) 
            
    return tgc_list


def buildTbcRowFromModel(cur_date, tuflow_model):
    '''Create a new row for the TGC file page
    @var tulfow_model: The TuflowModel object loaded from file
    @attention: See superclass for more details 
    '''
    tbc_cols = {'DATE': str(cur_date), 'TBC': 'None', 'FILES': 'None', 
                'COMMENTS': 'None'}
    tbc_list = []
    cur_date = str(cur_date)
    tbc_files = []
    tbc_path = 'None'
    
    # If there are any .tgc files in the TuflowModel; grab them all and join up
    # the filenames (as done in the run page) and append files to the list if
    # they aren't already in it.
    tbcs = tuflow_model.getModelObject(Tbc.TYPE)
    if len(tbcs) > 0:

        for g in tbcs:
            tbc_path = g.somefileRef.getFileNameAndExtension()
            paths = g.getFilePaths(SomeFile.NAME_AND_EXTENSION)
            for p in paths:
                if not p in tbc_files:
                    tbc_files.append(p)

            tbc_list.append({'DATE': cur_date, 'TBC': tbc_path, 
                             'FILES': tbc_files, 'COMMENTS': 'None'})

    else:
        tbc_list.append(tbc_cols) 
            
    return tbc_list

    
def buildDatRowFromModel(cur_date, run_page):
    '''Create a new row for the DAT file page
    @var ief: The IEF model file
    @attention: See superclass for more details 
    '''
    dat_cols = {'DATE': str(cur_date), 'DAT': 'None', 'AMENDMENTS': 'None', 
                'COMMENTS': 'None'}

    dat_cols['DAT'] = run_page['DAT']
    
    return dat_cols
        
        
def buildBcRowFromModel(cur_date):
    raise NotImplementedError("Boundary conditions page has not been implemented yet")
