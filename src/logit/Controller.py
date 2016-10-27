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


 Module:          Controller.py 
 Date:            16/11/2014
 Author:          Duncan Runnacles
 Since-Version:   0.1
 
 Summary:
    Controller functions for the GUI. Code that is not directly responsible 
    for updating or retrieving from the GUI is included in this module in
    order to separate it from the application library.

 UPDATES:
    DR - 03/12/15):
        Moved lots of the MainGui code into functions in here
        during extensive refactoring in that class.
    DR - 13/12/2015:
        Big refactor. Cleared up lots of functions, combined and removed a few
        as well. 
        Added a BdQueue class to store all database calls when creating new
        model entries until end so that they are all added at once. This really
        speeds up the process.
        Added the AddedRows class for storing the entries made to the DB. 
        The functions in this module are now A LOT easier to follow and 
        quite a few bugs have been removed. This is a big improvement.
    DR - 14/12/2015:
        Fixed bug in fetchAndCheckModel to do with if-else logic when a file
        was already found in the database.
        Added checks to deleteAssociatedEntries to ensure entry was made in
        new enough version of the database.
    DR - 04/03/2016:
        Added extractModel function.
    DR - 28/04/2016:
        Moved most of the vopyLogsToClipboard code into here from MainGui.
    DR - 08/09/2016:
        Big code strip-out and rework of whole module for transition to the
        new peewee database setup.
        There was a lot of code in here for interacting with the database
        module (which has now been removed). All of which is now much simpler
        and in the peeweemodels module instead.

 TODO:
    

###############################################################################
"""
import os
import traceback
import itertools
import cPickle
import shutil
import zipfile
from operator import itemgetter

from PyQt4 import QtCore, QtGui

import logging
logger = logging.getLogger(__name__)

from ship.utils.qtclasses import MyFileDialogs
from ship.utils import utilfunctions as uf

# Local modules
import LogBuilder
# logger.debug('Import LogBuilder complete')
import Exporters
# logger.debug('Import Exporters complete')
from app_metrics import utils as applog
logger.debug('Import app_metrics complete')
import globalsettings as gs

import peeweeviews as pv
import peeweemodels as pm
from peewee import *
from playhouse import shortcuts
from playhouse.dataset import DataSet


def reverse_enumerate(iterable):
    """Enumerate over an iterable in reverse order while retaining proper indexes
    """
    return itertools.izip(reversed(xrange(len(iterable))), reversed(iterable))


# class DbQueue(object):
#     """Queueing class for storing data to go into the database
#     """
#     
#     def __init__(self):
#         self.items = []
# 
#     def isEmpty(self):
#         """Returns True if list is empty
#         """
#         return self.items == []
# 
#     def enqueue(self, item):
#         """Add an item to the queue
#         """
#         self.items.insert(0,item)
# 
#     def dequeue(self):
#         """Pop an item from the front of the queue.
#         """
#         return self.items.pop()
# 
#     def size(self):
#         """Get the size of the queue
#         """
#         return len(self.items)
#  
 

def createQtTableItem(value, is_editable=False, drag_enabled=False, is_str=True):
    """Create a QTableWidgetItem and return
    TODO: Check if this can be dealt with meaningfully in the Table classes.
          Currently only used by the multiModelLoad path list.
    :param is_editable=False: Set editable flag.
    :return: QTableWidgetItem
    """
    if is_str:
        item = QtGui.QTableWidgetItem(str(value))
    else:
        item = QtGui.QTableWidgetItem(value)
     
    if is_editable:
        if drag_enabled:
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
        else:
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
    else:
        if drag_enabled:
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
        else:
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
         
    return item

    

