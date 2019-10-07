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
    DR - 08/09/2016:
        Updated when changing database backend to use peewee.
        buildTuflowRun() is now simplified as it no longer needs to gather the
        model files in to a string. These are now only collected in the TGC,
        TBC, etc MODEL entry.
        Most of the collation work that was done here is no longer performed 
        as it is done by the database during queries, which is possible now that
        it has been normalized better.
    DR - 29/11/2016:
        Updated to accomadate changes in the SHIP library (v0.3.0) which 
        rewrote large chunks of the tuflow package API and some fmp.

 TODO:

###############################################################################
"""

# Import python standard modules
import os
import datetime
from operator import attrgetter
from collections import defaultdict

import logging
logger = logging.getLogger(__name__)

# Import ship modules
try:
    from ship.utils.fileloaders.fileloader import FileLoader
    from ship.utils import utilfunctions as ufunc
    from ship.utils import filetools
    from ship.tuflow.datafiles import datafileloader
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
        self.tcf = ''
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

        run_filename = os.path.basename(file_path)
        
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
        except Exception as err:
            logger.error('Unable to load model file at:\n' + file_path)
            logger.exception(err)
            self.error = 'Unable to load model file at:\n' + file_path
            print (err)
            return False
        
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
                    self.tcf = os.path.basename(tcf_path)
                    self.tuflow = loader.loadFile(tcf_path, options) 
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
                
            self.tcf = os.path.basename(file_path)
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
        if self.log_type == TYPE_TUFLOW:
            log_pages = LogClasses.AllLogs(run_filename, self.tcf_dir, self.ief_dir)
        else:
            log_pages = LogClasses.AllLogs(run_filename, ief_dir=self.ief_dir)

        if self.run_options == {}: self.run_options = ''

        run, dat, ieds = self.buildRunRowFromModel()
        log_pages.addLogEntry(run)
        
        if self.log_type != TYPE_ISIS:
            se_vals = self.tuflow.user_variables.seValsToDict()
            for ckey, cval in self.tuflow.control_files.items():
                log_pages.addLogEntry(self.buildModelFileRow(cval, se_vals))
            log_pages.addLogEntry(self.buildBcRowFromModel(se_vals))
        
        if self.log_type != TYPE_ESTRY:
            log_pages.addLogEntry(self.buildDatRowFromModel(dat))
            log_pages.addLogEntry(ieds)
        
        return log_pages
    
    
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

        Note:
            Although only a single run entry is returned (because only one can
            exist for a particular run) it is returned in a list to maintain
            consistency with the other 'build' functions.
        
        Return:
            tuple(list, str) - (the 'RUN' data dictionary updated with the
                isis and tuflow run data, the .dat file path).
        """
        run_cols = {'TYPE': 'RUN', 'MODELLER': '', 
                    'TUFLOW_RESULTS': '', 'ISIS_RESULTS': '', 
                    'ESTRY_RESULTS': '', 'EVENT_DURATION': -9999.0,  
                    'COMMENTS': '', 'SETUP': '', 'ISIS_BUILD': '', 
                    'IEF': '', 'TCF': self.tcf, 'INITIAL_CONDITIONS': '', 
                    'TUFLOW_BUILD': 'None', 'EVENT_NAME': '', 'RUN_OPTIONS': '', 
                    'LOG_DIR': ''}
        
        dat = ''
        ieds = []
        if not self.log_type == TYPE_ESTRY and not self.ief is None:
            run_cols, options, dat, ieds = self.buildIsisRun(run_cols)
            run_cols['RUN_OPTIONS'] = self.run_options
        
        if self.log_type == TYPE_TUFLOW:
            run_cols = self.buildTuflowRun(run_cols)
            run_cols['RUN_OPTIONS'] = self.run_options
            
        return [run_cols], dat, ieds
    
    
    def buildIsisRun(self, run_cols):
        """Get all of the required log data from the ief file.
        
        :param ief_file: the Ief object.
        :param run_cols: the log data dictionary to fill.
        :return: the updated log_files dictionary.
        """    
        run_cols['IEF'] = self.ief.path_holder.filenameAndExtension()
        dat = filetools.getFileName(self.ief.getValue('Datafile'), True)
        run_cols['ISIS_RESULTS'] = self.ief.getValue('Results')
        
#         if self.ief.event_details.has_key('InitialConditions'):
        if 'InitialConditions' not in self.ief.event_details:
            run_cols['INITIAL_CONDITIONS'] = os.path.basename(self.ief.getValue('InitialConditions'))
        
