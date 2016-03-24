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


 Module:          LogBuilder.py
 Date:            16/11/2014
 Author:          Duncan Runnacles
 Since-Version:   0.1
 
 Summary:
    Created the initial log_pages dictionary that is used by the application
    to update the GUI and the database.
    Uses the tmactools package to read the ief and tuflow files and
    retrieve all the necessary data from the files. This data is then used to
    populate the different pages of the log. The log is split into pages 
    according to the required outputs (Run, Tgc, Tbc, Dat, BC DBase).

 UPDATES:
    DR - 19/11/2014:
        Added ability to log ISIS only runs.
    DR - 03/12/2015:
        Added functionality for loading ECF and BC_DBASE files from the model.
    DR - 13/12/2015:
        Now returns logs as an AllLogs object rather than as a dictionary.
    DR - 29/02/2016:
        Major re-write of module to use updated version of the tmactools.

 TODO:

###############################################################################
"""

# Import python standard modules
import os
import datetime
from operator import attrgetter

import logging
logger = logging.getLogger(__name__)

# Import tmactools modules
try:
    from tmactools.utils.fileloaders.fileloader import FileLoader
    from tmactools.utils import utilfunctions as ufunc
    from tmactools.utils import filetools
    from tmactools.tuflow.data_files import datafileloader
    
except:
    logger.error('Cannot load tmactools: Is it installed?')
    
import LogClasses

# Constants for identifying log type
TYPE_TUFLOW = 0
TYPE_ISIS = 1
TYPE_ESTRY = 2

missing_files = []

def loadModel(file_path, log_type):
    """Load the model at the given file path.
    The path given can be for either an .ief file or a .tcf file. It will use
    the tmactools to load the model file references and collect them into
    dictionaries for the different pages of the log file.
    
    :param file_path: the path to either an .ief or .tcf file.
    :param log_type: the type of model to load (tuflow/isis only/estry only)
    :return: dictionary containing dictionaries of log data retrieved from the
             model files.
    """
    missing_files = []
    
    # Check that the path actually exists before we start.
    if not os.path.exists(file_path):
        return False, 'File does not exist'
    
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
        return False, 'Not a recognised .ief or .tcf file'

    tuflow = None
    ief = None
    tcf_path = None
    ief_dir = 'None'
    tcf_dir = 'None'
    
    loader = FileLoader()
    model_file = loader.loadFile(file_path)
    if model_file == False:
        logger.error('Unable to load model file at:\n' + file_path)
        return False, 'Unable to load model file'

    # If we have an .ief file; load it first.
    if file_type == 'ief' and not log_type == TYPE_ESTRY:
        
        ief = model_file
        ief_dir = os.path.split(file_path)[0]
        
        # Get the ief filepaths (this returns a tuple of main paths, ied paths 
        # and snapshot paths, but we only want the main ones)
        ief_paths = ief.getFilePaths()[0]
        tcf_path = ief_paths['twodfile']
        
        # If the path that the ief uses to reach the tcf file doesn't exist it
        # means that the ief paths haven't been updated on the local machine, so
        # we return False and log the error.
        if log_type == TYPE_TUFLOW:
            if tcf_path == False or not os.path.exists(tcf_path):
                logger.error('Tcf file referenced by ief does not exist at\n:' +
                              str(tcf_path))
                missing_files.append(tcf_path)
                return False, 'Tcf file does not exist at: ' + str(tcf_path)

            elif not ufunc.checkFileType(tcf_path, ext=['.tcf', '.TCF']):
                logger.error('2D file referenced in ief is not a tuflow file:\n' +
                              str(tcf_path))
                missing_files.append(tcf_path)
                return False, '2D file referenced by the ief is not a .tcf file: ' + str(tcf_path)

            try:
                tuflow = loader.loadFile(tcf_path)
                tcf_dir = os.path.split(tcf_path)[0]
                missing_files = tuflow.missing_model_files
                if missing_files:
                    return False, '\n'.join(missing_files)
                
            except IOError:
                missing_files.append(tcf_path)
                logger.error('Unable to load Tuflow .tcf file at: ' + tcf_path)
                return False, '\n'.join(missing_files)
        
    # Then load the tuflow model if we are looking for one.
    if log_type == TYPE_TUFLOW and not file_type == 'ief':
        
        if not ufunc.checkFileType(file_path, ext=['.tcf', '.TCF']):
                logger.error('File path is not a TUFLOW tcf file:\n' +
                              str(file_path))
                missing_files.append(tcf_path)
                return False, '\n'.join(missing_files)
            
        tuflow = model_file
        tcf_dir = os.path.split(file_path)[0]
        missing_files = tuflow.missing_model_files
        if missing_files:
            return False, '\n'.join(missing_files)

    # Get the current date
    date_now = datetime.datetime.now()
    cur_date = date_now.strftime('%d/%m/%Y')
    
    # Load the data needed for the log into the log pages dictionary.
    log_pages = {}
    log_pages['RUN'] = buildRunRowFromModel(cur_date, ief, tuflow, log_type, 
                                            tcf_dir, ief_dir)
    
    if log_type == TYPE_ISIS:
        log_pages['TGC'] = None
        log_pages['TBC'] = None
        log_pages['ECF'] = None
        log_pages['TCF'] = None
        log_pages['BC_DBASE'] = None
    else:
        log_pages['ECF'] = buildModelFileRow(cur_date, tuflow, 'ecf')
        log_pages['TCF'] = buildModelFileRow(cur_date, tuflow, 'tcf')
        log_pages['TGC'] = buildModelFileRow(cur_date, tuflow, 'tgc')
        log_pages['TBC'] = buildModelFileRow(cur_date, tuflow, 'tbc')
        log_pages['BC_DBASE'] = buildBcRowFromModel(cur_date, tuflow)

    if log_type == TYPE_ESTRY:
        log_pages['DAT'] = None
    else:
        log_pages['DAT'] = buildDatRowFromModel(cur_date, log_pages['RUN'])
    

    # Record location of tuflow tcf file if included
    if log_type == TYPE_TUFLOW:
        all_logs = LogClasses.AllLogs(log_pages, tcf_dir, ief_dir)
    else:
        all_logs = LogClasses.AllLogs(log_pages)
        
    return all_logs, ''


def buildRunRowFromModel(cur_date, ief, tuflow, log_type, tcf_dir, ief_dir):
    """Creates the row for the 'run' model log entry based on the contents
    of the loaded ief file and tuflow model.
    
    TODO:
        At the moment the event duration is only found if there is an .ief file.
        This is because the tmactools doesn't currently try and find the
        event duration from the .tcf file. When it does this will be supported.
    
    :param ief_file: the Ief object loaded from file.
    :param tuflow_model: the TuflowModel object loaded from file.
    :param log_type: the type of run being logged. I.e. Tulfow run/isis only
           run/estry only run.
    """
    run_cols = {'DATE': str(cur_date), 'MODELLER': 'None', 
                'RESULTS_LOCATION_2D': 'None', 'RESULTS_LOCATION_1D': 'None', 
                'EVENT_DURATION': 'None', 'DESCRIPTION': 'None', 
                'COMMENTS': 'None', 'SETUP': 'None', 'ISIS_BUILD': 'None', 
                'IEF': 'None', 'DAT': 'None', 'TUFLOW_BUILD': 'None', 
                'TCF': 'None', 'TGC': 'None', 'TBC': 'None', 'BC_DBASE': 'None', 
                'ECF': 'None', 'EVENT_NAME': 'None', 'RUN_OPTIONS': 'None',
                'TCF_DIR': 'None', 'IEF_DIR': 'None'}
    
    if not log_type == TYPE_ESTRY and not ief == None:
        run_cols, options = buildIsisRun(ief, run_cols)
        run_cols['RUN_OPTIONS'] = options
        run_cols['IEF_DIR'] = ief_dir
    
    if log_type == TYPE_TUFLOW:
        run_cols = buildTuflowRun(ief, tuflow, run_cols)
        run_cols['TCF_DIR'] = tcf_dir
        
    return run_cols


def buildIsisRun(ief_file, run_cols):
    """Get all of the required log data from the ief file.
    
    :param ief_file: the Ief object.
    :param run_cols: the log data dictionary to fill.
    :return: the updated log_files dictionary.
    """    
    ief_paths = ief_file.getFilePaths()[0]
    run_cols['IEF'] = ief_file.path_holder.getFileNameAndExtension()
    run_cols['DAT'] = filetools.getFileName(ief_paths['datafile'], True)
    run_cols['RESULTS_LOCATION_1D'] = ief_paths['results']
    
    if ief_file.event_details.has_key('Finish'):    
        start = ief_file.event_details['Start']
        end = ief_file.event_details['Finish']
        run_cols['EVENT_DURATION'] = str(float(end) - float(start))
    else:
        run_cols['EVENT_DURATION'] = 'None'
        
    options = None
    if ief_file.event_details.has_key('2DOptions'):
        options = ief_file.event_details['2DOptions']
    
    return run_cols, options


def buildEstryRun():
    """Build the necessaries for an Estry only run.
    """
    raise NotImplementedError
        

def buildTuflowRun(has_ief_file, tuflow, run_cols):
    """Get all of the required log data for a tuflow run.
    
    :param has_ief_file: True is log entry has an ief file.
    :param tuflow_model: the TuflowModel object.
    :param run_cols: the log data dictionary to fill.
    :return: the updated log_files dictionary.
    """    
    # Fetch the main tcf file and the list of .trd files referenced by it.
    tcf_paths = tuflow.getModelFiles('tcf', name_only=True, with_extension=True)

    run_cols['TCF'] = "[" + ", ".join(tcf_paths) + "]"

    if not has_ief_file:
        # If we don't have an ief we should try and get the run duration 
        # variables from the tcf files instead
        start = None
        end = None
        variables = tuflow.getContents(tuflow.VARIABLE, in_order=True)
        
        # We get them in order so any later references will overwrite the
        # previous versions
        for v in variables:
            if v.command == 'Start Time':
                start = v.raw_var
            if v.command == 'End Time':
                end = v.raw_var
                    
        if not (start == None or end == None):
            try:
                run_cols['EVENT_DURATION'] = str(float(end) - float(start))
            except:
                pass
        
    
    # Get the tgc and tbc file details.
    tgc_paths = tuflow.getModelFiles('tgc', name_only=True, with_extension=True)
    tbc_paths = tuflow.getModelFiles('tbc', name_only=True, with_extension=True)
    ecf_paths = tuflow.getModelFiles('ecf', name_only=True, with_extension=True)

    if not len(tgc_paths) < 1:
        run_cols['TGC'] = "[" + ", ".join(tgc_paths) + "]"
    if not len(tbc_paths) < 1:
        run_cols['TBC'] = "[" + ", ".join(tbc_paths) + "]"
    if not len(ecf_paths) < 1:
        run_cols['ECF'] = "[" + ", ".join(ecf_paths) + "]"

    # Get the BC Database file references
    data = tuflow.getContents(tuflow.DATA)
    bc_paths = []
    for d in data:
        if d.command == 'BC Database':
            bc_paths.append(d.getFileNameAndExtension())
    
    # Get them into a single string
    if not len(bc_paths) < 1:
        run_cols['BC_DBASE'] = "[" + ", ".join(bc_paths) + "]"
    
    # Get the results and check for the result output command
    result = []
    in_results = tuflow.getContents(tuflow.RESULT)
    for r in in_results:
        if r.command == 'Output Folder':
            result.append(r)

    # Use the global_order variable same as for the duration calls
    result = max(result, key=attrgetter('global_order'))
    if result.file_name == '':
        if result.has_own_root:
            if result.file_name == '':
                result = os.path.join(result.root, tcf_paths[0])
            else:
                result = os.path.join(result.root, result.file_name)
        elif not result.getRelativePath() :
            result = tcf_paths[0]
        else:
            result = os.path.join(result.getRelativePath(), tcf_paths[0])
    run_cols['RESULTS_LOCATION_2D'] = result
        
    return run_cols
                

def buildModelFileRow(cur_date, tuflow, model_file):
    """Create a new row for the model file page.
    @var tulfow_model: The TuflowModel object loaded from file
    """
    cols = {'DATE': str(cur_date), model_file.upper(): 'None', 'FILES': 'None', 
                'COMMENTS': 'None'}
    out_list = []
    cur_date = str(cur_date)

    names = tuflow.getModelFiles(model_type=model_file.lower(), name_only=True, with_extension=True)
    if len(names) > 0:
        for n in names:
            files = tuflow.getFilesFromModelFile(model_file.lower(), model_filename=n, with_extension=True)
            
            # Get rid of any emtpty strings
            files = [x for x in files if x]
            
            out_list.append({'DATE': cur_date, model_file.upper(): n, 
                             'FILES': files, 'COMMENTS': 'None'})
    else:
        out_list.append(cols) 
        
    return out_list
    

def buildDatRowFromModel(cur_date, run_page):
    """Create a new row for the DAT file page
    @var cur_date: todays date.
    @var run_page: the run page details.
    @attention: See superclass for more details 
    """
    dat_cols = {'DATE': str(cur_date), 'DAT': 'None', 'AMENDMENTS': 'None', 
                'COMMENTS': 'None'}

    dat_cols['DAT'] = run_page['DAT']
    
    return dat_cols
        
        
def buildBcRowFromModel(cur_date, tuflow):
    """Create a new row for the BC Databas file page
    @var cur_date: todays date.
    @var tuflow_model: the TuflowModel object loaded from file.
    @attention: See superclass for more details.
    :return: Dictionary containing the data needed for the page.
    """
    bc_cols = {'DATE': str(cur_date), 'BC_DBASE': 'None', 'FILES': 'None', 
                'COMMENTS': 'None'}
    bc_list = []
    cur_date = str(cur_date)
    bc_files = []
    bc_path = 'None'
    
    # Get the BC Database objects from the model
    data = tuflow.getContents(tuflow.DATA, no_duplicates=True)
    bc = []
    for d in data:
        if d.command == 'BC Database':
            bc.append(d)
    
    if len(bc) > 0:
        
        for b in bc:
            bc_obj = datafileloader.loadDataFile(b)
            files = bc_obj.getAllPaths(include_this=False, name_only=True)
            bc_list.append({'DATE': cur_date, 'BC_DBASE': b.getFileNameAndExtension(), 
                            'FILES': files, 'COMMENTS': 'None'})
    
    else:
        bc_list.append(bc_cols) 
            
    return bc_list
    
    
    
    
    
    
    
    
    