def fetchAndCheckModel(open_path, run_options, errors):
    """Loads a model and makes a few conditional checks on it.
    Loads model from the given .tcf/.ief file and checks that the .ief, 
    .tcf and ISIS results don't already exist in the DB and then returns
    a success or fail status.
    
    :param db_path: path to the database on file.
    :param open_path: the .ief or .tcf file path.
    :return: tuple containing AllLogs (which could be the loaded log
             pages or False if the load failed and a dictionary containing
             the load status and messages for status bars and errors.
    """   
    def getMissingFiles(open_path, missing_files):
        """
        """
        # Check if it's because model files are missing
        message = ' at:\n%s' % (open_path)
        file_str = 'The following tuflow model files could not be loaded:\n' + '\n'.join(missing_files)
        message = ' at:\n%s\n\n%s' % (open_path, file_str)
        return message
        
    
    loader = LogBuilder.ModelLoader()
    all_logs = loader.loadModel(open_path, run_options)
    
    # Deal with any loading errors
    if all_logs == False:
        logger.warning('Unable to load file:\n%s\nDoes it exist?' % (open_path))
        
        if loader.missing_files:
            msg_add = getMissingFiles(open_path, loader.missing_files)
        else:
            msg_add = (':\n%s\nCould not find the following files:\n%s'  % (open_path, loader.error))

        # DEBUG
        errors.addError(errors.MODEL_LOAD, msg_add=msg_add, msgbox_error=True)
        return errors, all_logs
    
    else:
        # Check that this run doesn't already exist in the database
        if pv.runExists(all_logs.run_hash):
            logger.warning('Log entry already exists for :\n%s' % (all_logs.run_hash))
            errors.addError(errors.LOG_EXISTS, 
                                msg_add=(':\nRun name = %s\nfile = %s' % (all_logs.run_hash, open_path)),
                                                    msgbox_error=True)
            return errors, all_logs
        
        # Gets run status and MB info if run is already completed and includes tuflow
        all_logs.run['RUN_STATUS'] = 'Unknown'
        all_logs.run['MB'] = -9999.0
        if not all_logs.run['TCF'].strip() == '':
            outputs = getRunStatusInfo(all_logs.tcf_dir, all_logs.run['TCF'], all_logs.run['RUN_OPTIONS'])
            if outputs[0]:
                all_logs.run['RUN_STATUS'] = outputs[1]
                all_logs.run['MB'] = outputs[2]
    
        return errors, all_logs
 
    
def getRunStatusInfo(tcf_dir, tcf_name, run_options):
    """Get the status and MB of a simulation.
    
    Checks the tuflow _ TUFLOW Simulations.log file to see if the run has
    finished. If it has it records the exit status and the mass balance (MB)
    in the given all_logs RUN dicionary.
    
    If the run hasn't finished or there are any issues loading files etc it 
    will stop and return the all_logs in the same state as they were given.
    
    Args:
        all_logs(AllLogs): 
    
    Return:
        tuple(bool, str, str) - with the RUN dict RUN_STATUS and MB entries 
            updated. Or if there was a failure: (False, False, False) for a
            unfound path and (False, True, False) for an incomplete run.  
    """
    if not run_options.strip() == '':
        t = os.path.splitext(tcf_name)[0]
        tcf_name = str(resolveFilenameSEVals(t, run_options))
    
    sim_file = os.path.join(tcf_dir, '_ TUFLOW Simulations.log')
    if not os.path.exists(sim_file): return False, False, False
    
    tcf_line = None
    try:
        with open(sim_file, 'rb') as f:
            for line in f:
                
                if not 'Licence Change' in line and not 'Started' in line:
                    if tcf_name.upper() in line.upper():
                        tcf_line = line
        
    except IOError:
        logger.warning('Could not load _TUFLOW Simulations.log file')
        
    if tcf_line is None: return False, True, False
    
    status = 'None'
    mb = 'None'
    contents = tcf_line.split("  ") # Two spaces minimum
    for item in contents:
        if'Finished' in item or 'UNSTABLE' in item or 'INTERRUPTED' in item:
            item = item.strip()
            item = item.split(':')[0]
            status = item.strip()
        
        elif 'pCME5' in item:
            val = item.split('=')
            val = val[1].strip()
            mb = val.strip('%')
    
    return True, status, mb 

    
def loadSetup(settings_path, errors):
    """Load LogIT setup from file.
    """
    cur_settings = None
    if settings_path == False:
        return cur_settings, errors
    try:
        # Load the settings dictionary
        open_path = str(settings_path)
        cur_settings = cPickle.load(open(open_path, "rb"))
        cur_settings.cur_settings_path = settings_path
        return cur_settings, errors
    except:
        errors.addError(errors.SETTINGS_LOAD, msg_add='from:\n%s' % (open_path),
                                                            msgbox_error=True)
        logger.error('Could not load settings file')
        return cur_settings, errors
    

def checkVersionInfo(version, version_path):
    """Tests whether this is up to date with the version info on the server."""
    
    with open(version_path, 'rb') as f:
        lines = f.readlines()
        file_version = lines[0].strip()
        if not file_version == version:
            return False, file_version
        else:
            return (True,)
        