#         if self.ief.event_details.has_key('Finish'):    
        if 'Finish' not in self.ief.event_details:
            start = self.ief.event_details['Start']
            end = self.ief.event_details['Finish']
            run_cols['EVENT_DURATION'] = str(float(end) - float(start))
            
        options = 'None'
        if self.run_options: options = self.run_options
        
        # Create the ied model files
        ieds = self.buildIedRowFromModel(self.ief.getIedData())
        
        return run_cols, options, dat, ieds
        
    
    def buildTuflowRun(self, run_cols):
        """Get all of the required log data for a tuflow run.
        
        Includes:  
            - EVENT_DURATION  
            - OUTPUT_FOLDER  
            - LOG_FOLDER  
            - LOG_DIR  
            - TUFLOW_RESULTS  
        
        Args:
            run_cols(dict): to update with data extracted here.
            
        Return:
            dict - updated run_cols dict.
        """
        tcf_control = self.tuflow.control_files['TCF']
        se_vals = self.tuflow.user_variables.seValsToDict()
        if self.ief is None:
            # If we don't have an ief we should try and get the run duration 
            # variables from the tcf files instead
            start = None
            end = None
            stime = tcf_control.contains(command='start time')
            etime = tcf_control.contains(command='end time')
            if stime and etime:
                start = stime[0].variable
                end = etime[0].variable
                try:
                    run_cols['EVENT_DURATION'] = str(float(end) - float(start))
                except: pass
            
        # Tuflow results
        result = ''
        result_tcf = tcf_control.contains(command='output folder')
        if result_tcf:
            if result_tcf[-1].has_own_root:
                result = result_tcf[-1].absolutePath()
            elif result_tcf[-1].relativePath():
                result = result_tcf[-1].relativePath()
        run_cols['TUFLOW_RESULTS'] = result

        # Estry results
        if 'ECF' in self.tuflow.control_files.keys():
            result = ''
            result_ecf = self.tuflow.control_files['ECF'].contains(command='output folder')
            if result_ecf:
                if result_ecf[-1].has_own_root:
                    result = result_ecf[-1].absolutePath()
                elif result_ecf[-1].relativePath():
                    result = result_ecf[-1].relativePath()
            run_cols['ESTRY_RESULTS'] = result
        
        # Log folder
        log = tcf_control.contains(command='log folder')
        if log:
            result = log[-1].absolutePath()
        run_cols['LOG_DIR'] = result
        
        return run_cols
                

    def buildModelFileRow(self, control_file, se_vals): 
        """Create a new row for the model file page.
        
        Args:
            model_files(list): the TuflowModelFile's to extract data from.
            mtype(str): the type of TuflowModelFile (e.g. 'TGC').
            se_vals(dict): scenario/event values for this run.
        
        Return:
            list - containing the model file data for this mtype.
        """
        out_list = []
        all_files = control_file.filepaths(by_parent=True)
        for key, files in all_files.items():
            mtype = os.path.splitext(key)[1][1:].upper()
            out_list.append({
                'TYPE': mtype, 'NAME': key, 
                'FILES': files, 'COMMENTS': 'None', 'EXISTS': False
            })
        return out_list
            

    def buildDatRowFromModel(self, dat):
        """Create a new row for the DAT file page
        
        Note:
            Although only a single dat entry is returned (because only one can
            exist for a particular run) it is returned in a list to maintain
            consistency with the other 'build' functions.
        
        Return:
            list - containing the single dat file entry.
        """
        dat_cols = {'TYPE': 'DAT', 'NAME': 'None', 'AMENDMENTS': 'None', 
                    'COMMENTS': 'None', 'EXISTS': False}

        dat_cols['NAME'] = dat
        
        return [dat_cols]
    
    
    def buildIedRowFromModel(self, ieds):
        """
        """
        out_list = []
        if len(ieds) > 0:
            for ied in ieds:
                out_list.append({'TYPE': 'IED', 'NAME': os.path.basename(ied['file']),
                                 'REF': ied['name'], 'AMENDMENTS': 'None',
                                 'COMMENTS': 'None', 'EXISTS': False})
            
        return out_list

        
    def buildBcRowFromModel(self, se_vals):
        """Create a new row for the BC Databas file page
        
        Return:
            list - containing the bc database entries.
        """
        bc_list = []
        
        # Get the BC Database objects from the model
        data = []
        data.extend(self.tuflow.control_files['TCF'].files(fpt.DATA, 
                                                         se_vals=se_vals))
        if 'ECF' in self.tuflow.control_files.keys():
            data.extend(self.tuflow.control_files['ECF'].files(fpt.DATA, 
                                                             se_vals=se_vals))
        bc = []
        bc_files = []
        for d in data:
            if d.command.upper() == 'BC DATABASE':
                if not d.filename in bc_files:
                    bc.append(d)
                    bc_files.append(d.filename)
        del bc_files
        
        if len(bc) > 0:
            for b in bc:
                bc_obj = datafileloader.loadDataFile(b)
                files = bc_obj.getAllPaths(include_this=False, name_only=True)
                bc_list.append({'TYPE': 'BC_DBASE', 'NAME': b.filenameAndExtension(), 
                                'FILES': files, 'COMMENTS': 'None', 'EXISTS': False})
        
        return bc_list



