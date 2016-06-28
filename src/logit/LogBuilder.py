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
    Uses the ship package to read the ief and tuflow files and
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
        Major re-write of module to use updated version of the ship.
    DR - 28/04/2016:
        Added LOG_DIR, RUN_STATUS and MB to RUN table variables. Also obtains
        the location of the log directory from the SHIP library. 

 TODO:

###############################################################################
"""

# Import python standard modules
import os
import datetime
from operator import attrgetter

import logging
logger = logging.getLogger(__name__)

# Import ship modules
try:
    from ship.utils.fileloaders.fileloader import FileLoader
    from ship.utils import utilfunctions as ufunc
    from ship.utils import filetools
    from ship.tuflow.data_files import datafileloader
    from ship.tuflow import FILEPART_TYPES as fpt
    
except:
    logger.error('Cannot load ship: Is it installed?')
    
import LogClasses

# Constants for identifying log type
TYPE_TUFLOW = 0
TYPE_ISIS = 1
TYPE_ESTRY = 2

missing_files = []


class ModelLoader(object):
    
    def __init__(self):
        self.log_type = -1
        self.file_type = None
        self.ief = None
        self.tuflow = None
        self.ief_dir = 'None'
        self.tcf_dir = 'None'
        self.run_options = {}
        self.error = None
        self.missing_files = []
        
        # Get the current date
        date_now = datetime.datetime.now()
        self.cur_date = date_now.strftime('%d/%m/%Y')
        
    
    def loadModel(self, file_path, run_options={}):
        """
        """
        self.run_options = run_options
        options = ''
        
        # Check that the path actually exists before we start.
        if not os.path.exists(file_path):
            self.error = 'File does not exist'
            return False
        
        logger.info('loading model at filepath: ' + file_path)
        if ufunc.checkFileType(file_path, ext=['.ief', '.IEF']):
            self.file_type = 'ief'
            self.log_type = TYPE_ISIS
            
        elif ufunc.checkFileType(file_path, ext=['.tcf', '.TCF']):
            self.file_type = 'tcf'
            self.log_type = TYPE_TUFLOW
            
        elif ufunc.checkFileType(file_path, ext=['.ecf', '.ECF']):
            logger.error('File: ' + file_path + '\n.ecf files are not currently supported')
            self.error = 'Cannot currently load an ecf file as the main file'
            return False 
            
        else:
            logger.error('File: ' + file_path + '\nis not ief or tcf format')
            self.error = 'Not a recognised .ief or .tcf file'
            return False 
        
        if self.run_options:
            options = self.createSEVals(self.run_options)
        else:
            options = {}

        loader = FileLoader()
        try:
            model_file = loader.loadFile(file_path, options)
        except Exception, err:
            logger.error('Unable to load model file at:\n' + file_path)
            logger.exception(err)
            self.error = 'Unable to load model file at:\n' + file_path
            print str(err)
            return False
        
#         if loader.warnings:
#             logger.error('Model loaded with warnings at: ' + file_path)
#             logger.error('Warnings:\n' + str(loader.warnings))
#             self.error('Model loaded with warnings at: ' + file_path)
#             return False

        # If we have an .ief file; load it first.
        if self.log_type == TYPE_ISIS:
            
            self.ief = model_file
            self.ief_dir = str(os.path.split(file_path)[0])
            
            # Get the tcf and the 2D Scheme details
            tcf_path = self.ief.getValue('2DFile')
            scheme = self.ief.getValue('2DScheme')
            
            # Get the 2D run options from the isis ief form
            # These take precedence over any handed in by the user
            self.run_options = self.ief.getValue('2DOptions')
            if not self.run_options is None: 
                options = self.createSEVals(self.run_options)
            else:
                self.run_options = {}
                options = {}
            
            # If the path that the ief uses to reach the tcf file doesn't exist it
            # means that the ief paths haven't been updated on the local machine, so
            # we return False and log the error.
            if scheme == 'TUFLOW' and tcf_path is not None: 
                self.log_type = TYPE_TUFLOW
                if tcf_path == False or not os.path.exists(tcf_path):
                    logger.error('Tcf file referenced by ief does not exist at\n:' +
                                  str(tcf_path))
                    self.missing_files.append(tcf_path)
                    self.error = 'Tcf file does not exist at: ' + str(tcf_path)
                    return False

                elif not ufunc.checkFileType(tcf_path, ext=['.tcf', '.TCF']):
                    logger.error('2D file referenced in ief is not a tuflow file:\n' +
                                  str(tcf_path))
                    self.missing_files.append(tcf_path)
                    self.error = '2D file referenced by the ief is not a .tcf file: ' + str(tcf_path)
                    return False

                try:
                    self.tuflow = loader.loadFile(tcf_path, options) # self.run_options)
                    self.tcf_dir = os.path.split(tcf_path)[0]
                    self.missing_files = self.tuflow.missing_model_files
                    if self.missing_files:
                        self.error = 'Some key model files could not be found during load'
                        return False
                    
                except IOError:
                    logger.error('Unable to load Tuflow .tcf file at: ' + tcf_path)
                    self.missing_files.append(tcf_path)
                    self.error = 'Tcf file does not exist at: ' + str(tcf_path)
                    return False
                
                if loader.warnings:
                    logger.error('Model loaded with warnings at: ' + file_path)
                    logger.error('Warnings:\n' + str(loader.warnings))
                    return False
            
        # Then load the tuflow model if we are looking for one.
        if self.log_type == TYPE_TUFLOW and not self.file_type == 'ief':
            
            if not ufunc.checkFileType(file_path, ext=['.tcf', '.TCF']):
                    logger.error('File path is not a TUFLOW tcf file:\n' +
                                  str(file_path))
                    self.missing_files.append(tcf_path)
                    self.error = 'Tcf file does not exist at: ' + str(tcf_path)
                    return False
                
            self.tuflow = model_file
            self.tcf_dir = os.path.split(file_path)[0]
            self.missing_files = self.tuflow.missing_model_files
            if self.missing_files:
                self.error = 'Some key model files could not be found during load'
                return False
            
            if loader.warnings:
                logger.error('Model loaded with warnings at: ' + file_path)
                logger.error('Warnings:\n' + str(loader.warnings))
                return False

        # Load the data needed for the log into the log pages dictionary.
        log_pages = {}
        log_pages['RUN'] = self.buildRunRowFromModel()
        
        if self.log_type == TYPE_ISIS:
            log_pages['TGC'] = [None]
            log_pages['TBC'] = [None]
            log_pages['ECF'] = [None]
            log_pages['TCF'] = [None]
            log_pages['TEF'] = [None]
            log_pages['TRD'] = [None]
            log_pages['BC_DBASE'] = [None]
        else:
            se_vals = self.tuflow.getCurrentSEVals()
            tmfs = self.tuflow.getTuflowModelFiles(se_only=True, no_duplicates=True)
            log_pages['ECF'] = self.buildModelFileRow(tmfs['ecf'], 'ecf', se_vals)
            log_pages['TCF'] = self.buildModelFileRow(tmfs['tcf'], 'tcf', se_vals)
            log_pages['TGC'] = self.buildModelFileRow(tmfs['tgc'], 'tgc', se_vals)
            log_pages['TBC'] = self.buildModelFileRow(tmfs['tbc'], 'tbc', se_vals)
            log_pages['TEF'] = self.buildModelFileRow(tmfs['tef'], 'tef', se_vals)
            log_pages['TRD'] = self.buildModelFileRow(tmfs['trd'], 'trd', se_vals)
            log_pages['BC_DBASE'] = self.buildBcRowFromModel()

        if self.log_type == TYPE_ESTRY:
            log_pages['DAT'] = None
        else:
            log_pages['DAT'] = self.buildDatRowFromModel(log_pages['RUN'])
        

        # Record location of tuflow tcf file if included
        if self.log_type == TYPE_TUFLOW:
            all_logs = LogClasses.AllLogs(log_pages, self.tcf_dir, self.ief_dir)
        else:
            all_logs = LogClasses.AllLogs(log_pages, ief_dir=self.ief_dir)
            
        return all_logs
    
    
    def createSEVals(self, options):
        """
        """
        outvals = {'scenario': {}, 'event': {}}
        vals = options.split(" ")
        for i in range(len(vals)):
            if vals[i].startswith('-s'):
                outvals['scenario'][vals[i]] = vals[i+1]
            elif vals[i].startswith('-e'):
                outvals['event'][vals[i]] = vals[i+1]
        
        return outvals
    
    
    def buildRunRowFromModel(self):
        """Creates the row for the 'run' model log entry based on the contents
        of the loaded ief file and tuflow model.
        
        :param ief_file: the Ief object loaded from file.
        :param tuflow_model: the TuflowModel object loaded from file.
        :param log_type: the type of run being logged. I.e. Tulfow run/isis only
               run/estry only run.
        """
        run_cols = {'DATE': str(self.cur_date), 'MODELLER': 'None', 
                    'RESULTS_LOCATION_2D': 'None', 'RESULTS_LOCATION_1D': 'None', 
                    'EVENT_DURATION': 'None', 'DESCRIPTION': 'None', 
                    'COMMENTS': 'None', 'SETUP': 'None', 'ISIS_BUILD': 'None', 
                    'IEF': 'None', 'DAT': 'None', 'TUFLOW_BUILD': 'None', 
                    'TCF': 'None', 'TGC': 'None', 'TBC': 'None', 'BC_DBASE': 'None', 
                    'ECF': 'None', 'TEF': 'None', 'TRD': 'None', 'EVENT_NAME': 'None', 
                    'RUN_OPTIONS': 'None', 'TCF_DIR': 'None', 'IEF_DIR': 'None', 
                    'LOG_DIR': 'None', 'MB': 'None', 'RUN_STATUS': 'None'}
        
        if not self.log_type == TYPE_ESTRY and not self.ief is None:
            run_cols, options = self.buildIsisRun(run_cols)
            run_cols['RUN_OPTIONS'] = self.run_options
            run_cols['IEF_DIR'] = self.ief_dir
        
        if self.log_type == TYPE_TUFLOW:
            run_cols = self.buildTuflowRun(run_cols)
            run_cols['TCF_DIR'] = self.tcf_dir
            
        return run_cols
    
    
    def buildIsisRun(self, run_cols):
        """Get all of the required log data from the ief file.
        
        :param ief_file: the Ief object.
        :param run_cols: the log data dictionary to fill.
        :return: the updated log_files dictionary.
        """    
        run_cols['IEF'] = self.ief.path_holder.getFileNameAndExtension()
        run_cols['DAT'] = filetools.getFileName(self.ief.getValue('Datafile'), True)
        run_cols['RESULTS_LOCATION_1D'] = self.ief.getValue('Results')
        
        if self.ief.event_details.has_key('Finish'):    
            start = self.ief.event_details['Start']
            end = self.ief.event_details['Finish']
            run_cols['EVENT_DURATION'] = str(float(end) - float(start))
        else:
            run_cols['EVENT_DURATION'] = 'None'
            
#         options = 'None'
#         if self.ief.event_details.has_key('2DOptions'):
#             options = self.ief.event_details['2DOptions']
        options = 'None'
        if self.run_options: options = self.run_options
        
        return run_cols, options
        
    
    def buildTuflowRun(self, run_cols):
        """Get all of the required log data for a tuflow run.
        
        :param has_ief_file: True is log entry has an ief file.
        :param tuflow_model: the TuflowModel object.
        :param run_cols: the log data dictionary to fill.
        :return: the updated log_files dictionary.
        """
        # Fetch all of the tuflow control files that are within the current
        # scenario and event setups.
        modelfiles = self.tuflow.getModelFiles(se_only=True, no_duplicates=True)
         
        # Fetch the main tcf file and the list of .trd files referenced by it.
        tcf_paths = []
        for t in modelfiles['tcf']:
            tcf_paths.append(t.getFileNameAndExtension())
        run_cols['TCF'] = "[" + ", ".join(tcf_paths) + "]"

        if self.ief is None:
            # If we don't have an ief we should try and get the run duration 
            # variables from the tcf files instead
            start = None
            end = None
            variables = self.tuflow.getVariables(se_only=True, no_duplicates=True)
            
            # We get them in order so any later references will overwrite the
            # previous versions
            for v in variables:
                if v.command.upper() == 'START TIME':
                    start = v.raw_var
                if v.command.upper() == 'END TIME':
                    end = v.raw_var
                        
            if not (start == None or end == None):
                try:
                    run_cols['EVENT_DURATION'] = str(float(end) - float(start))
                except:
                    pass
        
        # Get the tgc and tbc file details.
        tgc_paths = [m.getFileNameAndExtension() for m in modelfiles['tgc']]
        tbc_paths = [m.getFileNameAndExtension() for m in modelfiles['tbc']]
        ecf_paths = [m.getFileNameAndExtension() for m in modelfiles['ecf']]
        tef_paths = [m.getFileNameAndExtension() for m in modelfiles['tef']]
        trd_paths = [m.getFileNameAndExtension() for m in modelfiles['trd']]

        if not len(tgc_paths) < 1:
            run_cols['TGC'] = "[" + ", ".join(tgc_paths) + "]"
        if not len(tbc_paths) < 1:
            run_cols['TBC'] = "[" + ", ".join(tbc_paths) + "]"
        if not len(ecf_paths) < 1:
            run_cols['ECF'] = "[" + ", ".join(ecf_paths) + "]"
        if not len(tef_paths) < 1:
            run_cols['TEF'] = "[" + ", ".join(tef_paths) + "]"
        if not len(trd_paths) < 1:
            run_cols['TRD'] = "[" + ", ".join(trd_paths) + "]"

        # Get the BC Database file references
        data = self.tuflow.getFiles(fpt.DATA, no_duplicates=True, se_only=True)
        bc_paths = []
        for d in data:
            if d.command.upper() == 'BC DATABASE':
                bc_paths.append(d.getFileNameAndExtension())
        
        # Get them into a single string
        if not len(bc_paths) < 1:
            run_cols['BC_DBASE'] = "[" + ", ".join(bc_paths) + "]"
        
        # Get the results and check for the result output command
        result_obj = None
        log_obj = None
        in_results = self.tuflow.getFiles(fpt.RESULT, se_only=True, no_duplicates=True)
        for r in in_results:
            if r.command.upper() == 'OUTPUT FOLDER' and r.modelfile_type.upper() == 'TCF':
                result_obj = r
            elif r.command.upper() == 'LOG FOLDER':
                log_obj = r

        # Use the global_order variable same as for the duration calls
        result = ''
        main_tcf = self.tuflow.mainfile.getFileNameAndExtension()
        main_tcf = os.path.splitext(main_tcf)[0]
        result = ''
        if not result_obj is None:
            if result_obj.has_own_root:
                result = result_obj.root
            elif not result_obj.getRelativePath():
                result = ''
            else:
                result = result_obj.getRelativePath()
        run_cols['RESULTS_LOCATION_2D'] = result
        
        log = ''
        if not log_obj is None:
            if log_obj.has_own_root:
                log = log_obj.root
            elif not log_obj.getRelativePath():
                log = self.tcf_dir
            else:
                log = os.path.join(self.tcf_dir, log_obj.getRelativePath())
        run_cols['LOG_DIR'] = log

        return run_cols
                

    def buildModelFileRow(self, model_files, mtype, se_vals):
        """Create a new row for the model file page.
        @var tulfow_model: The TuflowModel object loaded from file
        """
        cur_date = str(self.cur_date)
        cols = {'DATE': cur_date, mtype.upper(): 'None', 'FILES': 'None', 
                    'COMMENTS': 'None'}

        out_list = []
        if len(model_files) > 0:
            for m in model_files:
                files = m[0].getFileNames(with_extension=True, include_results=False,
                                         se_vals=se_vals)
                out_list.append({'DATE': cur_date, 
                                 mtype.upper(): m[1],
                                 'FILES': files, 'COMMENTS': 'None'})
        else:
            out_list.append(cols) 
            
        return out_list
    

    def buildDatRowFromModel(self, run_page):
        """Create a new row for the DAT file page
        @var run_page: the run page details.
        @attention: See superclass for more details 
        """
        dat_cols = {'DATE': str(self.cur_date), 'DAT': 'None', 'AMENDMENTS': 'None', 
                    'COMMENTS': 'None'}

        dat_cols['DAT'] = run_page['DAT']
        
        return dat_cols
        
        
    def buildBcRowFromModel(self):
        """Create a new row for the BC Databas file page
        :return: Dictionary containing the data needed for the page.
        """
        cur_date = str(self.cur_date)
        bc_cols = {'DATE': cur_date, 'BC_DBASE': 'None', 'FILES': 'None', 
                    'COMMENTS': 'None'}
        bc_list = []
        
        # Get the BC Database objects from the model
        data = self.tuflow.getFiles(fpt.DATA, no_duplicates=True, se_only=True)
        bc = []
        for d in data:
            if d.command.upper() == 'BC DATABASE':
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


        