def downloadNewVersion(cur_location, server_dir, download_filename):
    """Downloads the latest version to the users current install directory.
    
    Copies the latest version from the server, unzips it to the directory
    immediately outside the current directory and copies over users current
    settings into the new version.
    
    Args:
        cur_location(str): the current location of the executable.
        download_filename(str): the name of the download file (without extension).
    
    Return:
        Bool - False if failed, True otherwise.
    """
    download_dir = os.path.join(cur_location, '..', download_filename)
    try:
        os.mkdir(download_dir)
    except:
        logger.error('Unable to create download directory')
        return False
    download_file = os.path.join(server_dir, download_filename + '.zip')

    # Download and unzip new version
    try:
        shutil.copy(download_file, download_dir)
    except IOError:
        logger.error('Unable to download new version')
        return False
        
    zip_file = os.path.join(download_dir, download_filename + '.zip')
    zip_ref = zipfile.ZipFile(zip_file, 'r')
    zip_ref.extractall(download_dir)
    zip_ref.close()
    try:
        os.remove(zip_file)
    except IOError:
        logger.warning('Unable to delete zip file')
    
    # Copy over the current user settings
    userfile_old = os.path.join(cur_location, 'settings.logset')
    userfile_new = download_dir 
    try:
        shutil.copy(userfile_old, userfile_new)
    except IOError:
        logger.error('Unable to copy user settings file\n from: %s \nto: %s' % (userfile_old, userfile_new))
    
    return True    


def extractModel(cur_settings_path, run_row, errors):
    """Check the details of model location.
    
    Checks that the ief and tcf locations extracted from the log database exist
    and works out which path should be sent to the model extractor form.
    """
    
    ief = run_row['IEF']
    tcf = run_row['TCF']#[1:-1].split(',')[0]
    ief_dir = run_row['IEF_DIR']
    tcf_dir = run_row['TCF_DIR']
    input_path = None
    tcf_path = None
    
    # Make sure that the main input files we need exist and suchlike before 
    # we go any further
    if ief == 'None' and tcf == 'None':
        logger.error('No ief or tcf file names available to extract from')
        errors.addError(errors.EXTRACT_MODEL, 
                msg_add='\nNo ief or tcf file names available to extract from', 
                msgbox_error=True)
        
    if not ief == 'None':
        input_path = os.path.join(ief_dir, ief)
        if not os.path.exists(input_path):
            logger.error('Ief file does not exist - Do you need to update model location?')
            errors.addError(errors.EXTRACT_MODEL, 
                    msg_add='\nIef file does not exist - Do you need to update model location?\n' + input_path,
                    msgbox_error=True)
            return errors, None

    if not tcf == 'None':
        tcf_path = os.path.join(tcf_dir, tcf)
        if input_path is None:
            input_path = tcf_path
        if not os.path.exists(tcf_path):
            logger.error('Tcf file does not exist - Do you need to update model location?')
            errors.addError(errors.EXTRACT_MODEL, 
                    msg_add='\nTcf file does not exist - Do you need to update model location?\n' + tcf_path,
                    msgbox_error=True)
            return errors, None
    
    return errors, input_path


def prepLogsForCopy(log_path):
    """
    """
    zip_log = os.path.join(log_path, '..', 'logs.zip')
        
    # Remove any existing zip file
    if os.path.exists(zip_log):
        try:
            os.remove(zip_log)
        except:
            logger.warning('Unable to delete existing log zip file')
    
    # Create a zipfile handler
    zipper = zipfile.ZipFile(zip_log, 'w', zipfile.ZIP_DEFLATED)
    
    # Grab all of the log files into it
    for roots, dir, files in os.walk(log_path):
        for f in files:
            write_path = os.path.join(log_path, f)
            zipper.write(write_path, os.path.basename(write_path))
    zipper.close()
    
    return zip_log
    

def resolveFilenameSEVals(filename, se_vals):
    """Replace a tuflow placeholder filename with the scenario/event values.
    
    Replaces all of the placholder values (e.g. ~s1~_~e1~) in a tuflow 
    filename with the corresponding values provided in the run options string.
    If the run options flags are not found in the filename their values will
    be appended to the end of the string.
    
    The setup of the returned filename is always the same:  
        - First replace all placeholders with corresponding flag values.
        - s1 == s and e1 == e.
        - Append additional e values to end with '_' before first and '+' before others.
        - Append additional s values to end with '_' before first and '+' before others.
    
    Args:
        filename(str): the filename to update.
        se_vals(str): the run options string containing the 's' and 'e' flags
            and their corresponding values.
    
    Return:
        str - the updated filename.
    """
    # Format the se_vals string to the scenario/event dict
    se_vals = uf.convertRunOptionsToSEDict(se_vals)
    
    # Resolve the filename
    filename = uf.getSEResolvedFilename(filename, se_vals)
    
    return filename
    
    
    
    
    

    